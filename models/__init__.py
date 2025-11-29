from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .user import User, Validation
from .smartTvs import SmartTvs, get_tv_ip