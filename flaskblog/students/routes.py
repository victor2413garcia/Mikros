from datetime import datetime
import random
from flask_login import current_user, login_required
from flask import render_template, request, Blueprint, url_for, flash
from flaskblog import db
from flaskblog.students.forms import ResponseCellForm, ResponseMicroForm
from flaskblog.models import (Class, ClassList, Class, Professor, User, Student, Evaluation,
							 Assignations, Microphoto, AssignResponses, BgType, FloraType,
							 CellType, MorphCyto, ColorCyto, MorphCore, SizeCore, ChromatinCore,
							 Cell, Responses, CorrectionCell, CorrectionRes, University)

students = Blueprint('students', __name__)


@students.route("/student/classes/", methods=['GET', 'POST'])
@login_required
def classes():
	posts=[]
	inactivos=0
	st = Student.query.filter_by(user_id=current_user.id).first_or_404()
	lista = current_user.students.classes
	for i in lista:
		print(i.id)
		clase=Class.query.filter_by(id=i.class_id).first()
		inac = Class.query.filter_by(active=False, id=i.id).first()
		if inac:
			inactivos +=1
		prof=Professor.query.filter_by(id=clase.professor_id).first()
		prof=User.query.filter_by(id=prof.user_id).first()
		posts.append([clase, prof])
	return render_template('student_classes.html', posts=posts, laystudents=True, inactivos=inactivos)

@students.route('/student/classes/<int:class_id>', methods=['GET', 'POST'])
@login_required
def dashboard_class(class_id):
	st = Student.query.filter_by(user_id=current_user.id).first_or_404()
	class_d = Class.query.get_or_404(class_id)
	prof = Professor.query.filter_by(id=class_d.professor_id).first()
	prof = User.query.filter_by(id=prof.user_id).first()
	evals = Evaluation.query.filter_by(evaluations=class_d).order_by(Evaluation.date_delivered.desc()).all()
	is_expired = []
	backgr=url_for('static', filename='backgrounds/' + 'fondo.jpg')
	for ev in evals:
		now=datetime.utcnow()
		end=ev.date_limit
		if now > end:
			is_expired.append(True)
		else:
			is_expired.append(False)
	return render_template('student_class.html', class_d=class_d, evals=evals, is_expired=is_expired, backgr=backgr, prof=prof, spacing=True)

@students.route("/student/classes/eval/<int:eval_id>", methods=['GET', 'POST'])
@login_required
def dashboard_eval(eval_id):
	evaluation = Evaluation.query.get_or_404(eval_id)
	microphotos = Microphoto.query.filter_by(evaluation_id=eval_id).all()
	student = Student.query.filter_by(user_id=current_user.id).first_or_404()
	materia = Class.query.filter_by(id=evaluation.class_id).first()
	materia = materia.name
	backgr=url_for('static', filename='backgrounds/' + 'fondo.jpg')
	assign_list = []
	for photo in microphotos:
		assign = Assignations.query.filter_by(student_id=student.id, microphoto_id=photo.id).first()
		if assign:
			assign_list.append(assign)
	return render_template('student_evaluation.html',eval_id=eval_id, student_id=student.id, materia=materia, spacing=True, backgr=backgr, evaluation=evaluation, assign_list=assign_list)

@students.route("/student/classes/eval/assign/<int:assign_id>", methods=['GET', 'POST'])
@login_required
def dashboard_assign(assign_id):
	form = ResponseCellForm()
	form_t = ResponseMicroForm()
	st = Student.query.filter_by(user_id=current_user.id).first_or_404()
	assign = Assignations.query.filter_by(id=assign_id).first_or_404()

	#micro formulario
	micro_response = False
	seleccione = (0, "Seleccione una opción")
	opciones_backgr = [(tipo.id, tipo.name) for tipo in BgType.query.all()]
	opciones_backgr.insert(0, seleccione)
	form_t.backgr_type.choices = opciones_backgr
	opciones_flora = [(tipo.id, tipo.name) for tipo in FloraType.query.all()]
	opciones_flora.insert(0, seleccione)
	form_t.flora_type.choices = opciones_flora

	#celula formulario
	opciones_tipo = [(tipo.id, tipo.name) for tipo in CellType.query.all()]
	opciones_tipo.insert(0, seleccione)
	form.cell_type.choices = opciones_tipo
	opciones_morph_cyto = [(tipo.id, tipo.name) for tipo in MorphCyto.query.all()]
	opciones_morph_cyto.insert(0, seleccione)
	form.cyto_morph.choices = opciones_morph_cyto
	opciones_size_cyto = [(tipo.id, tipo.name) for tipo in SizeCore.query.all()]
	opciones_size_cyto.insert(0, seleccione)
	form.cyto_size.choices = opciones_size_cyto
	opciones_color_cyto = [(tipo.id, tipo.name) for tipo in ColorCyto.query.all()]
	opciones_color_cyto.insert(0, seleccione)
	form.cyto_color.choices = opciones_color_cyto

	opciones_morph_core = [(tipo.id, tipo.name) for tipo in MorphCore.query.all()]
	opciones_morph_core.insert(0, seleccione)
	form.core_morph.choices = opciones_morph_core
	opciones_size_core = [(tipo.id, tipo.name) for tipo in SizeCore.query.all()]
	opciones_size_core.insert(0, seleccione)
	form.core_size.choices = opciones_size_core
	opciones_chromatin_core = [(tipo.id, tipo.name) for tipo in ChromatinCore.query.all()]
	opciones_chromatin_core.insert(0, seleccione)
	form.core_chroma.choices = opciones_chromatin_core
	is_form_one=False

	if form.validate_on_submit():
		is_form_one=True
		cell = Cell(cell_type_id=form.cell_type.data, morph_cyto_id=form.cyto_morph.data, size_cyto_id=form.cyto_size.data, color_cyto_id=form.cyto_color.data, morph_core_id=form.core_morph.data, size_core_id=form.core_size.data, chromatin_core_id=form.core_chroma.data)
		db.session.add(cell)
		db.session.commit()
		last_cell = Cell.query.order_by(Cell.id.desc()).first()
		response = Responses(assignations_id=assign_id, cell_id=last_cell.id)
		db.session.add(response)
		db.session.commit()
		flash('¡Respuestas de Celula enviadas!', 'success')

	if not is_form_one:
		if form_t.validate_on_submit():
			micro = AssignResponses(assignations_id=assign.id, bg_type_id=form_t.backgr_type.data, flora_type_id=form_t.flora_type.data, cell_predominance=form_t.cell_predominance.data)
			db.session.add(micro)
			db.session.commit()
			flash('¡Respuestas de Microfoto enviadas!', 'success')

	is_response_micro = AssignResponses.query.filter_by(assignations_id=assign.id).first()
	micro_list=[]
	if is_response_micro:
		micro_response=True
		bgtype = BgType.query.filter_by(id=is_response_micro.bg_type_id).first()
		floratype = FloraType.query.filter_by(id=is_response_micro.flora_type_id).first()

		micro_list.append(bgtype.name)
		micro_list.append(floratype.name)
		micro_list.append(is_response_micro.cell_predominance)
	else:
		micro_response = False
		seleccione = (0, "Seleccione una opción")
		opciones_backgr = [(tipo.id, tipo.name) for tipo in BgType.query.all()]
		opciones_backgr.insert(0, seleccione)
		form_t.backgr_type.choices = opciones_backgr
		opciones_flora = [(tipo.id, tipo.name) for tipo in FloraType.query.all()]
		opciones_flora.insert(0, seleccione)
		form_t.flora_type.choices = opciones_flora

	photo = Microphoto.query.filter_by(id=assign.microphoto_id).first()
	photo_i=[url_for('static', filename='micro_pics/' + photo.image_file)]

	cells = Responses.query.filter_by(assignations_id=assign_id).all()
	cell_other_for=[]
	for i in cells:
		cell_for = Cell.query.filter_by(id=i.cell_id).first()
		cell_other_for.append(cell_for)
	cell_list=[]
	for cell in cell_other_for:
		cell_type = CellType.query.filter_by(id=cell.cell_type_id).first()
		cell_type = cell_type.name
		cyto_morph = MorphCyto.query.filter_by(id=cell.morph_cyto_id).first()
		cyto_morph = cyto_morph.name
		cyto_size = SizeCore.query.filter_by(id=cell.size_cyto_id).first()
		cyto_size = cyto_size.name
		cyto_color = ColorCyto.query.filter_by(id=cell.color_cyto_id).first()
		cyto_color = cyto_color.name
		core_morph = MorphCore.query.filter_by(id=cell.morph_core_id).first()
		core_morph = core_morph.name
		core_size = SizeCore.query.filter_by(id=cell.size_core_id).first()
		core_size = core_size.name
		core_chroma = ChromatinCore.query.filter_by(id=cell.chromatin_core_id).first()
		core_chroma = core_chroma.name
		cell_list.append([cell_type, cyto_morph, cyto_size, cyto_color, core_morph, core_size, core_chroma])
	ev = Evaluation.query.filter_by(id=photo.evaluation_id).first()
	now=datetime.utcnow()
	end=ev.date_limit
	is_expired=False
	if now > end:
		is_expired = False
	else:
		is_expired = True
	return render_template('student_assign.html', micro_list=micro_list, is_expired=is_expired, myprofile=True, cell_list=cell_list, micro_response=micro_response, form_t=form_t, form=form, assign=assign, photo=photo_i)

@students.route("/student/classes/eval/view/<int:eval_id><int:student_id>", methods=['GET', 'POST'])
@login_required
def dashboard_view(eval_id, student_id):
	eval_i = Evaluation.query.get_or_404(eval_id)
	clase = Class.query.filter_by(id=eval_i.class_id).first_or_404()
	corregido=False
	foto_id=0
	microphotos = Microphoto.query.filter_by(evaluation_id=eval_id).all()
	st = Student.query.filter_by(user_id=current_user.id).first()
	assign_list = []
	for photo in microphotos:
		assign = Assignations.query.filter_by(student_id=st.id, microphoto_id=photo.id).first()
		if assign:
			foto_id=photo.id
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
	
	ass = Assignations.query.filter_by(student_id=student_id, microphoto_id=foto_id).first()
	nota = ass.grade
	observacion = ass.observation
	return render_template('correction.html',nota=nota, observacion=observacion, student=True, corregido=corregido, evaluation=assign_list, rosa=True)

@students.route("/student/grades/", methods=['GET', 'POST'])
@login_required
def dashboard_grades():
	st = Student.query.filter_by(user_id=current_user.id).first_or_404()
	uni=University.query.get(current_user.university_id)
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	classes = ClassList.query.filter_by(student_id=st.id).all()
	class_list=[]
	gr=[]
	for class_ in classes:
		gr=[]
		if class_:
			cl = Class.query.filter_by(id=class_.class_id).first()
			if cl:
				evs = Evaluation.query.filter_by(class_id=cl.id).all()
				if evs:
					for ev in evs:
						mcs = Microphoto.query.filter_by(evaluation_id=ev.id).all()
						if mcs:
							for mc in mcs:
								g = Assignations.query.filter_by(microphoto_id=mc.id).first()
								if g:
									gr.append(g.grade)
			class_list.append([cl, gr])
	print(class_list)
	return render_template('grades.html', class_list=class_list, uni=uni, image_file=image_file)

@students.route("/student/profs/", methods=['GET', 'POST'])
@login_required
def dashboard_professors():
	st = Student.query.filter_by(user_id=current_user.id).first_or_404()
	lista = current_user.students.classes
	profs=[]
	for i in lista:
		clase=Class.query.filter_by(id=i.class_id).first()
		prof=Professor.query.filter_by(id=clase.professor_id).first()
		prof=User.query.filter_by(id=prof.user_id).first()
		image_file = url_for('static', filename='profile_pics/' + prof.image_file)
		profs.append([prof, image_file, clase])
	return render_template('professors.html', profs=profs)