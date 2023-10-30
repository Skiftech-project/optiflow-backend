from flask import Flask, request, jsonify
from math import *
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
Swagger(app)

# for working on same ports
CORS(app)


# module 1 and 4 (API)
@app.route('/index', methods=['POST'])
def index():
    data = request.get_json()
    distance = float(data['distance'])
    sensitivity = float(data['sensitivity'])
    power = float(data['power'])
    max_area = calculate_max_area(sensitivity, power)

    if 'angleWidth' and 'angleHeight' in data:
        angle_width = radians(float(data['angleWidth']))
        angle_height = radians(float(data['angleHeight']))
        max_distance = calculate_max_distance(max_area, angle_width, angle_height)
        return jsonify({
            'max_area': max_area,
            'max_distance': max_distance,
        })

    elif 'spotWidth' and 'spotHeight' in data:
        plume_width = float(data['spotWidth'])
        plume_height = float(data['spotHeight'])
        angle_width = (calculate_divergence_angle(plume_width, distance))
        angle_height = (calculate_divergence_angle(plume_height, distance))
        max_distance = calculate_max_distance(max_area, angle_width, angle_height)
        return jsonify({
            'angle_width': degrees(angle_width),
            'angle_height': degrees(angle_height),
            'max_area': max_area,
            'max_distance': max_distance,
        })


# API for module 2
@app.route('/module_2', methods=['POST'])
def module_2():
    data = request.get_json()
    min_plume_size = float(data['min_plume_size'])
    angle_width = radians(float(data['angleWidth']))
    angle_height = radians(float(data['angleHeight']))

    min_distance = calculate_distance(min_plume_size, min(angle_width, angle_height))

    return jsonify({
        'min_distance': min_distance
    })


# API for module 3
@app.route('/module_3', methods=['POST'])
def module_3():
    data = request.get_json()
    angle_width = radians(float(data['angleWidth']))
    angle_height = radians(float(data['angleHeight']))
    distance = float(data['distance'])

    plume_width = calculate_size(angle_width, distance)
    plume_height = calculate_size(angle_height, distance)

    return jsonify({
        'plume_width': plume_width,
        'plume_height': plume_height,
    })


def calculate_divergence_angle(size, distance):
    """
    Calculates divergence angle
    :param size: size of plume
    :param distance: distance
    :type size: float
    :type distance: float
    :return: returns angle value
    :rtype: float
    """
    angle = 2 * atan(size / (2 * distance))
    return angle


def calculate_max_area(sensitivity, power):
    """
    Calculates max area of ellipse
    :param sensitivity: sensitivity of receiver
    :param power: power of receiver
    :type sensitivity: float
    :type power: float
    :return: returns a max area
    :rtype float
    """
    max_area = power / sensitivity
    return max_area


def calculate_max_distance(max_area, angle_width, angle_height):
    """
    calculate max guaranteed distance of data transfer
    :param max_area: value calculated in calculate_max_area()
    :param angle_width: value of width angle
    :param angle_height: value of height angle
    :type max_area: float
    :type angle_width: float
    :type angle_height: float
    :return: returns a value of max distance
    :rtype: float
    """
    max_angle = max(angle_width, angle_height)
    min_angle = min(angle_width, angle_height)
    coefficient = min_angle / max_angle
    max_distance = sqrt((max_area / (2 * pi * (1 - cos(max_angle / 2)))) / coefficient)
    return max_distance


def calculate_size(angle, distance):
    """
    Calculates the size of plume
    :param angle: value of angle
    :param distance: value of distance
    :type angle: float
    :type distance: float
    :return: returns a plume size
    :rtype: float
    """
    size = 2 * distance * tan(angle / 2)
    return size


def calculate_distance(size, angle):
    """
    Calculates the minimal effective distance
    :param size: size of the plume
    :param angle: angle value
    :type size: float
    :type angle: float
    :return: returns the value of the minimal effective distance
    :rtype: float
    """
    distance = size / (2 * tan(angle / 2))
    return distance


if __name__ == '__main__':
    app.run(debug=True)
