// Анимация появления элементов при скролле
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Инициализация анимаций
document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления элементов
    document.querySelectorAll('.card, .btn, .navbar-brand, .search-form').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Анимация кнопок при наведении
    const buttons = document.querySelectorAll('.btn, .card');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function(e) {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        button.addEventListener('mouseleave', function(e) {
            if (!this.classList.contains('hover-scale')) {
                this.style.transform = 'translateY(0) scale(1)';
            }
        });
    });

    // Анимация поиска при фокусе
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.05)';
        });
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }

    // Анимация фона на главной странице
    const hero = document.querySelector('.hero-section');
    if (hero) {
        let position = 0;
        setInterval(() => {
            position = (position + 0.5) % 100;
            hero.style.backgroundPosition = `${position}% ${position}%`;
        }, 100);
    }

    // Анимация хлебных крошек
    const breadcrumbs = document.querySelectorAll('.breadcrumb-item');
    breadcrumbs.forEach((crumb, index) => {
        crumb.style.animationDelay = `${index * 0.1}s`;
    });

    // Автоматическое скрытие flash сообщений
    const alerts = document.querySelectorAll('.alert-custom');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Плавная прокрутка для якорей
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Функция для анимации поиска
function animateSearch() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.style.transform = 'scale(0.95)';
        setTimeout(() => {
            searchForm.style.transform = 'scale(1)';
        }, 150);
    }
}

// Улучшение анимации воды
function enhanceWaterEffect() {
    const hero = document.querySelector('.hero-section');
    if (!hero) return;

    // Добавляем интерактивность при наведении
    hero.addEventListener('mouseenter', function() {
        this.style.animationDuration = '12s';
    });

    hero.addEventListener('mouseleave', function() {
        this.style.animationDuration = '18s';
    });

    // Периодическое изменение скорости для естественности
    setInterval(() => {
        const durations = ['16s', '18s', '20s'];
        const randomDuration = durations[Math.floor(Math.random() * durations.length)];
        hero.style.animationDuration = randomDuration;
    }, 30000);
}

// Анимация для кнопок с переливанием
function initAdminButtonAnimations() {
    const adminButtons = document.querySelectorAll('.btn-admin-pulse');

    adminButtons.forEach((button, index) => {
        // Добавляем задержку для каждой кнопки для создания волнового эффекта
        button.style.animationDelay = `${index * 0.3}s`;

        // Улучшаем анимацию при наведении
        button.addEventListener('mouseenter', function() {
            this.style.animationDuration = '4s';
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.animationDuration = '8s';
            this.style.transform = 'translateY(0) scale(1)';
        });

        // Добавляем эффект клика
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(1px) scale(0.98)';
        });

        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
    });
}

// Обновляем DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // ... существующий код ...

    initButtonAnimations();
    initAdminButtonAnimations();
    enhanceWaterEffect();
});