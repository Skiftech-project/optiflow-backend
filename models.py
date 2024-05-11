import re
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import validates
from sqlalchemy_utils import EmailType
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(), nullable=False)
    email = db.Column(EmailType, nullable=False, unique=True)
    password = db.Column(db.Text())
    
    saved_templates = db.relationship("SavedCalculationTemplate", back_populates="user", cascade='all, delete-orphan')
    token_block_list = db.relationship("TokenBlockList", back_populates="user", cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.username}>"

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise AssertionError('Username is required')
        if len(username) > 20:
            raise AssertionError('Username must be less than 20 characters')
        elif len(username) < 2:
            raise AssertionError('Username must be more than 2 characters')
        return username

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise AssertionError('Email is required')
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise AssertionError('Invalid email address')
        return email

    def set_password(self, password):
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
            raise AssertionError(errors)

        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class TokenBlockList(db.Model):
    __tablename__ = 'token_block_list'
    id = db.Column(db.Integer(), primary_key=True)
    
    user_id = db.Column(db.String(), db.ForeignKey(User.id))
    user = db.relationship("User", back_populates="token_block_list")
    
    jti = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti}>"

    def save(self, user_id):
        self.user_id = user_id
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_token_by_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class CalculationTemplate(db.Model):
    __tablename__ = 'calculation_templates'
    template_name = db.Column(db.String(), primary_key=True)
    sensitivity = db.Column(db.Float(), nullable=False)
    power = db.Column(db.Float(), nullable=False)

    plume_form = db.Column(db.String(), nullable=False)

    angle_width = db.Column(db.Float(), nullable=True)
    angle_height = db.Column(db.Float(), nullable=True)

    distance = db.Column(db.Float(), nullable=True)
    spot_width = db.Column(db.Float(), nullable=True)
    spot_height = db.Column(db.Float(), nullable=True)
    min_plume_size = db.Column(db.Float(), nullable=True)
    distance_for_plume_size = db.Column(db.Float(), nullable=True)

    def __repr__(self):
        return f"<Template {self.template_name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_templates(cls):
        return cls.query.all()


class SavedCalculationTemplate(db.Model):
    __tablename__ = 'saved_calculation_templates'
    id = db.Column(db.Integer(), primary_key=True)
    
    
    user_id = db.Column(db.String(), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="saved_templates")
    
    sensitivity = db.Column(db.Float(), nullable=False)
    power = db.Column(db.Float(), nullable=False)

    plume_form = db.Column(db.String(), nullable=False)

    angle_width = db.Column(db.Float(), nullable=False)
    angle_height = db.Column(db.Float(), nullable=False)

    distance = db.Column(db.Float(), nullable=True)
    spot_width = db.Column(db.Float(), nullable=True)
    spot_height = db.Column(db.Float(), nullable=True)
    min_plume_size = db.Column(db.Float(), nullable=True)
    distance_for_plume_size = db.Column(db.Float(), nullable=True)
    
    
    max_distance = db.Column(db.Float(), nullable=False)
    min_distance = db.Column(db.Float(), nullable=True)
    plume_width_module3 = db.Column(db.Float(), nullable=True)
    plume_height_module3 = db.Column(db.Float(), nullable=True)
    

    def __repr__(self):
        return f"<Template {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_saved_templates(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()