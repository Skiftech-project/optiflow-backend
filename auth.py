from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                current_user, get_jwt, get_jwt_identity,
                                jwt_required)

from models import TokenBlockList, User
from schemas import UserSchema

auth_bp = Blueprint('auth', __name__)

schema = UserSchema()


@auth_bp.post('/register')
@swag_from('docs/register.yml')
def register_user():

    data = request.get_json()

    errors = schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    user = User.get_user_by_email(email=data.get('email'))

    if user is not None:
        return jsonify({'error': 'User already exists'}), 409

    new_user = User(username=data.get('username'), email=data.get('email'))
    new_user.set_password(password=data.get('password'))
    new_user.save()

    access_token = create_access_token(identity=new_user.email, additional_claims={
                                       "username": new_user.username})
    refresh_token = create_refresh_token(identity=new_user.email, additional_claims={
                                         "username": new_user.username})
    return jsonify({
        "message": "User created and logged in successfully",
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    }), 201


@auth_bp.post('/login')
@swag_from('docs/login.yml')
def login_user():

    data = request.get_json()

    user = User.get_user_by_email(email=data.get('email'))

    if user and user.check_password(password=data.get('password')):

        access_token = create_access_token(identity=user.email, additional_claims={
                                           "username": user.username})
        refresh_token = create_refresh_token(identity=user.email, additional_claims={
                                             "username": user.username})
        return jsonify({
            "message": "Logged in successfully",
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

        }), 200

    return jsonify({'error': 'Invalid credentials'}), 400


@auth_bp.get('/whoami')
@jwt_required()
@swag_from('docs/whoami.yml')
def whoami():
    return jsonify({'message': " message", "user_details": {
        "username": current_user.username,
        "email": current_user.email,
    }}), 200


@auth_bp.get('/refresh')
@jwt_required(refresh=True)
@swag_from('docs/refresh.yml')
def refresh_access():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token})


@auth_bp.get('/logout')
@jwt_required(verify_type=False)
@swag_from('docs/logout.yml')
def logout_user():
    jwt = get_jwt()
    jti = jwt['jti']

    token_type = jwt['type']

    token_b = TokenBlockList(jti=jti)
    token_b.save()

    return jsonify({'message': f'{token_type} token revoked successfully'}), 200
