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

    def __repr__(self):
        return f"<User {self.username}>"

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise AssertionError('Username is required')
        if len(username) > 20:
            raise AssertionError('Username must be less than 10 characters')
        elif len(username) < 4:
            raise AssertionError('Username must be more than 4 characters')
        return username

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise AssertionError('Email is required')
        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise AssertionError('Invalid email address')
        return email

    def set_password(self, password):
        if not password:
            raise AssertionError('Password is required')
        if not re.match('\d.*[A-Z]|[A-Z].*\d', password):
            raise AssertionError(
                'Password must contain 1 capital letter and 1 number')
        if len(password) < 8 or len(password) > 50:
            raise AssertionError(
                'Password must be between 8 and 50 characters')

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
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
