from flask import Flask, render_template, request, redirect, url_for, jsonify, redirect
from models import db, User, Validation, SmartTvs, get_tv_ip
from flask_migrate import Migrate
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
import asyncio
import os
from dotenv import load_dotenv
from tvControls import run_tv_command, test_connection
from routes.homepage import homepage_bp
from routes.features import features_bp



load_dotenv()
app = Flask(__name__)

#routes
app.register_blueprint(homepage_bp)
app.register_blueprint(features_bp)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///homflow.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db.init_app(app)
migrate =  Migrate(app, db)
oauth = OAuth(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_password"


google = oauth.register(
    name= "google",
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration",
    api_base_url = "https://www.googleapis.com/oauth2/v1/",
    client_kwargs = {'scope': 'openid email profile'}
)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("pageNotFound.html"), 404


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("signUp.html", errors={}, success=None, error=None)

    try:
        validation = Validation(request.form)
        if not validation.is_valid_form():
             return render_template("signUp.html", errors=validation.errors, success=None, error = None)

        new_user = User(
            email=request.form['email'],
            username=request.form['username']
        )
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return render_template("signUp.html", success="Registration successful.", errors = {}, error = None)
    except Exception as e:
        db.session.rollback()
        return render_template("signUp.html", errors = {}, success=None,error=f"Registration failed. {e}")


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

@app.route("/login_password", methods=['GET', 'POST'])
def login_password():
    if request.method == 'GET':
        return render_template("logIn.html", success=None, error=None)

    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()

    if not user:
        return render_template("logIn.html", success=None, error="Invalid credentials. Please try again.")

    if user and user.check_password( password):
        login_user(user)
        return render_template("login.html", success="Login successful.", error=None)
    else:
        return render_template("logIn.html", success=None, error="Invalid credentials. Please try again.")
        
@app.route("/dashboard")
@login_required
def dashboard():
    user_tvs = SmartTvs.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html",user = current_user, tvs=user_tvs)
        

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
    

@app.route("/logout", methods=['POST'])
@login_required
def logout():
    # clearing user session
    logout_user()
    return redirect(url_for('homepage'))

@app.route("/delete_account/<int:user_id>", methods=['POST'])
def delete_account(user_id):
    user = User.query.get(user_id)
    if user and user.id == current_user.id:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("homepage"))
    else:
        pass
    




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
        return render_template("dashboard.html", user=current_user, tvs=current_user.smart_tvs, success="TV added successfully!", error=None)
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR during TV addition: {e}") 
        return render_template("dashboard.html", user=current_user, tvs=current_user.smart_tvs, success=None, error="Failed to add TV. Please try again.")
        



@app.route("/delete_tv/<int:tv_id>", methods=['POST'])
@login_required
def delete_tv(tv_id):
    tv = SmartTvs.query.get_or_404(tv_id)
    if tv.user_id != current_user.id:
        return render_template("dashboard.html", user=current_user, tvs=current_user.smart_tvs, success=None, error="Unauthorized action.")
    try:
        db.session.delete(tv)
        db.session.commit()
        return render_template("dashboard.html", user = current_user, tvs = current_user.smart_tvs, success="Tv deleted successfully!" , error=None)
    except Exception as e:
        db.session.rollback()
        print(f"ERROR during TV deletion: {e}")
        return render_template("dashboard.html", user=current_user, tvs=current_user.smart_tvs, success=None, error="Failed to delete TV. Please try again.")


# tv brand routing controls
@app.route("/connect-samsung-tv", methods=['POST'])
def connect_samsung():
    try:
        print("Starting connection to Samsung TV...")
        asyncio.run(test_connection())
        print("Samsung TV connection complete.")
        return redirect(url_for('dashboard'))

    except Exception as e:
        print(f"Error during Samsung TV connection: {e}")
        return jsonify({"success": False, "error": {e}}), 500
    

@app.route('/power-toggle', methods=['POST'])
def power_toggle():
    return run_tv_command("power_toggle")

@app.route('/volume-up', methods=['POST'])
def volume_up():
    return run_tv_command("volume_up")

@app.route("/volume-down", methods=['POST'])
def volume_down():
    return run_tv_command("volume_down")


if __name__ == "__main__":
    with app.app_context():  
        app.run( host='localhost', port=5000, debug = True)


 