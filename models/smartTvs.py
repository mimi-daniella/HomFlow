from flask_sqlalchemy import SQLAlchemy
from models import db

# smart tv model
class SmartTvs(db.Model):
        __tablename__ ='smart_tvs'
        id = db.Column(db.Integer, primary_key = True)
        tv_label = db.Column(db.String(50), nullable = False)
        ip_address = db.Column(db.String(50), nullable = False)
        platform = db.Column(db.String(50), nullable = False)
        control_method = db.Column(db.String(50), nullable = False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
        # relationship
        owner = db.relationship('User', backref = db.backref('smart_tvs', lazy = True))


def get_tv_ip(user_id, label = None):
    if label:
        tv = SmartTvs.query.filter_by(user_id=user_id, tv_label=label).first()
    else:
        tv = SmartTvs.query.filter_by(user_id=user_id).first()
    return tv.ip_address if tv else None

