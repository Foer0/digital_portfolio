from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from auth import auth
from employer import employer
from seeker import seeker
from admin import admin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'

# Инициализация базы данных
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Регистрация Blueprint
app.register_blueprint(auth)
app.register_blueprint(employer)
app.register_blueprint(seeker)
app.register_blueprint(admin)

@login_manager.user_loader
def load_user(user_id):
    # Исправляем для SQLAlchemy 2.0
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    from models import Vacancy
    # Показываем только активные и одобренные вакансии
    vacancies = Vacancy.query.filter_by(is_active=True, is_approved=True).order_by(Vacancy.created_at.desc()).limit(3).all()
    return render_template('index.html', vacancies=vacancies)

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

# Глобальный контекст для поиска
@app.context_processor
def inject_global_vars():
    return {
        'search_query': request.args.get('search', ''),
        'current_path': request.path
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Создаём или обновляем администратора с правильным паролем
        admin_user = db.session.get(User, 1)
        if not admin_user:
            admin_user = User(
                email='admin@admin.com',
                password=generate_password_hash('Admin123!', method='pbkdf2:sha256'),
                name='Administrator',
                role='admin'
            )
            db.session.add(admin_user)
            print("Администратор создан: admin@admin.com / Admin123!")
        else:
            # Обновляем пароль администратора
            admin_user.password = generate_password_hash('Admin123!', method='pbkdf2:sha256')
            print("Пароль администратора обновлен: Admin123!")

        # Обновляем пароли для тестовых пользователей
        test_users = [
            (2, 'alex.ivanov@mail.ru', 'Password123!'),
            (3, 'maria.petrova@gmail.com', 'Password123!'),
            (4, 'sergey.smirnov@yandex.ru', 'Password123!'),
            (5, 'ekaterina.volkova@mail.ru', 'Password123!'),
            (6, 'hr@techcompany.ru', 'Password123!'),
            (7, 'careers@webstudio.com', 'Password123!'),
            (8, 'jobs@fintech.org', 'Password123!')
        ]

        for user_id, email, password in test_users:
            user = db.session.get(User, user_id)
            if user:
                user.password = generate_password_hash(password, method='pbkdf2:sha256')
                print(f"Пароль для {email} обновлен: {password}")

        db.session.commit()

    app.run(debug=True)