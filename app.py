from flask import Flask, request, jsonify
from math import *
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
Swagger(app)

# for working on same ports
CORS(app)


@app.route('/2d', methods=['POST'])
def index2d():
    """
       This is the index API.
       ---
       parameters:
         - name: sensitivity
           in: formData
           type: number
           required: true
         - name: power
           in: formData
           type: number
           required: true
         - name: plume_form
           in: formData
           type: text
           required: true
         - name: angleWidth
           in: formData
           type: number
           required: true
         - name: angleHeight
           in: formData
           type: number
           required: true
         - name: distance
           in: formData
           type: number
           required: true
         - name: spotWidth
           in: formData
           type: number
           required: true
         - name: spotHeight
           in: formData
           type: number
           required: true
       responses:
         200:
           description: Max distance calculation result.
    """

    data = request.get_json()
    print(data)
    sensitivity = float(data['sensitivity'])
    power = float(data['power'])
    max_area = calculate_max_area(sensitivity, power)

    plume_form = data['plumeForm']

    if 'angleWidth' and 'angleHeight' in data:
        angle_width = radians(float(data['angleWidth']))
        angle_height = radians(float(data['angleHeight']))

        max_distance = calculate_max_distance(max_area, angle_width, angle_height, plume_form)

    elif 'spotWidth' and 'spotHeight' in data:
        distance = float(data['distance'])
        plume_width = float(data['spotWidth'])
        plume_height = float(data['spotHeight'])
        angle_width = (calculate_divergence_angle(plume_width, distance))
        angle_height = (calculate_divergence_angle(plume_height, distance))

        max_distance = calculate_max_distance(max_area, angle_width, angle_height, plume_form)

    # module 2
    min_plume_size = float(data['minPlumeSize'])
    if min_plume_size != 0:
        min_distance = calculate_distance(min_plume_size, min(angle_width, angle_height))
    else:
        min_distance = 0

    # module 3
    distance_module3 = float(data['distanceModuleThird'])
    if distance_module3 != 0:
        plume_width_module3 = calculate_size(angle_width, distance_module3)
        plume_height_module3 = calculate_size(angle_height, distance_module3)
    else:
        plume_width_module3 = 0
        plume_height_module3 = 0

    return jsonify({
        'angle_width': round(degrees(angle_width), 2),
        'angle_height': round(degrees(angle_height), 2),
        'max_distance': round(max_distance, 2),

        # module 2
        'min_distance': round(min_distance, 2),

        # module 3
        'plume_width_module3': round(plume_width_module3, 2),
        'plume_height_module3': round(plume_height_module3, 2),

        # plume
        'plumeForm': plume_form

    })


@app.route('/3d', methods=['POST'])
def index3d():
    data = request.get_json()
    print(data)
    sensitivity = float(data['sensitivity'])
    power = float(data['power'])
    max_area = calculate_max_area(sensitivity, power)

    plume_form = data['plumeForm']

    if 'angleWidth' and 'angleHeight' in data:
        angle_width = radians(float(data['angleWidth']))
        angle_height = radians(float(data['angleHeight']))

        max_distance = calculate_max_distance(max_area, angle_width, angle_height, plume_form)

    elif 'spotWidth' and 'spotHeight' in data:
        distance = float(data['distance'])
        plume_width = float(data['spotWidth'])
        plume_height = float(data['spotHeight'])
        angle_width = (calculate_divergence_angle(plume_width, distance))
        angle_height = (calculate_divergence_angle(plume_height, distance))

        max_distance = calculate_max_distance(max_area, angle_width, angle_height, plume_form)

    # module 2
    min_plume_size = float(data['minPlumeSize'])
    if min_plume_size != 0:
        min_distance = calculate_distance(min_plume_size, min(angle_width, angle_height))
    else:
        min_distance = 0

    # module 3
    distance_module3 = float(data['distanceModuleThird'])
    if distance_module3 != 0:
        plume_width_module3 = calculate_size(angle_width, distance_module3)
        plume_height_module3 = calculate_size(angle_height, distance_module3)
    else:
        plume_width_module3 = calculate_size(angle_width, max_distance)
        plume_height_module3 = calculate_size(angle_height, max_distance)

    if 'angleWidth' and 'angleHeight' in data:
        return jsonify({
            'max_distance': round(max_distance, 2),

            # module 2
            'min_distance': round(min_distance, 2),

            # module 3
            'plume_width': round(plume_width_module3, 2),
            'plume_height': round(plume_height_module3, 2)

        })
    elif 'spotWidth' and 'spotHeight' in data:
        return jsonify({
            'angle_width': round(degrees(angle_width), 2),
            'angle_height': round(degrees(angle_height), 2),
            'max_distance': round(max_distance, 2),

            # module 2
            'min_distance': round(min_distance, 2),

            # module 3
            'plume_width_module3': round(plume_width_module3, 2),
            'plume_height_module3': round(plume_height_module3, 2)

        })
    else:
        return jsonify({
            'bad_request': 'mistake in filling fields'
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


def calculate_max_distance(max_area, angle_width, angle_height, plume_form):
    """
    calculate max guaranteed distance of data transfer
    :param max_area: value calculated in calculate_max_area()
    :param angle_width: value of width angle
    :param angle_height: value of height angle
    :type max_area: float
    :type angle_width: float
    :type angle_height: float
    :type plume_form: float
    :return: returns a value of max distance
    :rtype: float
    """
    max_angle = max(angle_width, angle_height)
    min_angle = min(angle_width, angle_height)
    coefficient = min_angle / max_angle

    if plume_form == 'rectangle':
        form_coefficient = pi/4
        print(f'spotWidth rectangle {coefficient}')
    elif plume_form == 'ellipse':
        form_coefficient = 1
        print(f'spotWidth ellipse {coefficient}')

    max_distance = sqrt(((max_area / (2 * pi * (1 - cos(max_angle / 2)))) / coefficient) * form_coefficient)
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
