import re

from marshmallow import Schema, ValidationError, fields, validate


def validate_password(password):

    errors = {}
    if len(password) < 8:
        errors['length'] = 'Password must be at least 8 characters long'
    if len(password) > 50:
        errors['length'] = 'Password must not exceed 50 characters'

    if not re.match(r'^(?=.*[a-z])', password):
        errors['lowercase'] = 'Password must contain at least one lowercase letter'

    if not re.match(r'^(?=.*[A-Z])', password):
        errors['uppercase'] = 'Password must contain at least one uppercase letter'

    if not re.match(r'^(?=.*\d)', password):
        errors['digit'] = 'Password must contain at least one digit'

    if not re.match(r'^(?=.*[@$!%*?&])', password):
        errors['special'] = 'Password must contain at least one special character'

    if errors:
        raise ValidationError(errors)


class UserSchema(Schema):
    id = fields.String(dump_only=True)
    username = fields.String(
        required=True, validate=validate.Length(min=2, max=20))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate_password)


class UserUpdateSchema(Schema):
    username = fields.String(
        required=False, validate=validate.Length(min=2, max=20))
    email = fields.Email(required=False)
    password = fields.String(required=False, validate=validate_password)
    
    
class UserUpdatePasswordSchema(Schema):
    new_password = fields.String(required=False, validate=validate_password)


class CalculationTemplateSchema(Schema):
    template_name = fields.String(required=True)
    sensitivity = fields.Float(required=True)
    power = fields.Float(required=True)
    plume_form = fields.String(required=True)
    angle_width = fields.Float(required=True)
    angle_height = fields.Float(required=True)
    distance = fields.Float()
    spot_width = fields.Float()
    spot_height = fields.Float()
    min_plume_size = fields.Float()
    distance_for_plume_size = fields.Float()


class SavedCalculationTemplateSchema(Schema):
    id = fields.Integer(required=True)
    calculator_type = fields.String(required=True)
    user_id = fields.String(required=True)
    sensitivity = fields.Float(required=True)
    power = fields.Float(required=True)
    plume_form = fields.String(required=True)
    angle_width = fields.Float(required=True)
    angle_height = fields.Float(required=True)
    distance = fields.Float()
    spot_width = fields.Float()
    spot_height = fields.Float()
    min_plume_size = fields.Float()
    distance_for_plume_size = fields.Float()
    max_distance = fields.Float(required=True)
    min_distance = fields.Float()
    plume_width_module3 = fields.Float()
    plume_height_module3 = fields.Float()
