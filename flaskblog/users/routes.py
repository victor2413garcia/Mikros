from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, University, Professor, Student, Class
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    # Consultar la base de datos para obtener las opciones
    uni_db = University.query.all()
    
    # Tipos de usuarios
    user_t = [{'id' : 0, 'name' : 'Seleccione una opción'},{'id' : 1, 'name' : 'Estudiante'},{'id' : 2, 'name' : 'Profesor'}]
    # Generar las opciones para el campo SelectField
    op_uni = [(uni.id, uni.name) for uni in uni_db]
    op_user = [(user['id'], user['name']) for user in user_t]
    op_uni.insert(0, (0, 'Seleccione una opción'))
    
    # Establecer las opciones en el campo SelectField
    form.university.choices = op_uni
    form.user_type.choices = op_user

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(ci=form.ci.data ,name=form.name.data, lastname=form.lastname.data, email=form.email.data, telephone=form.phone.data, password=hashed_password, university_id=form.university.data)
        db.session.add(user)
        db.session.commit()
        if int(form.user_type.data) == 1:
            user_id = User.query.filter_by(ci=form.ci.data).first_or_404()
            user_type = Student(user_id=user_id.id)
        elif int(form.user_type.data) == 2:
            user_id = User.query.filter_by(ci=form.ci.data).first_or_404()
            user_type = Professor(user_id=user_id.id)
        db.session.add(user_type)
        db.session.commit()
        flash('¡Tu cuenta ha sido creada! Ahora puedes Iniciar Sesión', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Registrar', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(ci=form.ci.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.professors:
                return redirect(next_page) if next_page else redirect(url_for('professors.classes'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('students.classes'))
        else:
            flash('Inicio de Sesion fallido. Por favor chequea email y contraseña', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.ci = form.ci.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Tu cuenta ha sido actualizada!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.ci.data = current_user.ci
        form.email.data = current_user.email
        uni=University.query.get(current_user.university_id)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Cuenta',
                           image_file=image_file, uni=uni,form=form)

"""
@users.route("/user/<string:ci>")
def user_posts(ci):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(ci=ci).first_or_404()
    prof= Professor.query.filter_by(user_id=user.id).first_or_404()
    print(prof)
    posts = Class.query.filter_by(subjects=prof)\
        .order_by(Class.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)
    """


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Un Email ha sido enviado con instrucciones para recuperarlo.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Recuperar Contraseña', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token expirado o invalido', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Tu contraseña ha sido recuperada! Ahora puedes Iniciar Sesión', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Recuperar Contraseña', form=form)
