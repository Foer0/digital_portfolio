from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import re

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    portfolios = db.relationship('Portfolio', backref='user', lazy=True)
    company = db.relationship('Company', backref='user', uselist=False, lazy=True)
    vacancies = db.relationship('Vacancy', backref='employer', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Автоматическая проверка email при создании
        if not self._validate_email(self.email):
            raise ValueError("Invalid email format")

    @staticmethod
    def _validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    contact_email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Новое поле для модерации компаний
    is_approved = db.Column(db.Boolean, default=False, nullable=False)


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    education = db.Column(db.Text)
    projects = db.Column(db.Text)
    contact_info = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    # Новое поле для модерации портфолио
    is_approved = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Гарантируем, что created_at и updated_at всегда установлены
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    employment_type = db.Column(db.String(50))  # full-time, part-time, remote
    experience_level = db.Column(db.String(50))  # junior, middle, senior
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)  # Модерация вакансий
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = db.relationship('Company', backref='vacancies', lazy=True)
    applications = db.relationship('Application', backref='vacancy', lazy=True)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'), nullable=False)
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, reviewed, rejected, accepted
    # Новое поле для причины отказа
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seeker = db.relationship('User', backref='applications', lazy=True)
    portfolio = db.relationship('Portfolio', backref='applications', lazy=True)