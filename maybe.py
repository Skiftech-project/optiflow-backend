from flask import Flask, request, jsonify
from math import *
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
Swagger(app)

# for working on same ports
CORS(app)


@app.route('/index', methods=['POST'])
def index():
    data = request.get_json()
    sensitivity = float(data['sensitivity'])
    power = float(data['power'])
    max_area = calculate_max_area(sensitivity, power)

    if 'angleWidth' and 'angleHeight' in data:
        angle_width = radians(float(data['angleWidth']))
        angle_height = radians(float(data['angleHeight']))
        max_distance = calculate_max_distance(max_area, angle_width, angle_height)

    elif 'spotWidth' and 'spotHeight' in data:
        distance = float(data['distance'])
        plume_width = float(data['spotWidth'])
        plume_height = float(data['spotHeight'])
        angle_width = (calculate_divergence_angle(plume_width, distance))
        angle_height = (calculate_divergence_angle(plume_height, distance))
        max_distance = calculate_max_distance(max_area, angle_width, angle_height)

    # module 2
    min_plume_size = float(data['min_plume_size'])
    if min_plume_size != 0:
        min_distance = calculate_distance(min_plume_size, min(angle_width, angle_height))
    else:
        min_distance = 0

    # module 3
    distance_module3 = float(data['distance'])
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
        'plume_width': round(plume_width_module3, 2),
        'plume_height': round(plume_height_module3, 2)

    })


if __name__ == '__main__':
    app.run(debug=True)