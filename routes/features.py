from flask import Blueprint, render_template

features_bp = Blueprint('features',__name__, template_folder='templates')

@features_bp.route('/features')
def features_page():
    return render_template('features.html')


