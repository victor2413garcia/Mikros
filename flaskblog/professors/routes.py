from datetime import datetime
import random
from flask import (render_template, url_for, flash,
				   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import (Class, Professor, Evaluation, Microphoto, InvitationLink,
							 ClassList, Student, User, Assignations, Responses, Cell, CellType,
							 MorphCyto, SizeCore, ColorCyto, MorphCore, ChromatinCore, AssignResponses,
							 BgType, FloraType, CorrectionCell, CorrectionRes)
from flaskblog.professors.forms import ClassForm, EvaluationForm, dynamic_form, CorrectionForm, GradeForm
from flaskblog.professors.utils import save_picture, generate_link, check_status, search

# Modulo de Profesor
professors = Blueprint('professors', __name__)


@professors.route("/professor/classes/", methods=['GET', 'POST'])
@login_required
def classes():
	form = ClassForm()
	prof= Professor.query.filter_by(user_id=current_user.id).first_or_404()
	posts = Class.query.filter_by(subjects=prof).order_by(Class.date_posted.desc()).all()
	inactivos = Class.query.filter_by(active=False, subjects=prof).count()
	if form.validate_on_submit():
		prof = Professor.query.filter_by(user_id=current_user.id).first_or_404()
		class_add = Class(name=form.name.data, description=form.description.data, period=form.quarter.data, subjects=prof)
		db.session.add(class_add)
		db.session.commit()
		page_num = Class.query.filter_by(name=form.name.data).first()
		generate_link(page_num.id)

		flash('¡Clase creada exitosamente!', 'success')
		posts = Class.query.filter_by(subjects=prof).order_by(Class.date_posted.desc()).all()
		redirect(url_for('professors.classes'))
	return render_template('classes.html', layout=True, inactivos=inactivos, posts=posts, title='Mis Clases', form=form, legend='Crear Clase')


@professors.route("/professor/classes/<int:class_id>", methods=['GET', 'POST'])
@login_required
def dashboard_class(class_id):
	form=EvaluationForm()
	backgr=url_for('static', filename='backgrounds/' + 'fondo.jpg')
	edit_c=ClassForm()
	class_d = Class.query.get_or_404(class_id)
	prof = Professor.query.filter_by(user_id=current_user.id).first_or_404()
	if class_d.professor_id != prof.id:
		abort(403)
	evals = Evaluation.query.filter_by(evaluations=class_d).order_by(Evaluation.date_delivered.desc()).all()
	inv_link = InvitationLink.query.filter_by(invlink=class_d).first_or_404()
	inv_link = inv_link.link
	port = request.host
	is_expired = []
	students=[]
	c_list = ClassList.query.filter_by(class_id=class_id).all()
	for ids in c_list:
		st = Student.query.filter_by(id=ids.student_id).first()
		st = User.query.filter_by(students=st).first()
		students.append(st)

	for ev in evals:
		now=datetime.utcnow()
		end=ev.date_limit
		if now > end:
			is_expired.append(True)
		else:
			is_expired.append(False)
	if form.validate_on_submit():
		evals_add = Evaluation(name=form.title.data, description=form.description.data, date_limit=form.date_limit.data, evaluations=class_d)
		db.session.add(evals_add)
		db.session.commit()
		evalu = Evaluation.query.filter_by(name=form.title.data).first_or_404()
		data = form.picture.data
		picture = save_picture(data, evalu)
		flash('¡Evaluacion creada exitosamente!', 'success')
		evals = Evaluation.query.filter_by(evaluations=class_d).order_by(Evaluation.date_delivered.desc()).all()
		for ev in evals:
			now=datetime.utcnow()
			end=ev.date_limit
			if now > end:
				is_expired.append(True)
			else:
				is_expired.append(False)
		redirect(url_for('professors.dashboard_class', class_id=class_id))
	if edit_c.validate_on_submit():
		class_d.name=edit_c.name.data
		class_d.period=edit_c.quarter.data
		class_d.description=edit_c.description.data
		db.session.commit()
	elif request.method == 'GET':
		edit_c.name.data=class_d.name
		edit_c.quarter.data=class_d.period
		edit_c.description.data=class_d.description
	return render_template('class.html', class_id=class_id, backgr=backgr, students=students, port=port, inv_link=inv_link, edit_c=edit_c, is_expired=is_expired, legend="Nueva Evaluación", form=form, spacing=True, evals=evals, title=class_d.name, class_d=class_d)

@professors.route("/professor/classes/<int:class_id>/update", methods=['GET', 'POST'])
@login_required
def update_class(class_id):
	post = Class.query.get_or_404(class_id)
	if post.subjects.collaborator != current_user:
		abort(403)
	form = ClassForm()
	if form.validate_on_submit():
		post.name = form.name.data
		post.period = form.quarter.data
		post.description = form.description.data
		db.session.commit()
		flash('¡Tu clase ha sido actualizada!', 'success')
		return redirect(url_for('professors.dashboard_class', class_id=post.id))
	elif request.method == 'GET':
		form.name.data = post.name
		form.quarter.data = post.period
		form.description.data = post.description
	return render_template('classes.html', title='Mis Clases',
						   form=form, legend='Modificar Clase')


@professors.route("/professor/classes/eval/<int:eval_id>", methods=['GET', 'POST'])
@login_required
def dashboard_eval(eval_id):
	pr = Professor.query.filter_by(user_id=current_user.id).first_or_404()
	mic_ids=Microphoto.query.filter_by(evaluation_id=eval_id).all()
	form = dynamic_form(len(mic_ids))
	eval_i = Evaluation.query.get_or_404(eval_id)
	clase = Class.query.filter_by(id=eval_i.class_id).first_or_404()
	if clase.professor_id != pr.id:
		abort(403)
	students=[]
	c_list = ClassList.query.filter_by(class_id=eval_i.class_id).all()
	images = []
	for image in mic_ids:
		images.append(url_for('static', filename='micro_pics/' + image.image_file))
	backgr=url_for('static', filename='backgrounds/' + 'fondo.jpg')
	for ids in c_list:
		st = Student.query.filter_by(id=ids.student_id).first()
		status = check_status(st, mic_ids)
		st = User.query.filter_by(students=st).first()
		students.append([st, status])
	if form.validate_on_submit():
		for i, field_name in enumerate(form.field_names):
			field_value = request.form.get(field_name)
			if field_value == 'y':
				st = Student.query.filter_by(user_id=form.student_id.data).first()
				asignar=Assignations(microphoto_id=int(str(mic_ids[i])), student_id=st.id)
				db.session.add(asignar)
				db.session.commit()
				flash('¡Microfotos asignadas!','success')
		students=[]
		for ids in c_list:
			st = Student.query.filter_by(id=ids.student_id).first()
			status = check_status(st, mic_ids)
			st = User.query.filter_by(students=st).first()
			students.append([st, status])
	port = request.host

	return render_template('evaluation.html', port=port, spacing=True, backgr=backgr, form=form, images=images, eval_i=eval_i, students=students)

@professors.route("/professor/classes/<int:class_id>/delete", methods=['POST', 'GET'])
@login_required
def delete_class(class_id):
	post = Class.query.get_or_404(class_id)
	if post.subjects.collaborator != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('!Tu clase ha sido eliminada!', 'success')
	return redirect(url_for('professors.classes'))

@professors.route("/professor/classes/eval/<int:eval_id>/delete", methods=['POST', 'GET'])
@login_required
def delete_eval(eval_id):
	post = Evaluation.query.get_or_404(eval_id)
	prof = Class.query.filter_by(id=post.class_id).first()
	if prof.subjects.collaborator != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('!Tu evaluación ha sido eliminada!', 'success')
	return redirect(url_for('professors.dashboard_class', class_id=prof.id))

@professors.route("/invitation/<string:inv_link>", methods=['GET', 'POST'])
@login_required
def invitation(inv_link):
	link = InvitationLink.query.filter_by(link=inv_link).first_or_404()
	student_id = Student.query.filter_by(member=current_user).first_or_404()
	student_id = student_id.id
	add = ClassList(class_id=link.classes, student_id=student_id)
	db.session.add(add)
	db.session.commit()
	flash('¡Has sido invitado a esta clase!','success')
	return(redirect(url_for('students.classes')))

@professors.route("/professor/classes/eval/correction/<int:eval_id><int:student_id>", methods=['GET', 'POST'])
@login_required
def correction(eval_id, student_id):
	form=GradeForm()
	pr = Professor.query.filter_by(user_id=current_user.id).first_or_404()
	eval_i = Evaluation.query.get_or_404(eval_id)
	clase = Class.query.filter_by(id=eval_i.class_id).first_or_404()
	corregido=False
	foto_id=0
	if clase.professor_id != pr.id:
		abort(403)
	microphotos = Microphoto.query.filter_by(evaluation_id=eval_id).all()
	st = Student.query.filter_by(user_id=student_id).first()
	assign_list = []
	for photo in microphotos:
		assign = Assignations.query.filter_by(student_id=st.id, microphoto_id=photo.id).first()
		if assign:
			if assign.grade:
				corregido=True

			photo = Microphoto.query.filter_by(id=assign.microphoto_id).first()
			photo_i=[url_for('static', filename='micro_pics/' + photo.image_file)]
			cells = Responses.query.filter_by(assignations_id=assign.id).all()
			cell_other_for=[]
			for i in cells:
				cell_for = Cell.query.filter_by(id=i.cell_id).first()
				correct = CorrectionCell.query.filter_by(cell=i.cell_id).first()
				cell_other_for.append([cell_for, correct])
			cell_list=[]
			for cell in cell_other_for:
				cell = cell[0]
				cell_type = CellType.query.filter_by(id=cell.cell_type_id).first()
				cell_type = [cell_type.name, correct.cell_type]
				cyto_morph = MorphCyto.query.filter_by(id=cell.morph_cyto_id).first()
				cyto_morph = [cyto_morph.name, correct.morph_cyto]
				cyto_size = SizeCore.query.filter_by(id=cell.size_cyto_id).first()
				cyto_size = [cyto_size.name, correct.size_cyto]
				cyto_color = ColorCyto.query.filter_by(id=cell.color_cyto_id).first()
				cyto_color = [cyto_color.name, correct.color_cyto]
				core_morph = MorphCore.query.filter_by(id=cell.morph_core_id).first()
				core_morph = [core_morph.name, correct.morph_core]
				core_size = SizeCore.query.filter_by(id=cell.size_core_id).first()
				core_size = [core_size.name, correct.size_core]
				core_chroma = ChromatinCore.query.filter_by(id=cell.chromatin_core_id).first()
				core_chroma = [core_chroma.name, correct.chromatin_core]
				cell_list.append([cell_type, cyto_morph, cyto_size, cyto_color, core_morph, core_size, core_chroma, cell.id])
			is_response_micro = AssignResponses.query.filter_by(assignations_id=assign.id).first()
			micro_list=[]
			if is_response_micro:
				micro_response=True
				bgtype = BgType.query.filter_by(id=is_response_micro.bg_type_id).first()
				floratype = FloraType.query.filter_by(id=is_response_micro.flora_type_id).first()
				correct = CorrectionRes.query.filter_by(responses=is_response_micro.id).first()

				micro_list.append([bgtype.name, correct.bg_type])
				micro_list.append([floratype.name, correct.flora_type])
				micro_list.append([is_response_micro.cell_predominance, correct.cell_predominance])
			num = random.random()
			num_t = random.random()
			assign_list.append([photo_i, assign, [num, cell_list], [num_t, micro_list]])
	if form.validate_on_submit():
		for photo in microphotos:
			assign = Assignations.query.filter_by(student_id=st.id, microphoto_id=photo.id).first()
			if assign:
				foto_id=photo.id
				break
		ass = Assignations.query.filter_by(student_id=st.id, microphoto_id=foto_id).first()
		ass.grade = form.grade.data
		ass.observation = form.observation.data
		db.session.add(ass)
		db.session.commit()
	elif request.method == 'GET':
		for photo in microphotos:
			assign = Assignations.query.filter_by(student_id=st.id, microphoto_id=photo.id).first()
			if assign:
				foto_id=photo.id
				break
		ass = Assignations.query.filter_by(student_id=st.id, microphoto_id=foto_id).first()
		form.grade.data = ass.grade
		form.observation.data = ass.observation
	return render_template('correction.html',form=form, corregido=corregido, evaluation=assign_list, rosa=True)

@professors.route("/professor/classes/eval/correct/<int:eval_id><int:student_id>", methods=['GET', 'POST'])
@login_required
def correct(eval_id, student_id):
	form = CorrectionForm()
	pr = Professor.query.filter_by(user_id=current_user.id).first_or_404()
	eval_i = Evaluation.query.get_or_404(eval_id)
	clase = Class.query.filter_by(id=eval_i.class_id).first_or_404()
	if clase.professor_id != pr.id:
		abort(403)
	assign_list=search(eval_id, student_id)
	if type(assign_list) != list:
		return redirect(url_for('professors.correction', eval_id=eval_id, student_id=student_id))
	if form.validate_on_submit():
		assign_list=search(eval_id, student_id)
		if type(assign_list) != list:
			return redirect(url_for('professors.correction', eval_id=eval_id, student_id=student_id))
		cor_cell = CorrectionCell(cell=form.cell_id.data ,cell_type=form.cell_type.data ,morph_cyto=form.morph_cyto.data ,size_cyto=form.size_cyto.data ,color_cyto=form.color_cyto.data ,morph_core=form.morph_core.data ,size_core=form.size_core.data ,chromatin_core=form.chromatin_core.data)
		db.session.add(cor_cell)
		ass=AssignResponses.query.filter_by(assignations_id=int(form.assign_id.data)).first()
		if not ass.correction:
			cor_micro = CorrectionRes(bg_type= form.bg_type.data ,flora_type=form.flora_type.data ,cell_predominance=form.cell_predominance.data, responses=ass.id)
			db.session.add(cor_micro)
		db.session.commit()
		flash('Celula corregida exitosamente','success')
	return render_template("correct.html",form=form, evaluation=assign_list, some=True, rosa=True)

@professors.route("/professor/studs/", methods=['GET', 'POST'])
@login_required
def dashboard_students():
	prof = Professor.query.filter_by(user_id=current_user.id).first()
	students_list=[]
	for class_ in prof.classes:
		students=[]
		for member in class_.members:
			student = Student.query.filter_by(id=member.student_id).first()
			student = User.query.filter_by(id=student.user_id).first()
			students.append(student)
		students_list.append([class_, students])
	return render_template('students.html', students_list=students_list)

@professors.route("/professor/studs/<int:student_id><int:class_id>", methods=['GET', 'POST'])
@login_required
def student_grade(student_id, class_id):
	student = Student.query.filter_by(user_id=student_id).first()
	class_ = Class.query.filter_by(id=class_id).first()
	assigns=[]
	for evaluations in class_.evaluations:
		for micros in evaluations.images:
			assign=Assignations.query.filter_by(microphoto_id=micros.id, student_id=student.id).first()
			if assign:
				assigns.append([assign, evaluations])
	student=User.query.filter_by(id=student.user_id).first()
	image_file = url_for('static', filename='profile_pics/' + student.image_file)
	return render_template('student_grade.html', assigns=assigns, class_=class_, student=student, image_file=image_file)
