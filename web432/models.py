from .database import db
from flask_login import UserMixin
from datetime import datetime

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    photo = db.Column(db.String(255), default='profile/logo.png')
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_url_en = db.Column(db.String(255), unique=True, nullable=False)
    news_url_pt = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(20), default='draft')
    title_en = db.Column(db.String(255), unique=True, nullable=False)
    title_pt = db.Column(db.String(255), unique=True, nullable=False)
    summary_en = db.Column(db.Text, nullable=False)
    summary_pt = db.Column(db.Text, nullable=False)
    body_en = db.Column(db.Text, nullable=False)
    body_pt = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    cover = db.Column(db.String(200), nullable=True)
    photos = db.Column(db.String(2000), nullable=True)
    photographers = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)