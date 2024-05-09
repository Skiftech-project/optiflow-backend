import os
from math import *

from dotenv import load_dotenv
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from flask_cors import CORS

from auth import auth_bp
from extensions import db, jwt, migrate
from models import TokenBlockList, User
from users import user_bp

# for local
# load_dotenv()
app = Flask(__name__)

template = {
    "swagger": "2.0",
    "info": {
        "title": "Optiflow API",
        "description": "API for Optiflow Project",
    },
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "JWT": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT authorization header using the Bearer scheme",
        }
    }
}

Swagger(app, template=template)

# for working on same ports
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'SQLALCHEMY_DATABASE_URI', 'sqlite:///database.db')
app.config['SQLALCHEMY_ECHO'] = bool(os.getenv('SQLALCHEMY_ECHO', 1))
app.config['FLASK_JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret')

# initialize extensions
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)

# register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')

# jwt error handlers


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'message': 'Request does not contain an access token.',
        'error': 'authorization_header'
    }), 401


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).one_or_none()


@jwt.additional_claims_loader
def make_additional_claims(identity):
    if identity == "user56":
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.token_in_blocklist_loader
def token_in_blocklist_callback(jwt_header, jwt_data):
    jti = jwt_data['jti']
    token = db.session.query(TokenBlockList).filter(
        TokenBlockList.jti == jti).scalar()

    return token is not None


@app.route('/2d', methods=['POST'])
@swag_from('docs/post2d.yml')
def index2d():

    data = request.get_json()
    print(data)
    sensitivity = float(data['sensitivity'])
    power = float(data['power'])
    max_area = calculate_max_area(sensitivity, power)

    plume_form = data['plumeForm']

    if 'angleWidth' and 'angleHeight' in data:
        angle_width = radians(float(data['angleWidth']))
        angle_height = radians(float(data['angleHeight']))

        max_distance = calculate_max_distance(
            max_area, angle_width, angle_height, plume_form)

    elif 'spotWidth' and 'spotHeight' in data:
        distance = float(data['distance'])
        plume_width = float(data['spotWidth'])
        plume_height = float(data['spotHeight'])
        angle_width = (calculate_divergence_angle(plume_width, distance))
        angle_height = (calculate_divergence_angle(plume_height, distance))

        max_distance = calculate_max_distance(
            max_area, angle_width, angle_height, plume_form)

    # module 2
    min_plume_size = float(data['minPlumeSize'])
    if min_plume_size != 0:
        min_distance = calculate_distance(
            min_plume_size, min(angle_width, angle_height))
    else:
        min_distance = 0

    # module 3
    distance_for_plume_size = float(data['distanceModuleThird'])
    if distance_for_plume_size != 0:
        plume_width_module3 = calculate_size(angle_width, distance_for_plume_size)
        plume_height_module3 = calculate_size(angle_height, distance_for_plume_size)
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
@swag_from('docs/post3d.yml')
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

        max_distance = calculate_max_distance(
            max_area, angle_width, angle_height, plume_form)

    elif 'spotWidth' and 'spotHeight' in data:
        distance = float(data['distance'])
        plume_width = float(data['spotWidth'])
        plume_height = float(data['spotHeight'])
        angle_width = (calculate_divergence_angle(plume_width, distance))
        angle_height = (calculate_divergence_angle(plume_height, distance))

        max_distance = calculate_max_distance(
            max_area, angle_width, angle_height, plume_form)

    # module 2
    min_plume_size = float(data['minPlumeSize'])
    if min_plume_size != 0:
        min_distance = calculate_distance(
            min_plume_size, min(angle_width, angle_height))
    else:
        min_distance = 0

    plume_width_3d = calculate_size(angle_width, max_distance)
    plume_height_3d = calculate_size(angle_height, max_distance)

    # module 3
    distance_for_plume_size = float(data['distanceModuleThird'])
    if distance_for_plume_size != 0:
        plume_width_module3 = calculate_size(angle_width, distance_for_plume_size)
        plume_height_module3 = calculate_size(angle_height, distance_for_plume_size)
    else:
        plume_width_module3 = 0
        plume_height_module3 = 0

    if 'angleWidth' and 'angleHeight' in data:
        return jsonify({
            'max_distance': round(max_distance, 2),

            # module 2
            'min_distance': round(min_distance, 2),

            'plume_width': round(plume_width_3d, 2),
            'plume_height': round(plume_height_3d, 2),

            # module 3
            'plume_width_cut': round(plume_width_module3, 2),
            'plume_height_cut': round(plume_height_module3, 2)

        })
    elif 'spotWidth' and 'spotHeight' in data:
        return jsonify({
            'angle_width': round(degrees(angle_width), 2),
            'angle_height': round(degrees(angle_height), 2),
            'max_distance': round(max_distance, 2),

            # module 2
            'min_distance': round(min_distance, 2),

            'plume_width': round(plume_width_3d, 2),
            'plume_height': round(plume_height_3d, 2),

            # module 3
            'plume_width_cut': round(plume_width_module3, 2),
            'plume_height_cut': round(plume_height_module3, 2)

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

    max_distance = sqrt(
        ((max_area / (2 * pi * (1 - cos(max_angle / 2)))) / coefficient) * form_coefficient)
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
    app.run(host='0.0.0.0', port=5000)
