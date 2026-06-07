"""
Точка входа Flask-приложения.
Запуск: python app.py
"""

import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import desc

import config
from cases_data import CASES, get_case_by_slug
from forms import ContactForm, LoginForm
from models import Admin, ContactRequest, db

load_dotenv()

# --- Инициализация приложения ---

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"
login_manager.login_message = "Войдите в систему для доступа к админ-панели."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id: str) -> Admin | None:
    return db.session.get(Admin, int(user_id))


@app.context_processor
def inject_globals():
    """Глобальные переменные для шаблонов."""
    from datetime import datetime

    return {
        "current_year": datetime.now().year,
        "chat_api_url": config.CHAT_API_URL,
    }


def setup_logging() -> None:
    """Настройка логирования в файл и консоль."""
    if not app.debug:
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)


def init_db() -> None:
    """Создание таблиц и администратора по умолчанию."""
    with app.app_context():
        db.create_all()
        admin = Admin.query.filter_by(username=config.ADMIN_USERNAME).first()
        if not admin:
            admin = Admin(username=config.ADMIN_USERNAME)
            admin.set_password(config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Создан администратор: %s", config.ADMIN_USERNAME)


# --- Публичные маршруты ---


@app.route("/")
def index():
    """Главная страница с hero-блоком и превью кейсов."""
    return render_template("index.html", cases=CASES)


@app.route("/cases")
def cases_list():
    """Страница со всеми кейсами."""
    return render_template("cases.html", cases=CASES)


@app.route("/cases/<slug>")
def case_detail(slug: str):
    """Детальная страница кейса."""
    case = get_case_by_slug(slug)
    if not case:
        flash("Кейс не найден.", "warning")
        return redirect(url_for("cases_list"))
    return render_template("case_detail.html", case=case)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Форма обратной связи."""
    form = ContactForm()
    if form.validate_on_submit():
        contact_req = ContactRequest(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            subject=form.subject.data.strip(),
        )
        db.session.add(contact_req)
        db.session.commit()
        app.logger.info(
            "Новая заявка #%s от %s (%s)",
            contact_req.id,
            contact_req.name,
            contact_req.email,
        )
        flash("Спасибо! Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", form=form)


# --- Админ-панель ---


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Авторизация администратора."""
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data.strip()).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember.data)
            app.logger.info("Вход администратора: %s", admin.username)
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("admin_dashboard"))
        flash("Неверный логин или пароль.", "danger")
        app.logger.warning("Неудачная попытка входа: %s", form.username.data)

    return render_template("admin/login.html", form=form)


@app.route("/admin/logout")
@login_required
def admin_logout():
    """Выход из админ-панели."""
    app.logger.info("Выход администратора: %s", current_user.username)
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    """Таблица всех заявок."""
    requests_list = ContactRequest.query.order_by(desc(ContactRequest.created_at)).all()
    return render_template("admin/dashboard.html", requests=requests_list)


@app.route("/admin/request/<int:request_id>/read", methods=["POST"])
@login_required
def admin_mark_read(request_id: int):
    """Отметить заявку как прочитанную."""
    contact_req = db.session.get(ContactRequest, request_id)
    if contact_req:
        contact_req.is_read = True
        db.session.commit()
        app.logger.info("Заявка #%s отмечена прочитанной", request_id)
        flash(f"Заявка #{request_id} отмечена как прочитанная.", "success")
    else:
        flash("Заявка не найдена.", "warning")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/request/<int:request_id>/unread", methods=["POST"])
@login_required
def admin_mark_unread(request_id: int):
    """Снять отметку «прочитано»."""
    contact_req = db.session.get(ContactRequest, request_id)
    if contact_req:
        contact_req.is_read = False
        db.session.commit()
        app.logger.info("Заявка #%s отмечена непрочитанной", request_id)
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/request/<int:request_id>/delete", methods=["POST"])
@login_required
def admin_delete_request(request_id: int):
    """Удаление заявки."""
    contact_req = db.session.get(ContactRequest, request_id)
    if contact_req:
        db.session.delete(contact_req)
        db.session.commit()
        app.logger.info("Заявка #%s удалена", request_id)
        flash(f"Заявка #{request_id} удалена.", "info")
    else:
        flash("Заявка не найдена.", "warning")
    return redirect(url_for("admin_dashboard"))


# --- Обработчики ошибок ---


@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html"), 500


# --- Запуск ---

setup_logging()
init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
