from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import User, Company, Portfolio, Vacancy, Application, db
from datetime import datetime
from sqlalchemy import desc, asc

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
        'pending_vacancies': Vacancy.query.filter_by(is_approved=False).count(),
        'pending_portfolios': Portfolio.query.filter_by(is_approved=False).count(),
        'pending_companies': Company.query.filter_by(is_approved=False).count()
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

    # Параметры сортировки
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    # Доступные поля для сортировки
    valid_sort_fields = ['id', 'name', 'email', 'role', 'created_at', 'last_login']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'

    # Применяем сортировку
    if order == 'desc':
        users = User.query.order_by(desc(getattr(User, sort_by))).all()
    else:
        users = User.query.order_by(asc(getattr(User, sort_by))).all()

    return render_template('admin/users.html',
                           users=users,
                           sort_by=sort_by,
                           order=order)


@admin.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    user = db.session.get(User, user_id)

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

    # Параметры сортировки
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    # Доступные поля для сортировки
    valid_sort_fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'is_approved']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'

    # Применяем сортировку
    if order == 'desc':
        vacancies = Vacancy.query.order_by(desc(getattr(Vacancy, sort_by))).all()
    else:
        vacancies = Vacancy.query.order_by(asc(getattr(Vacancy, sort_by))).all()

    return render_template('admin/vacancies.html',
                           vacancies=vacancies,
                           sort_by=sort_by,
                           order=order)


@admin.route('/admin/vacancy/<int:vacancy_id>')
@login_required
def view_vacancy(vacancy_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    vacancy = Vacancy.query.get_or_404(vacancy_id)
    return render_template('admin/vacancy_view.html', vacancy=vacancy)


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

    # Сначала удаляем все связанные заявки
    applications = Application.query.filter_by(vacancy_id=vacancy_id).all()
    for application in applications:
        db.session.delete(application)

    # Затем удаляем саму вакансию
    db.session.delete(vacancy)
    db.session.commit()

    flash('Вакансия и связанные заявки удалены')
    return redirect(url_for('admin.manage_vacancies'))


@admin.route('/admin/portfolio/<int:portfolio_id>')
@login_required
def view_portfolio(portfolio_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('admin/portfolio_view.html', portfolio=portfolio)


@admin.route('/admin/portfolio/<int:portfolio_id>/approve', methods=['POST'])
@login_required
def approve_portfolio(portfolio_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio.is_approved = True
    db.session.commit()

    flash('Портфолио одобрено')
    return redirect(url_for('admin.manage_portfolios'))


@admin.route('/admin/portfolio/<int:portfolio_id>/reject', methods=['POST'])
@login_required
def reject_portfolio(portfolio_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio.is_approved = False
    db.session.commit()

    flash('Портфолио отклонено')
    return redirect(url_for('admin.manage_portfolios'))


@admin.route('/admin/portfolio/<int:portfolio_id>/delete', methods=['POST'])
@login_required
def delete_portfolio(portfolio_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    portfolio = Portfolio.query.get_or_404(portfolio_id)

    # Сначала удаляем все связанные заявки
    applications = Application.query.filter_by(portfolio_id=portfolio_id).all()
    for application in applications:
        db.session.delete(application)

    # Затем удаляем само портфолио
    db.session.delete(portfolio)
    db.session.commit()

    flash('Портфолио и связанные заявки удалены')
    return redirect(url_for('admin.manage_portfolios'))


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

    # Параметры сортировки
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    # Доступные поля для сортировки
    valid_sort_fields = ['id', 'title', 'profession', 'experience_years', 'created_at', 'updated_at', 'is_approved']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'

    # Применяем сортировку
    if order == 'desc':
        portfolios = Portfolio.query.order_by(desc(getattr(Portfolio, sort_by))).all()
    else:
        portfolios = Portfolio.query.order_by(asc(getattr(Portfolio, sort_by))).all()

    return render_template('admin/portfolios.html',
                           portfolios=portfolios,
                           sort_by=sort_by,
                           order=order)


@admin.route('/admin/company/<int:company_id>')
@login_required
def view_company(company_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    company = Company.query.get_or_404(company_id)
    vacancies = Vacancy.query.filter_by(company_id=company_id).all()

    return render_template('admin/company_view.html', company=company, vacancies=vacancies)


@admin.route('/admin/company/<int:company_id>/approve', methods=['POST'])
@login_required
def approve_company(company_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()

    flash('Компания одобрена')
    return redirect(url_for('admin.manage_companies'))


@admin.route('/admin/company/<int:company_id>/reject', methods=['POST'])
@login_required
def reject_company(company_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    company = Company.query.get_or_404(company_id)
    company.is_approved = False
    db.session.commit()

    flash('Компания отклонена')
    return redirect(url_for('admin.manage_companies'))


@admin.route('/admin/company/<int:company_id>/delete', methods=['POST'])
@login_required
def delete_company(company_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    company = Company.query.get_or_404(company_id)

    # Сначала удаляем все вакансии компании и связанные заявки
    vacancies = Vacancy.query.filter_by(company_id=company_id).all()
    for vacancy in vacancies:
        # Удаляем заявки на эту вакансию
        applications = Application.query.filter_by(vacancy_id=vacancy.id).all()
        for application in applications:
            db.session.delete(application)
        # Удаляем вакансию
        db.session.delete(vacancy)

    # Затем удаляем саму компанию
    db.session.delete(company)
    db.session.commit()

    flash('Компания, её вакансии и связанные заявки удалены')
    return redirect(url_for('admin.manage_companies'))


@admin.route('/admin/companies')
@login_required
def manage_companies():
    if current_user.role != 'admin':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    # Параметры сортировки
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    # Доступные поля для сортировки
    valid_sort_fields = ['id', 'company_name', 'industry', 'created_at', 'updated_at', 'is_approved']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'

    # Применяем сортировку
    if order == 'desc':
        companies = Company.query.order_by(desc(getattr(Company, sort_by))).all()
    else:
        companies = Company.query.order_by(asc(getattr(Company, sort_by))).all()

    return render_template('admin/companies.html',
                           companies=companies,
                           sort_by=sort_by,
                           order=order)