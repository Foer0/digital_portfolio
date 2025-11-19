from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import User, Company, Portfolio, Vacancy, Application, db
from datetime import datetime

admin = Blueprint('admin', __name__)


@admin.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    stats = {
        'users_count': User.query.count(),
        'companies_count': Company.query.count(),
        'vacancies_count': Vacancy.query.count(),
        'applications_count': Application.query.count(),
        'pending_vacancies': Vacancy.query.filter_by(is_approved=False).count()
    }

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_vacancies = Vacancy.query.order_by(Vacancy.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_users=recent_users,
                           recent_vacancies=recent_vacancies)


@admin.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    user = db.session.get(User, user_id)  # Исправлено для SQLAlchemy 2.0

    # Не позволяем удалить самого себя
    if user.id == current_user.id:
        flash('Нельзя удалить собственный аккаунт')
        return redirect(url_for('admin.manage_users'))

    # Мягкое удаление - деактивация пользователя
    user.is_active = False
    db.session.commit()

    flash(f'Пользователь {user.name} деактивирован')
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/user/<int:user_id>/activate', methods=['POST'])
@login_required
def activate_user(user_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()

    flash(f'Пользователь {user.name} активирован')
    return redirect(url_for('admin.manage_users'))


@admin.route('/admin/vacancies')
@login_required
def manage_vacancies():
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    vacancies = Vacancy.query.all()
    return render_template('admin/vacancies.html', vacancies=vacancies)


@admin.route('/admin/vacancy/<int:vacancy_id>/toggle', methods=['POST'])
@login_required
def toggle_vacancy(vacancy_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403

    vacancy = Vacancy.query.get_or_404(vacancy_id)
    vacancy.is_active = not vacancy.is_active
    db.session.commit()

    flash('Статус вакансии изменен')
    return redirect(url_for('admin.manage_vacancies'))


@admin.route('/admin/vacancy/<int:vacancy_id>/approve', methods=['POST'])
@login_required
def approve_vacancy(vacancy_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403

    vacancy = Vacancy.query.get_or_404(vacancy_id)
    vacancy.is_approved = True
    db.session.commit()

    flash('Вакансия одобрена')
    return redirect(url_for('admin.manage_vacancies'))


@admin.route('/admin/vacancy/<int:vacancy_id>/reject', methods=['POST'])
@login_required
def reject_vacancy(vacancy_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403

    vacancy = Vacancy.query.get_or_404(vacancy_id)
    vacancy.is_approved = False
    db.session.commit()

    flash('Вакансия отклонена')
    return redirect(url_for('admin.manage_vacancies'))


@admin.route('/admin/vacancy/<int:vacancy_id>/delete', methods=['POST'])
@login_required
def delete_vacancy(vacancy_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    vacancy = Vacancy.query.get_or_404(vacancy_id)
    db.session.delete(vacancy)
    db.session.commit()

    flash('Вакансия удалена')
    return redirect(url_for('admin.manage_vacancies'))


@admin.route('/admin/portfolio/<int:portfolio_id>')
@login_required
def view_portfolio(portfolio_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('admin/portfolio_view.html', portfolio=portfolio)


@admin.route('/admin/portfolios')
@login_required
def manage_portfolios():
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    # Исправляем портфолио с отсутствующими датами
    broken_portfolios = Portfolio.query.filter(
        (Portfolio.created_at == None) | (Portfolio.updated_at == None)
    ).all()

    for portfolio in broken_portfolios:
        if portfolio.created_at is None:
            portfolio.created_at = datetime.utcnow()
        if portfolio.updated_at is None:
            portfolio.updated_at = datetime.utcnow()

    if broken_portfolios:
        db.session.commit()
        flash(f'Исправлено {len(broken_portfolios)} портфолио с отсутствующими датами')

    portfolios = Portfolio.query.all()
    return render_template('admin/portfolios.html', portfolios=portfolios)


@admin.route('/admin/company/<int:company_id>')
@login_required
def view_company(company_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    company = Company.query.get_or_404(company_id)
    vacancies = Vacancy.query.filter_by(company_id=company_id).all()

    return render_template('admin/company_view.html', company=company, vacancies=vacancies)


@admin.route('/admin/companies')
@login_required
def manage_companies():
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)