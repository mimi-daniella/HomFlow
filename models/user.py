from flask_sqlalchemy import SQLAlchemy
import re
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

# user model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable= False)
    username = db.Column(db.String(25), nullable = False)
    password_hash = db.Column(db.String(128), nullable=False)
    google_id = db.Column(db.String(128), unique=True, nullable=True)
    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} {self.username}>"
    

class Validation:
    def __init__(self, data):
        self.data = data
        self.errors = {}

    def is_valid_email(self, pattern):
        email = self.data.get("email")
        if not re.match(pattern, email):
            self.errors['email'] = "Invalid email adress"
        return re.match(pattern, email) is not None
    
    def is_unique_email(self, email):
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            self.errors['email'] = "Email has already been used. Please try a different one."
     
    def is_strong_password(self): 
        password = self.data.get("password")
        if len(password) < 8:
            self.errors['password'] = "Password must be at least 8 characters long"
        confirm_password = self.data.get('confirm_password')
        if password != confirm_password:
            self.errors['confirm_password'] = "Passwords do not match"

    def is_valid_form(self):
        self.is_valid_email( r'^[\w\.-]+@[\w\.-]+\.\w+$')
        self.is_unique_email(self.data.get("email"))
        self.is_strong_password()
        return not self.errors
    