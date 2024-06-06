import re

from marshmallow import Schema, ValidationError, fields, validate, post_dump


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
    id = fields.Integer(required=True, dump_only=True)
    user_id = fields.String(required=True, dump_only=True)
    calculator_type = fields.String(required=True)
    title = fields.String(required=True)
    sensitivity = fields.Float(required=True)
    power = fields.Float(required=True)
    plume_form = fields.String(required=True)
    angle_width = fields.Float(required=True)
    angle_height = fields.Float(required=True)
    distance = fields.Float(allow_none=True)
    spot_width = fields.Float(allow_none=True)
    spot_height = fields.Float(allow_none=True)
    min_plume_size = fields.Float()
    distance_for_plume_size = fields.Float()
    max_distance = fields.Float(required=True)
    min_distance = fields.Float()
    plume_width_module3 = fields.Float()
    plume_height_module3 = fields.Float()

    @post_dump
    def split_data(self, data, many, **kwargs):
        print(f'----------------------{data}------------------------------')

        input_data = {
            'calculator_type': data.pop('calculator_type'),
            'sensitivity': data.pop('sensitivity'),
            'power': data.pop('power'),
            'plume_form': data.pop('plume_form'),
            'distance': data.pop('distance'),
            'spot_width': data.pop('spot_width'),
            'spot_height': data.pop('spot_height'),
            'min_plume_size': data.pop('min_plume_size'),
            'distance_for_plume_size': data.pop('distance_for_plume_size')
        }
        output_data = {
            'max_distance': data.pop('max_distance'),
            'min_distance': data.pop('min_distance'),
            'plume_width_module3': data.pop('plume_width_module3'),
            'plume_height_module3': data.pop('plume_height_module3')
        }
        if input_data.get('distance') is None and input_data.get('spot_width') is None and input_data.get('spot_height') is None:
            input_data['angle_width'] = data.pop('angle_width')
            input_data['angle_height'] = data.pop('angle_height')
        else:
            output_data['angle_width'] = data.pop('angle_width')
            output_data['angle_height'] = data.pop('angle_height')
        data['title'] = data.pop('title')
        data['input_data'] = input_data
        data['output_data'] = output_data
        return data
