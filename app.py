from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re 
from authlib.integrations.flask_client import OAuth
import asyncio
from samsung import SamsungController 
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///homflow.db"
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
oauth = OAuth(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_password"


# Samsung websocket
async def main_application_logic():
    print ("Starting Samsung app...")

    if not current_user.is_authenticated:
        print("User is not logged in.")
        return
    tv_ip = get_tv_ip(current_user.id)

    if not tv_ip:
        # flash("No TV found. Please add a TV to your account.", "error")
        return

    # initialize the class
    controller = SamsungController(host=tv_ip)
    # testing connection
    connected = await controller.connect()
    if connected:
        print("Sending commands to tv for testing connection...")
        await controller.volume_up()
        await controller.volume_down()
    else:
        print("Cannot proceed with the application. Please check your connection to the TV.")


google = oauth.register(
    name= "google",
    client_id = os.environ.get('CLIENT_ID'),
    client_secret = os.environ.get('CLIENT_SECRET'),
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration",
    api_base_url = "https://www.googleapis.com/oauth2/v1/",
    client_kwargs = {'scope': 'openid email profile'}
)

# user model
class User(db.Model, UserMixin):
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
    

# smart tv model
class SmartTvs(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        tv_label = db.Column(db.String(50), nullable = False)
        ip_address = db.Column(db.String(50), nullable = False)
        platform = db.Column(db.String(50), nullable = False)
        control_method = db.Column(db.String(50), nullable = False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
        # relationship
        user = db.relationship('User', backref = db.backref('smart_tvs', lazy = True))


def get_tv_ip(user_id, label = None):
    if label:
        tv = SmartTvs.query.filter_by(user_id=user_id, tv_label=label).first()
    else:
        tv = SmartTvs.query.filter_by(user_id=user_id).first()
    return tv.ip_address if tv else None


# routes
@app.route("/")
def homepage():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("pageNotFound.html"), 404


@app.route("/register", methods =['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("signUp.html", errors = {})
    
    try:
        validation = Validation(request.form)
        if not validation.is_valid_form():
            first_error_key = next(iter(validation.errors))
            error_message = validation.errors[first_error_key][0]
            return jsonify({
                "status": "error",
                "message": f"Validation failed: {error_message}"  
                }), 400

        new_user = User(
        email = request.form['email'],
        username = request.form['username']
        )
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return jsonify({"status": "ok", "message": "Registration successful! \n You can now access dashboard!", "redirect_url": "/dashboard"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error during user registration: {e}")
        return jsonify({"status": "error", "message": f"Database error ({str(e)})"}), 500



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/add_tv') or request.path.startswith('/delete_tv'):
        return jsonify({"status": "error","message": "Please log in to access this page."}), 401
    return redirect(url_for('login_password'))

@app.route("/login")
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/login_password", methods = ['GET', 'POST'])
def login_password():
    if request.method == 'GET':
        return render_template("logIn.html")
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and user.check_password_hash(password):
        login_user(user)
        # flash('Logged in successfully.')
        return redirect(url_for('dashboard'))
    else:
        # flash('Invalid email or password. Please try again.', 'error')
        return render_template("logIn.html", error="Invalid email or password. Please try again. ")

@app.route("/authorize")
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
    except Exception as e:
        print(f"Error during Google auth: {e}")
        return redirect(url_for('login_password', error='Google login failed. Please check your credentials and try again.'))

    email = user_info['email']
    user = User.query.filter_by(email=email).first()
    
    if user:
        # Existing user logs in
        login_user(user) 
        return redirect(url_for('dashboard'))
    else:
        # New Google user signup
        new_user = User(
            email = user_info['email'],
            username = user_info['name'],
            google_id = user_info.get('id') or user_info.get('sub')
        )
        new_user.set_password("oauth_no_password_set") 
        db.session.add(new_user)
        db.session.commit()
        
        # FIX for 'NoneType' error: Log in the user object after commit
        login_user(new_user) 
        return redirect(url_for('dashboard'))
    


# @login_required
@app.route("/add_tv", methods=['POST'])
@login_required
def add_tv():
    print("Received form data for adding TV:", request.form) 
    try:
        tv = SmartTvs(
            tv_label = request.form['tv_label'], 
            ip_address = request.form['ip_address'],
            platform = request.form['platform'],
            control_method = request.form['control_method'],
            user_id = current_user.id
        )
        db.session.add(tv)
        db.session.commit()
        
        new_tv_data = { 
            "id": tv.id, 
            "tv_label": tv.tv_label, 
            "ip_address": tv.ip_address, 
            "platform": tv.platform, 
            "control_method": tv.control_method 
        }
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        print(f"ERROR during TV addition: {e}") 
        return jsonify({"status": "error", "message": f"Database Error: {str(e)}"}), 500
        


@app.route("/dashboard")
@login_required
def dashboard():
    user_tvs = SmartTvs.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html",user = current_user, tvs=user_tvs)


@app.route("/delete_tv/<int:tv_id>", methods=['POST'])
def delete_tv(tv_id):
    tv = SmartTvs.query.get_or_404(tv_id)
    if tv.user_id != current_user.id:
        # flash("Unauthorized action.", "error")
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    db.session.delete(tv)
    db.session.commit()
    # flash("TV deleted successfully.", "success")
    return jsonify({"status": "success", "message": "Tv deleted successfully."}), 200


# tv brand routing controls
@app.route("/connect-samsung-tv", methods=['POST'])
def connect_samsung():
    asyncio.run(main_application_logic())
    return True

@app.route('/power-toggle', methods=['POST'])
def power_toggle():

    tv_ip = get_tv_ip(current_user.id)
    controller = SamsungController(host=tv_ip)
    asyncio.run(controller.power_toggle())
    return jsonify({"status": "success", "message": "Power toggle"}), 200

@app.route('/volume-up', methods=['POST'])
def volume_up():

    tv_ip = get_tv_ip(current_user.id)
    controller = SamsungController(host=tv_ip)
    asyncio.run(controller.volume_up())
    return jsonify({"status": "success", "message": "volume_up"}), 200

@app.route("/volume-down", methods=['POST'])
def volume_down():

    tv_ip = get_tv_ip(current_user.id)
    controller = SamsungController(host=tv_ip)
    asyncio.run(controller.volume_down())
    return jsonify({"status": "success", "message": "volume_down"}), 200


if __name__ == "__main__":
    with app.app_context():  
        db.drop_all()  
        db.create_all()
    app.run( host='localhost', port=5000, debug = True)


 