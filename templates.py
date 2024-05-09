from flasgger import swag_from
from flask import Blueprint, jsonify, request

from models import CalculationTemplate

template_bp = Blueprint('template', __name__)


@template_bp.get('/getAllTemplates')
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


