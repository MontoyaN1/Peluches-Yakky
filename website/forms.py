from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, length, NumberRange


class SingUpForm(FlaskForm):
    email = EmailField("Correo", validators=[DataRequired()])
    username = StringField(
        "Nombre de usuario", validators=[DataRequired(), length(min=2)]
    )
    password1 = PasswordField(
        "Ingresa tu contraseña", validators=[DataRequired(), length(min=6)]
    )
    password2 = PasswordField(
        "Confirma tu contraseña", validators=[DataRequired(), length(min=6)]
    )
    submit = SubmitField("Crear")


class LoginForm(FlaskForm):
    email = EmailField("Correo", validators=[DataRequired()])
    password = PasswordField(
        "Ingresa tu contraseña", validators=[DataRequired(), length(min=6)]
    )
    submit = SubmitField("Ingresar")
