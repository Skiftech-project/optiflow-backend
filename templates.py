from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import CalculationTemplate, SavedCalculationTemplate, User
from schemas import CalculationTemplateSchema, SavedCalculationTemplateSchema
from sqlalchemy.inspection import inspect

template_bp = Blueprint('template', __name__)

calculation_template_schema = CalculationTemplateSchema()
saved_calculation_template_schema = SavedCalculationTemplateSchema()


@template_bp.get('/getAllTemplates')
@swag_from('docs/Template/get_all_templates.yml')
def get_all_templates():
    all_templates = CalculationTemplate.get_all_templates()
    templates_data = calculation_template_schema.dump(all_templates, many=True)
    return jsonify({"templates": templates_data}), 200


@template_bp.post('/initializeTemplates')
def initialize_templates():
    templates_data = [
        {"template_name": "template1", "sensitivity": 0.5, "power": 10.0, "plume_form": "ellipse",
         "angle_width": 45.0, "angle_height": 30.0, "distance": 100.0, "spot_width": 20.0,
         "spot_height": 15.0, "min_plume_size": 5.0, "distance_for_plume_size": 50.0},
        {"template_name": "template2", "sensitivity": 0.6, "power": 8.0, "plume_form": "rectangle",
         "angle_width": 14.3, "angle_height": 15.67, "distance": None, "spot_width": None,
         "spot_height": None, "min_plume_size": None, "distance_for_plume_size": None},
        {"template_name": "template3", "sensitivity": 15, "power": 2000.0, "plume_form": "ellipse",
         "angle_width": 3.45, "angle_height": 15.2, "distance": 15.0, "spot_width": 4.7,
         "spot_height": 8.2, "min_plume_size": None, "distance_for_plume_size": None},
    ]

    # Додавання об'єктів до сесії і збереження в базі даних
    for template_data in templates_data:
        template = CalculationTemplate(**template_data)
        template.save()

    return jsonify({"message": "Templates initialized successfully"}), 200


@template_bp.get('/getUserSavedTemplates')
@jwt_required()
@swag_from('docs/Template/get_saved_templates.yml')
def get_user_saved_templates():
    user_email = get_jwt_identity()
    user = User.get_user_by_email(email=user_email)
    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    user_templates = SavedCalculationTemplate.get_saved_templates(user.id)

    templates_data = saved_calculation_template_schema.dump(
        user_templates, many=True)

    if not templates_data:
        return jsonify({'error': 'No saved templates found for this user'}), 404

    return jsonify({"templates": templates_data}), 200


@template_bp.post('/saveTemplate')
@jwt_required()
@swag_from('docs/Template/saveTemplate.yml')
def save_templates():
    data = request.get_json()
    combined_data = {**data.get('input_data', {}), **data.get('output_data', {})}

    user_email = get_jwt_identity()
    user = User.get_user_by_email(email=user_email)

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    template = SavedCalculationTemplate(user_id=user.id, **combined_data)
    template.save()

    return jsonify({"message": "Template saved successfully"}), 200


@template_bp.delete('/deleteTemplate')
@jwt_required()
@swag_from('docs/Template/deleteTemplate.yml')
def delete_template():
    data = request.get_json()

    user_email = get_jwt_identity()
    user = User.get_user_by_email(email=user_email)

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    template = SavedCalculationTemplate.get_template_by_id(data.get('id'))

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    template.delete()

    return jsonify({"message": "Template deleted successfully"}), 200


@template_bp.put('/updateTemplate')
@jwt_required()
@swag_from('docs/Template/updateTemplate.yml')
def update_template():
    data = request.get_json()

    user_email = get_jwt_identity()
    user = User.get_user_by_email(email=user_email)

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    template = SavedCalculationTemplate.get_template_by_id(data.get('id'))

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    if 'id' in data:
        del data['id']
    if len(data) == 0:
        return jsonify({'error': 'No changes to update'}), 400

    for key, value in data.items():
        if hasattr(template, key):
            setattr(template, key, value)
        else:
            return jsonify({'error': f'Field {key} does not exist'}), 404

    template.save()
    return jsonify({"message": "Template updated successfully"}), 200
