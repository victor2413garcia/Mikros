from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, IntegerField,
						 DateField, MultipleFileField, DecimalField, BooleanField, HiddenField)
from wtforms.validators import DataRequired, NumberRange, Optional


class ClassForm(FlaskForm):
    name = StringField('Materia', validators=[DataRequired()])
    quarter = IntegerField('Trimestre', validators=[DataRequired(), NumberRange(min=1, max=15)])
    description = TextAreaField('Descripcion', validators=[DataRequired()])
    submit = SubmitField('Crear Clase')

class EvaluationForm(FlaskForm):
	title = StringField('Titulo', validators=[DataRequired()])
	description = TextAreaField('Descripcion', validators=[DataRequired()])
	picture = MultipleFileField('Microfotos', validators=[FileAllowed(['jpg', 'png'])])
	date_limit = DateField('Hasta', validators=[DataRequired()], format='%Y-%m-%d')
	submit = SubmitField('Crear Evaluacion')

class AssignationForm(FlaskForm):
    student_id = HiddenField('student_id', validators=[DataRequired()])
    submit = SubmitField('Asignar')

def dynamic_form(num):
    class_name = "AssignationForm"
    field_names = []

    for index in range(num):
        field_name = f"field_{index}"
        setattr(AssignationForm, field_name, BooleanField('', validators=[Optional()]))
        field_names.append(field_name)
    setattr(AssignationForm, "field_names", field_names)
    return AssignationForm()


class CorrectionForm(FlaskForm):
    cell_type = BooleanField('', validators=[Optional()])
    morph_cyto = BooleanField('', validators=[Optional()])
    size_cyto = BooleanField('', validators=[Optional()])
    color_cyto = BooleanField('', validators=[Optional()])
    morph_core = BooleanField('', validators=[Optional()])
    size_core = BooleanField('', validators=[Optional()])
    chromatin_core = BooleanField('', validators=[Optional()])
    bg_type = BooleanField('', validators=[Optional()])
    flora_type = BooleanField('', validators=[Optional()])
    cell_predominance = BooleanField('', validators=[Optional()])
    cell_id = HiddenField('cell_id', validators=[DataRequired()])
    assign_id = HiddenField('assign_id', validators=[DataRequired()])
    submit = SubmitField('Siguiente')


class GradeForm(FlaskForm):
    observation = TextAreaField('Observaciones', validators=[Optional()])
    grade = DecimalField('Calificacion', validators=[DataRequired(),NumberRange(min=0, max=20)])
    submit = SubmitField('Cargar Calificación')
