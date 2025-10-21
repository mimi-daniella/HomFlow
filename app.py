from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re #for regex validation
from api_key import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///homflow.db"
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = SECRET_KEY
oauth = OAuth(app)

google = oauth.register(
    name= "google",
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration",
    api_base_url = "https://www.googleapis.com/oauth2/v1/",
    client_kwargs = {'scope': 'openid email profile'}
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable= False)
    username = db.Column(db.String(25), nullable = False)
    password_hash = db.Column(db.String(128), nullable=False)   

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
    


class SmartTvs(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        tv_label = db.Column(db.String(50), nullable = False)
        brand = db.Column(db.String(50), nullable = False)
        model = db.Column(db.String(50), nullable = False)
        platform = db.Column(db.String(50), nullable = False)
        control_method = db.Column(db.String(50), nullable = False)
        ip_address = db.Column(db.String(50))
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
        # relationship
        user = db.relationship('User', backref = db.backref('smart_tvs', lazy = True))



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
    
    validation = Validation(request.form)
    if not validation.is_valid_form():
        return render_template("signUp.html", errors = validation.errors)

    new_user = User(
        email = request.form['email'],
        username = request.form['username']
    )
    new_user.set_password(request.form['password'])
    db.session.add(new_user)
    db.session.commit()
    flash("Your acccount has been successfully created. You can now access HomFlow's dashboard.")
    print(f"New user created: {new_user.email}")
    session['user_id'] = new_user.id
    return redirect(url_for("dashboard"))

@app.route("/login")
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    email = user_info['email']
    user = User.query.filter_by(email=email).first()
    if user:
        session['user'] = user_info
        return redirect(url_for('dashboard'))
    else:
        new_user = User(
            email = user_info['email'],
            username = user_info['name'],
            # profile_pic = user_info['picture']
        )
        new_user.set_password("defaultpassword")  
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('dashboard'))

@app.route("/add_tv", methods=['POST'])
def add_tv():
    tv = SmartTvs(
        tv_label = request.form['tv_label'], 
        brand = request.form['brand'],
        model = request.form['model'],
        platform = request.form['platform'],
        control_method = request.form['control_method'],
        ip_address = request.form['ip_address'],
        user_id = session.get('user_id')
    )
    db.session.add(tv)
    db.session.commit()
    flash("TV added successfully!")
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
# @login_required
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for("register"))
    user = User.query.get(user_id)
    user_tvs = SmartTvs.query.filter_by(user_id=user.id).all()
    return render_template("dashboard.html",user = user, tvs=user_tvs)

@app.route("/delete_tv/<int:tv_id>", methods=['POST'])
def delete_tv(tv_id):
    tv = SmartTvs.query.get_or_404(tv_id)
    if tv.user_id != session.get('user_id'):
        flash("Unauthorized action.")
        return redirect(url_for("dashboard"))
    
    db.session.delete(tv)
    db.session.commit()
    flash("TV deleted successfully.")
    return redirect(url_for("dashboard"))





if __name__ == "__main__":
    with app.app_context():  
        # db.drop_all()  
        db.create_all()
    app.run( host='localhost', port=5000, debug = True)

