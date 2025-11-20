from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Portfolio, Vacancy, Application, User, Company, db

seeker = Blueprint('seeker', __name__)


@seeker.route('/seeker/dashboard')
@login_required
def dashboard():
    if current_user.role != 'seeker':
        flash('Доступ запрещен')
        return redirect(url_for('index'))

    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    applications = Application.query.filter_by(seeker_id=current_user.id).all()

    return render_template('seeker/dashboard.html',
                           portfolio=portfolio,
                           applications=applications)


@seeker.route('/seeker/portfolio/edit', methods=['GET', 'POST'])
@login_required
def edit_portfolio():
    if current_user.role != 'seeker':
        return redirect(url_for('index'))

    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        if not portfolio:
            portfolio = Portfolio(user_id=current_user.id)
            db.session.add(portfolio)

        portfolio.title = request.form.get('title')
        portfolio.profession = request.form.get('profession')
        portfolio.bio = request.form.get('bio')
        portfolio.skills = request.form.get('skills')
        portfolio.experience_years = request.form.get('experience_years')
        portfolio.education = request.form.get('education')
        portfolio.projects = request.form.get('projects')
        portfolio.contact_info = request.form.get('contact_info')
        portfolio.is_public = True if request.form.get('is_public') else False
        # Сбрасываем статус модерации при редактировании
        portfolio.is_approved = False

        db.session.commit()
        flash('Портфолио обновлено и отправлено на модерацию')
        return redirect(url_for('seeker.dashboard'))

    return render_template('seeker/edit_portfolio.html', portfolio=portfolio)


@seeker.route('/vacancies')
def vacancies():
    # Получаем параметры поиска и фильтрации
    search = request.args.get('search', '')
    experience = request.args.get('experience', '')
    employment_type = request.args.get('employment_type', '')
    salary_min = request.args.get('salary_min', '')

    # Показываем только активные и одобренные вакансии
    query = Vacancy.query.filter_by(is_active=True, is_approved=True)

    # Применяем фильтры
    if search:
        query = query.filter(
            (Vacancy.title.contains(search)) |
            (Vacancy.description.contains(search)) |
            (Company.company_name.contains(search))
        ).join(Company)

    if experience and experience != 'all':
        query = query.filter(Vacancy.experience_level == experience)

    if employment_type and employment_type != 'all':
        query = query.filter(Vacancy.employment_type == employment_type)

    if salary_min:
        query = query.filter(Vacancy.salary_max >= int(salary_min))

    # Сортировка
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'salary_high':
        query = query.order_by(Vacancy.salary_max.desc())
    elif sort_by == 'salary_low':
        query = query.order_by(Vacancy.salary_max.asc())
    else:  # newest
        query = query.order_by(Vacancy.created_at.desc())

    vacancies = query.all()

    return render_template('seeker/vacancies.html',
                           vacancies=vacancies,
                           search=search,
                           experience=experience,
                           employment_type=employment_type,
                           salary_min=salary_min,
                           sort=sort_by)


@seeker.route('/seeker/apply/<int:vacancy_id>', methods=['POST'])
@login_required
def apply(vacancy_id):
    if current_user.role != 'seeker':
        return redirect(url_for('index'))

    vacancy = db.session.get(Vacancy, vacancy_id)
    if not vacancy:
        flash('Вакансия не найдена')
        return redirect(url_for('seeker.vacancies'))

    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()

    if not portfolio:
        flash('Сначала создайте портфолио')
        return redirect(url_for('seeker.edit_portfolio'))

    # Проверяем, не откликался ли уже
    existing_application = Application.query.filter_by(
        vacancy_id=vacancy_id,
        seeker_id=current_user.id
    ).first()

    if existing_application:
        flash('Вы уже откликались на эту вакансию')
        return redirect(url_for('seeker.vacancies'))

    application = Application(
        vacancy_id=vacancy_id,
        seeker_id=current_user.id,
        portfolio_id=portfolio.id,
        cover_letter=request.form.get('cover_letter')
    )

    db.session.add(application)
    db.session.commit()

    flash('Отклик отправлен успешно!')
    return redirect(url_for('seeker.dashboard'))