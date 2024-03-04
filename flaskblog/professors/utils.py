import os
import secrets
import uuid
import random
from PIL import Image
from flask import url_for, current_app, request, redirect
from flaskblog.models import (Microphoto, InvitationLink, Assignations, Responses, CorrectionRes,
								Student, Cell, CellType, MorphCyto, SizeCore, ColorCyto, MorphCore,
								ChromatinCore, AssignResponses, BgType, FloraType)
from flaskblog import db
from werkzeug.utils import secure_filename
from sqlalchemy import and_


def save_picture(form_picture, evalu):
	for file in form_picture:
		file_name = secure_filename(file.filename)
		random_hex = secrets.token_hex(8)
		_, f_ext = os.path.splitext(file_name)
		picture_fn = random_hex + f_ext
		picture_path = os.path.join(current_app.root_path, 'static/micro_pics', picture_fn)
		file.save(picture_path)
		micro = Microphoto(image_file=picture_fn, image=evalu)
		db.session.add(micro)
	db.session.commit()

	return file_name

def generate_link(page):
	link = str(uuid.uuid4())  # Genera un ID único
	page = page  # Obtiene la página asociada desde el formulario
	invitation_link = InvitationLink(link=link, classes=page)
	db.session.add(invitation_link)
	db.session.commit()

def check_status(student, micro_ids):
	status = ''
	assigns=[]
	respons=[]
	corrects=[]
	for micro in micro_ids:
		assignation = Assignations.query.filter(and_(Assignations.student_id==student.id, Assignations.microphoto_id==micro.id)).all()
		if not assignation == []:
			assigns.append(assignation[0])
	for assign in assigns: 
		response = Responses.query.filter_by(assignations_id=assign.id).all()
		if not response == []:
			respons.append(response[0])
	for resp in respons:
		correction = CorrectionRes.query.filter_by(responses=resp.id).first()
		print(correction)
		if not correction == None:
			corrects.append(correction)
	if corrects:
		status = 'correction'
	elif respons:
		status = 'response'
	elif assigns:
		status = 'assign'
	else:
		status = 'no_assign'

	return status

def search(eval_id, student_id):
	microphotos = Microphoto.query.filter_by(evaluation_id=eval_id).all()
	st = Student.query.filter_by(user_id=student_id).first()
	assign_list = []
	for photo in microphotos:
		assign = Assignations.query.filter_by(student_id=st.id, microphoto_id=photo.id).first()
		if assign:
			photo = Microphoto.query.filter_by(id=assign.microphoto_id).first()
			photo_i=[url_for('static', filename='micro_pics/' + photo.image_file)]
			cells = Responses.query.filter_by(assignations_id=assign.id).all()
			cell_other_for=[]
			for i in cells:
				cell_for = Cell.query.filter_by(id=i.cell_id).first()
				if not cell_for.correction:
					cell_other_for.append(cell_for)
			if not cell_other_for:
				return 'no_a_list'
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
				cell_list.append([cell_type, cyto_morph, cyto_size, cyto_color, core_morph, core_size, core_chroma, cell.id, assign.id])
			is_response_micro = AssignResponses.query.filter_by(assignations_id=assign.id).first()
			micro_list=[]
			if is_response_micro:
				if not is_response_micro.correction:
					micro_response=True
					bgtype = BgType.query.filter_by(id=is_response_micro.bg_type_id).first()
					floratype = FloraType.query.filter_by(id=is_response_micro.flora_type_id).first()

					micro_list.append(bgtype.name)
					micro_list.append(floratype.name)
					micro_list.append(is_response_micro.cell_predominance)
			if not micro_list:
				return 'no_a_list'
			num = random.random()
			num_t = random.random()
			assign_list.append([photo_i, assign, [num, cell_list], [num_t, micro_list]])
	return assign_list