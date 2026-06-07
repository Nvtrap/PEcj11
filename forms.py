"""Формы Flask-WTF с валидацией."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp


class ContactForm(FlaskForm):
    """Форма обратной связи на публичной части сайта."""

    name = StringField(
        "Имя",
        validators=[
            DataRequired(message="Укажите имя"),
            Length(min=2, max=120, message="Имя: от 2 до 120 символов"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Укажите email"),
            Email(message="Некорректный email"),
            Length(max=120),
        ],
    )
    phone = StringField(
        "Телефон",
        validators=[
            DataRequired(message="Укажите телефон"),
            Length(min=7, max=30, message="Телефон: от 7 до 30 символов"),
            Regexp(
                r"^[\d\s\+\-\(\)]+$",
                message="Телефон может содержать только цифры, +, -, (, )",
            ),
        ],
    )
    subject = StringField(
        "Тема сообщения",
        validators=[
            DataRequired(message="Укажите тему"),
            Length(min=3, max=200, message="Тема: от 3 до 200 символов"),
        ],
    )
    submit = SubmitField("Отправить")


class LoginForm(FlaskForm):
    """Форма входа в админ-панель."""

    username = StringField(
        "Логин",
        validators=[
            DataRequired(message="Введите логин"),
            Length(min=3, max=80),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введите пароль"),
            Length(min=4, max=128),
        ],
    )
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")
