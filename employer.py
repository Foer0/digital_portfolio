from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Company, Vacancy, Application, User, Portfolio, db

employer = Blueprint('employer', __name__)


@employer.route('/employer/dashboard')
@login_required
def dashboard():
    if current_user.role != 'employer':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    company = Company.query.filter_by(user_id=current_user.id).first()
    vacancies = Vacancy.query.filter_by(employer_id=current_user.id).all()
    applications = Application.query.join(Vacancy).filter(Vacancy.employer_id == current_user.id).all()

    return render_template('employer/dashboard.html',
                           company=company,
                           vacancies=vacancies,
                           applications=applications)


@employer.route('/employer/company/edit', methods=['GET', 'POST'])
@login_required
def edit_company():
    if current_user.role != 'employer':
        return redirect(url_for('index'))

    company = Company.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        if not company:
            company = Company(user_id=current_user.id)
            db.session.add(company)

        company.company_name = request.form.get('company_name')
        company.description = request.form.get('description')
        company.industry = request.form.get('industry')
        company.website = request.form.get('website')
        company.contact_email = request.form.get('contact_email')
        company.phone = request.form.get('phone')
        company.address = request.form.get('address')
        # Сбрасываем статус модерации при редактировании
        company.is_approved = False

        db.session.commit()
        flash('Информация о компании обновлена и отправлена на модерацию')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/edit_company.html', company=company)


@employer.route('/employer/vacancy/create', methods=['GET', 'POST'])
@login_required
def create_vacancy():
    if current_user.role != 'employer':
        return redirect(url_for('index'))

    company = Company.query.filter_by(user_id=current_user.id).first()

    # Проверяем, есть ли компания и одобрена ли она
    if not company:
        flash('Сначала заполните информацию о компании')
        return redirect(url_for('employer.edit_company'))

    if not company.is_approved:
        flash('Ваша компания находится на модерации. Вы не можете создавать вакансии до завершения проверки.')
        return redirect(url_for('employer.dashboard'))

    if request.method == 'POST':
        vacancy = Vacancy(
            employer_id=current_user.id,
            company_id=company.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            requirements=request.form.get('requirements'),
            salary_min=request.form.get('salary_min'),
            salary_max=request.form.get('salary_max'),
            employment_type=request.form.get('employment_type'),
            experience_level=request.form.get('experience_level'),
            location=request.form.get('location')
        )

        db.session.add(vacancy)
        db.session.commit()
        flash('Вакансия создана и отправлена на модерацию')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/create_vacancy.html')


@employer.route('/employer/portfolio/<int:portfolio_id>')
@login_required
def view_portfolio(portfolio_id):
    if current_user.role != 'employer':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    portfolio = db.session.get(Portfolio, portfolio_id)
    if not portfolio:
        flash('Портфолио не найдено')
        return redirect(url_for('employer.dashboard'))

    # Проверяем, что портфолио одобрено модератором
    if not portfolio.is_approved:
        flash('Это портфолио находится на модерации и недоступно для просмотра')
        return redirect(url_for('employer.dashboard'))

    # Проверяем, что портфолио публичное или работодатель имеет отношение к откликам
    if not portfolio.is_public:
        # Проверяем, есть ли отклик от этого соискателя на вакансии работодателя
        application = Application.query.join(Vacancy).filter(
            Application.portfolio_id == portfolio_id,
            Vacancy.employer_id == current_user.id
        ).first()

        if not application:
            flash('Это портфолио недоступно для просмотра')
            return redirect(url_for('employer.dashboard'))

    return render_template('employer/portfolio_view.html', portfolio=portfolio)


@employer.route('/employer/application/<int:application_id>/update_status', methods=['POST'])
@login_required
def update_application_status(application_id):
    if current_user.role != 'employer':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    application = db.session.get(Application, application_id)
    if not application:
        flash('Заявка не найдена')
        return redirect(url_for('employer.dashboard'))

    # Проверяем, что вакансия принадлежит текущему работодателю
    if application.vacancy.employer_id != current_user.id:
        flash('Доступ запрещен')
        return redirect(url_for('employer.dashboard'))

    new_status = request.form.get('status')
    rejection_reason = request.form.get('rejection_reason', '').strip()

    # Проверяем, что при отклонении указана причина
    if new_status == 'rejected' and not rejection_reason:
        flash('При отклонении заявки необходимо указать причину отказа')
        return redirect(url_for('employer.view_application', application_id=application_id))

    if new_status in ['pending', 'reviewed', 'accepted', 'rejected']:
        application.status = new_status

        # Сохраняем причину отказа только при статусе rejected
        if new_status == 'rejected':
            application.rejection_reason = rejection_reason
        else:
            application.rejection_reason = None

        db.session.commit()

        if new_status == 'rejected':
            flash(f'Отклик отклонен. Причина: {rejection_reason}')
        else:
            flash(f'Статус отклика изменен на: {new_status}')

    return redirect(url_for('employer.view_application', application_id=application_id))


@employer.route('/employer/application/<int:application_id>')
@login_required
def view_application(application_id):
    if current_user.role != 'employer':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    application = db.session.get(Application, application_id)
    if not application:
        flash('Заявка не найдена')
        return redirect(url_for('employer.dashboard'))

    # Проверяем, что заявка относится к вакансии текущего работодателя
    if application.vacancy.employer_id != current_user.id:
        flash('Доступ запрещен')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/application_view.html', application=application)