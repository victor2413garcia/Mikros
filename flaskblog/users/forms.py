from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, NoneOf
from flask_login import current_user
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    name = StringField('Nombre',
                        validators=[DataRequired()])
    lastname = StringField('Apellido',
                        validators=[DataRequired()])
    ci = IntegerField('Cedula de identidad',
                        validators=[DataRequired(), NumberRange(min=1000000, max=35000000)])
    university = SelectField('Universidad', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    user_type = SelectField('Tipo de usuario', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Telefono',
                        validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_ci(self, cedula):
        ci = User.query.filter_by(ci=cedula.data).first()
        if ci:
            raise ValidationError('Cedula ya registrada. ¡Inicie sesion!.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este correo ya ha sido registrado. Por favor elija uno diferente.')

class LoginForm(FlaskForm):
    ci = IntegerField('Cedula',
                        validators=[DataRequired(), NumberRange(min=1000000, max=35000000)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesion')


class UpdateAccountForm(FlaskForm):
    ci = IntegerField('Cedula',
                        validators=[DataRequired(), NumberRange(min=1000000, max=35000000)], render_kw={"readonly": True})
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Actualizar imagen de perfil', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Subir')

    def validate_ci(self, cedula):
        ci = User.query.filter_by(ci=cedula.data).first()
        if ci:
            raise ValidationError('Cedula ya registrada. ¡Inicie sesion!.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este correo ya ha sido registrado. Por favor elija uno diferente.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar cambio de Contraseña')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No existe una cuenta con este correo. Deber registrarte primero.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Recuperar Contraseña')
