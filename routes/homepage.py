from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

homepage_bp = Blueprint('homepage', __name__, template_folder='templates')

@homepage_bp.route('/')
def homepage_index():
    # if current_user.is_authenticated:
    #     return redirect(url_for('dashboard'))
    return render_template('index.html')

