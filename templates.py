from flasgger import swag_from
from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required

from models import CalculationTemplate, SavedCalculationTemplate, User
from flask_jwt_extended import get_jwt_identity

template_bp = Blueprint('template', __name__)


@template_bp.get('/getAllTemplates')
@swag_from('docs/Template/get_all_templates.yml')
def get_all_templates():
    all_templates = CalculationTemplate.get_all_templates()
    templates_data = []
    for template in all_templates:
        template_data = {
            "template_name": template.template_name,
            "sensitivity": template.sensitivity,
            "power": template.power,
            "plume_form": template.plume_form,
            "angle_width": template.angle_width,
            "angle_height": template.angle_height,
            "distance": template.distance,
            "spot_width": template.spot_width,
            "spot_height": template.spot_height,
            "min_plume_size": template.min_plume_size,
            "distance_for_plume_size": template.distance_for_plume_size
        }
        templates_data.append(template_data)

    return jsonify({"templates": templates_data}), 200


@template_bp.post('/initializeTemplates')
def initialize_templates():
    templates_data = [
        {"template_name": "template1", "sensitivity": 0.5, "power": 10.0, "plume_form": "ellipse",
         "angle_width": 45.0, "angle_height": 30.0, "distance": 100.0, "spot_width": 20.0,
         "spot_height": 15.0, "min_plume_size": 5.0, "distance_for_plume_size": 50.0},
        {"template_name": "template2", "sensitivity": 0.6, "power": 8.0, "plume_form": "rectangle",
         "angle_width": None, "angle_height": None, "distance": None, "spot_width": None,
         "spot_height": None, "min_plume_size": None, "distance_for_plume_size": None},
        {"template_name": "template3", "sensitivity": 15, "power": 2000.0, "plume_form": "ellipse",
         "angle_width": None, "angle_height": None, "distance": 15.0, "spot_width": 4.7,
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
    
    templates_data = []
    for template in user_templates:
        template_data = {
            "id": template.id,
            "user_id": template.user_id,
            "sensitivity": template.sensitivity,
            "power": template.power,
            "plume_form": template.plume_form,
            "angle_width": template.angle_width,
            "angle_height": template.angle_height,
            "distance": template.distance,
            "spot_width": template.spot_width,
            "spot_height": template.spot_height,
            "min_plume_size": template.min_plume_size,
            "distance_for_plume_size": template.distance_for_plume_size,
            "max_distance": template.max_distance,
            "min_distance": template.min_distance,
            "plume_width_module3": template.plume_width_module3,
            "plume_height_module3": template.plume_height_module3
        }
        templates_data.append(template_data)

    if not templates_data:
        return jsonify({'error': 'No saved templates found for this user'}), 404
    
    return jsonify({"templates": templates_data}), 200


@template_bp.post('/saveTemplate')
@jwt_required()
@swag_from('docs/Template/saveTemplate.yml')
def save_templates():
    data = request.get_json()
    
    user_email = get_jwt_identity()
    user = User.get_user_by_email(email=user_email)
    
    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404
    
    template = SavedCalculationTemplate(user_id=user.id, **data)
    template.save()

    return jsonify({"message": "Template saved successfully"}), 200