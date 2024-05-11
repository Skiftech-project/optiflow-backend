import datetime
import os
import smtplib
from email.mime.text import MIMEText

from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                current_user, decode_token, get_jwt,
                                get_jwt_identity, jwt_required)
from marshmallow import ValidationError

from models import TokenBlockList, User
from schemas import UserSchema, UserUpdateSchema, validate_password

auth_bp = Blueprint('auth', __name__)
schema = UserSchema()
update_schema = UserUpdateSchema()


def create_access_and_refresh_tokens(user):
    access_token = create_access_token(identity=user.email, additional_claims={
                                       "username": user.username})
    refresh_token = create_refresh_token(identity=user.email, additional_claims={
                                         "username": user.username})
    return access_token, refresh_token


@auth_bp.post('/register')
@swag_from('docs/Auth/register.yml')
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

    access_token, refresh_token = create_access_and_refresh_tokens(new_user)

    # Получение декодированных данных токена, включая срок действия
    decoded_token = decode_token(access_token)
    # Время жизни access токена в секундах
    expires_in_seconds = decoded_token['exp'] - decoded_token['iat']

    return jsonify({
        "message": "User created and logged in successfully",
        "tokens": {
            "access_token": access_token,
            "access_token_expires_time (seconds)": expires_in_seconds,
            "refresh_token": refresh_token,
        }
    }), 201


@auth_bp.post('/login')
@swag_from('docs/Auth/login.yml')
def login_user():

    data = request.get_json()

    user = User.get_user_by_email(email=data.get('email'))

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    if not user.check_password(password=data.get('password')):
        return jsonify({'error': 'Invalid password'}), 400

    access_token, refresh_token = create_access_and_refresh_tokens(user)

    return jsonify({
        "message": "Logged in successfully",
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    }), 200


@auth_bp.get('/refresh')
@jwt_required(refresh=True)
@swag_from('docs/Auth/refresh.yml')
def refresh_access():
    user_email = get_jwt_identity()
    new_access_token = create_access_token(identity=user_email)
    return jsonify({"access_token": new_access_token})


def update_data(user, data):
    if 'username' in data:
        new_username = data.get("username")
        user.username = new_username

    if 'email' in data:
        new_email = data.get("email")
        user.email = new_email

    if 'password' in data:
        new_password = data.get("password")
        user.set_password(new_password)


@auth_bp.put('/updateProfile')
@jwt_required()
@swag_from('docs/Auth/update_profile.yml')
def update_user_profile():
    user_email = get_jwt_identity()
    user = User.get_user_by_email(user_email)

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    errors = update_schema.validate(data)

    if errors:
        return jsonify({'error': errors}), 400

    update_data(user, data)

    user.save()

    # Обновляем токены
    access_token, refresh_token = create_access_and_refresh_tokens(user)

    return jsonify({
        'message': 'User profile updated successfully',
        'tokens': {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 200


@auth_bp.get('/logout')
@jwt_required(verify_type=False)
@swag_from('docs/Auth/logout.yml')
def logout_user():
    identity = get_jwt_identity()
    user = User.get_user_by_email(email=identity)

    jwt = get_jwt()
    jti = jwt['jti']

    token_type = jwt['type']

    token_b = TokenBlockList(jti=jti)
    token_b.save(user_id=user.id)

    return jsonify({'message': f'{token_type} token revoked successfully'}), 200


@auth_bp.delete('/deleteAccount')
@jwt_required()
@swag_from('docs/Auth/delete_profile.yml')
def delete_account():
    user_email = get_jwt_identity()
    user = User.get_user_by_email(user_email)

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    user.delete()

    return jsonify({'message': f'User profile {user.username} deleted successfully'}), 200


@auth_bp.get('/whoami')
@jwt_required()
@swag_from('docs/Auth/whoami.yml')
def whoami():
    return jsonify({'message': " message", "user_details": {
        "username": current_user.username,
        "email": current_user.email,
    }}), 200


def send_email(user, restore_link):
    recipient_email = user.email
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')

    message = MIMEText(
        f'Для зміни пароля перейдіть за посиланням: {restore_link}')
    message['Subject'] = 'Password recovery'
    message['From'] = sender_email
    message['To'] = recipient_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False


@auth_bp.post('/sendResetEmail')
@swag_from('docs/Auth/send_reset_email.yml')
def send_restore_email():
    data = request.get_json()
    user = User.get_user_by_email(email=data.get('email'))

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    expires = datetime.timedelta(minutes=10)
    access_token = create_access_token(
        identity=user.email, expires_delta=expires)

    restore_link = f"http://localhost:5000/reset-password/{access_token}"
    # restore_link = f"{domen}:{port}/reset-password/{access_token}"

    if send_email(user, restore_link):
        return jsonify({'message': "Email sent successfully", "details": {
            "confirmation_link": restore_link,
            "email": user.email,
        }}), 200
    else:
        return jsonify({'error': "An error occurred while sending the email"}), 500


@auth_bp.put('/restorePassword')
@jwt_required()
@swag_from('docs/Auth/restore_password.yml')
def restore_password():
    data = request.get_json()
    user_email = get_jwt_identity()
    user = User.get_user_by_email(email=user_email)

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    new_password = data.get("password")
    try:
        validate_password(new_password)
        user.set_password(new_password)
        user.save()
    except ValidationError as e:
        errors = e.args[0]
        return jsonify({'error': errors}), 400

    return jsonify({'message': 'Password reset successfully'}), 200
