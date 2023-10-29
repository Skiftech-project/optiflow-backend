from flask import Flask, render_template, request, jsonify, g
from math import *
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
Swagger(app)
# for working on same ports
CORS(app)
# Создайте контекст приложения
with app.app_context():
    g.angle_width = None
    g.angle_height = None
    g.max_area = None
    g.max_distance = None

# module 1 and 4 (API)
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        distance = float(data['distance'])
        sensitivity = float(data['sensitivity'])
        power = float(data['power'])
        max_area = calculate_max_area(sensitivity, power)

        if 'angleWidth' and 'angleHeight' in data:
            angle_width = radians(float(data['angleWidth']))
            angle_height = radians(float(data['angleHeight']))
            max_distance = calculate_max_distance(max_area, angle_width, angle_height)
        elif 'spotWidth' and 'spotHeight' in data:
            plume_width = float(data['spotWidth'])
            plume_height = float(data['spotHeight'])

            angle_width = (calculate_divergence_angle(plume_width, distance))
            angle_height = (calculate_divergence_angle(plume_height, distance))

        # Устанавливайте значения внутри контекста приложения
        with app.app_context():
            g.angle_width = angle_width
            g.angle_height = angle_height
            g.max_area = max_area
            g.max_distance = max_distance

        return jsonify({
            'angle_width': angle_width,
            'angle_height': angle_height,
            'max_area': max_area,
            'max_distance': max_distance,
            "test": 200
        })
    elif request.method == 'GET':
        # Возвращать предварительно рассчитанные значения при GET запросе
        return jsonify({
            'angle_width': g.angle_width,
            'angle_height': g.angle_height,
            'max_area': g.max_area,
            'max_distance': g.max_distance
        })


# API for module 2
@app.route('/module_2', methods=['POST'])
def module_2():
    data = request.get_json()
    min_plume_size = float(data['min_plume_size'])
    angle_width = radians(float(data['angle_width']))
    angle_height = radians(float(data['angle_height']))

    min_distance = calculate_distance(min_plume_size, min(angle_width, angle_height))

    return jsonify({
        'angle_width': angle_width,
        'angle_height': angle_height,
        'min_plume_size': min_plume_size,
        'min_distance': min_distance
    })


# API for module 3
@app.route('/module_3', methods=['POST'])
def module_3():
    data = request.get_json()
    angle_width = radians(float(data['angle_width']))
    angle_height = radians(float(data['angle_height']))
    distance = float(data['distance'])

    plume_width = calculate_size(angle_width, distance)
    plume_height = calculate_size(angle_height, distance)

    return jsonify({
        'angle_width': angle_width,
        'angle_height': angle_height,
        'distance': distance,
        'plume_width': plume_width,
        'plume_height': plume_height,
    })


def calculate_divergence_angle(size, distance):
    angle = 2 * atan(size / (2 * distance))
    return angle


def calculate_max_area(sensitivity, power):
    max_area = power / sensitivity
    return max_area


def calculate_max_distance(max_area, angle_width, angle_height):
    max_angle = max(angle_width, angle_height)
    min_angle = min(angle_width, angle_height)
    coefficient = min_angle / max_angle
    max_distance = sqrt((max_area / (2 * pi * (1 - cos(max_angle / 2)))) / coefficient)
    return max_distance


def calculate_size(angle, distance):
    size = 2 * distance * tan(angle / 2)
    return size


def calculate_distance(size, angle):
    distance = size / (2 * tan(angle / 2))
    return distance


if __name__ == '__main__':
    app.run(debug=True)
