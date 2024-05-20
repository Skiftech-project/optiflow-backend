import datetime
import os
import smtplib
from email.mime.text import MIMEText

from flasgger import swag_from
from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                current_user, decode_token, get_jwt,
                                get_jwt_identity, jwt_required)
from marshmallow import ValidationError

from models import TokenBlockList, User
from schemas import UserSchema, UserUpdateSchema, UserUpdatePasswordSchema, validate_password

auth_bp = Blueprint('auth', __name__)
schema = UserSchema()
update_schema = UserUpdateSchema()
update_password_schema = UserUpdatePasswordSchema()


def create_access_and_refresh_tokens(user):
    access_token = create_access_token(identity=user.email, additional_claims={
                                       "username": user.username}, expires_delta=datetime.timedelta(seconds=30))
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

    # Получение декодированных данных access токена, включая срок действия
    decoded_access_token = decode_token(access_token)
    access_token_expires_in_seconds = decoded_access_token['exp'] - decoded_access_token['iat']
    
    # Получение декодированных данных refresh токена, включая срок действия
    decoded_refresh_token = decode_token(refresh_token)
    refresh_token_expires_in_seconds = decoded_refresh_token['exp'] - decoded_refresh_token['iat']
    
    response = make_response(
        jsonify({
        "message": "User created and logged in successfully",
        "access_token": access_token,
        "access_token_expires_time (seconds)": access_token_expires_in_seconds,
        "refresh_token_expires_time (seconds)": refresh_token_expires_in_seconds,
    }), 201)
    
    response.set_cookie(
        'refreshToken',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='None',
        path="/"
    )
    
    return response


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

    response = make_response(jsonify({
        "message": "Logged in successfully",
        "access_token": access_token,
    }), 200)
    
    response.set_cookie(
        'refreshToken',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='None',
        path="/"
    )
    
    return response
    
    


@auth_bp.get('/refresh')
@swag_from('docs/Auth/refresh.yml')
def refresh_access():
    refresh_token = request.cookies.get('refreshToken')
    print(request.cookies)
    
    if not refresh_token:
        return jsonify({"error": "Refresh token is missing"}), 401
    
    try:
        decoded_refresh_token = decode_token(refresh_token)
        user_email = decoded_refresh_token['sub']
        
        user = User.get_user_by_email(email=user_email)
        new_access_token, new_refresh_token = create_access_and_refresh_tokens(user=user)
        
        response = make_response(
            jsonify({"access_token": new_access_token})
        )
        
        response.set_cookie(
            'refreshToken',
            new_refresh_token,
            httponly=True,
            secure=True,
            samesite='None',
            path="/"
        )
        return response
        
    except Exception as e:
        return jsonify({"error": "Invalid refresh token"}), 401
    

def update_data(user, data):
    if 'username' in data:
        new_username = data.get("username")
        user.username = new_username

    if 'email' in data:
        new_email = data.get("email")
        user.email = new_email


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
    
    
    new_email = data.get('email')
    if new_email and new_email != user_email:
        existing_user = User.get_user_by_email(new_email)
        if existing_user:
            return jsonify({'error': 'Email is already in use'}), 409

    update_data(user, data)

    user.save()

    # Обновляем токены
    access_token, refresh_token = create_access_and_refresh_tokens(user)
    
    response = make_response(jsonify({
        "message": "User profile updated successfully",
        "access_token": access_token,
    }), 200)
    
    response.set_cookie(
        'refreshToken',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='None',
        path="/"
    )
    
    return response


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

    response = make_response(jsonify({'message': f'{token_type} token revoked successfully'}), 200)
    response.delete_cookie(key='refreshToken', httponly=True, secure=True, samesite='None', path="/")

    return response


@auth_bp.delete('/deleteAccount')
@jwt_required()
@swag_from('docs/Auth/delete_profile.yml')
def delete_account():
    user_email = get_jwt_identity()
    user = User.get_user_by_email(user_email)

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    # logout_user()
    user.delete()

    response = make_response(jsonify({'message': f'User profile {user.username} deleted successfully'}), 200)
    response.delete_cookie('refreshToken')
    return response


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
    domen = os.getenv("DOMEN")
    data = request.get_json()
    user = User.get_user_by_email(email=data.get('email'))

    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    expires = datetime.timedelta(minutes=10)
    access_token = create_access_token(
        identity=user.email, expires_delta=expires)

    restore_link = f"{domen}login/restorePassword/?token={access_token}"

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



@auth_bp.put('/updateUserPassword')
@jwt_required()
@swag_from('docs/Auth/update_user_password.yml')
def update_user_password():
    user_email = get_jwt_identity()
    user = User.get_user_by_email(user_email)
    
    if not user:
        return jsonify({'error': 'User with this email is not registered'}), 404

    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not user.check_password(password=old_password):
        return jsonify({'error': 'The current password is incorrect'}), 400
    
    if user.check_password(password=new_password):
        return jsonify({'error': 'The new password cannot be the same as the current password'}), 400
    
    new_data = {
        'new_password': new_password
    }
    errors = update_password_schema.validate(new_data)

    if errors:
        return jsonify({'error': errors}), 400
    
    user.set_password(new_password)
    user.save()
    
    return jsonify({
        'message': 'User password updated successfully',
    }), 200
    
