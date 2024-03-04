from flask import render_template, request, Blueprint, redirect, url_for
from flask_login import current_user
from flaskblog.models import Class

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
	if current_user.is_authenticated:
		if current_user.professors:
			redirect(url_for('professors.classes'))
		elif current_user.students:
			redirect(url_for('students.classes'))
	return render_template('home.html')


@main.route("/about")
def about():
    return render_template('about.html', title='About')
