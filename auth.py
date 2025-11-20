from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Company, Portfolio, db
import re
import html

auth = Blueprint('auth', __name__)


def validate_password(password):
    """Проверка сложности пароля"""
    if len(password) < 8:
        return "Пароль должен содержать минимум 8 символов"
    if not re.search(r"[A-Z]", password):
        return "Пароль должен содержать хотя бы одну заглавную букву"
    if not re.search(r"[a-z]", password):
        return "Пароль должен содержать хотя бы одну строчную букву"
    if not re.search(r"[0-9]", password):
        return "Пароль должен содержать хотя бы одну цифру"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return "Пароль должен содержать хотя бы один специальный символ"
    return None


def validate_email(email):
    """Проверка валидности email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_name(name):
    """Проверка имени"""
    if len(name.strip()) < 2:
        return "Имя должно содержать минимум 2 символа"
    if len(name.strip()) > 50:
        return "Имя слишком длинное (максимум 50 символов)"
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', name):
        return "Имя может содержать только буквы, пробелы и дефисы"
    return None


def sanitize_input(text):
    """Очистка ввода от потенциально опасного контента"""
    if not text:
        return text
    # Экранируем HTML-символы
    return html.escape(text.strip())


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        if not email or not password:
            flash('Заполните все обязательные поля')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Пользователь с таким email не найден')
            return redirect(url_for('auth.login'))

        if not check_password_hash(user.password, password):
            flash('Неверный пароль')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Ваш аккаунт деактивирован. Обратитесь к администратору.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)

        # Редирект в зависимости от роли
        if user.role == 'employer':
            flash('Добро пожаловать в личный кабинет работодателя!')
            return redirect(url_for('employer.dashboard'))
        elif user.role == 'admin':
            flash('Добро пожаловать в админ-панель!')
            return redirect(url_for('admin.admin_panel'))
        else:
            flash('Добро пожаловать в личный кабинет соискателя!')
            return redirect(url_for('seeker.dashboard'))

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = sanitize_input(request.form.get('name', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role')

        # Валидация полей
        if not all([email, name, password, confirm_password, role]):
            flash('Заполните все обязательные поля')
            return redirect(url_for('auth.register'))

        # Валидация email
        if not validate_email(email):
            flash('Введите корректный email адрес')
            return redirect(url_for('auth.register'))

        # Валидация имени
        name_error = validate_name(name)
        if name_error:
            flash(name_error)
            return redirect(url_for('auth.register'))

        # Проверка совпадения паролей
        if password != confirm_password:
            flash('Пароли не совпадают')
            return redirect(url_for('auth.register'))

        # Валидация сложности пароля
        password_error = validate_password(password)
        if password_error:
            flash(password_error)
            return redirect(url_for('auth.register'))

        # Проверка уникальности email
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email уже зарегистрирован')
            return redirect(url_for('auth.register'))

        # Создание пользователя
        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        # Создаём профиль в зависимости от роли
        if role == 'employer':
            company = Company(
                user_id=new_user.id,
                company_name=name
            )
            db.session.add(company)
        elif role == 'seeker':
            portfolio = Portfolio(
                user_id=new_user.id,
                title=f"Портфолио {name}",
                profession="Специалист"
            )
            db.session.add(portfolio)

        db.session.commit()
        login_user(new_user)

        flash('Регистрация успешна! Добро пожаловать!')
        if role == 'employer':
            return redirect(url_for('employer.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.admin_panel'))
        else:
            return redirect(url_for('seeker.dashboard'))

    return render_template('auth/register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы')
    return redirect(url_for('index'))