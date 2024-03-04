from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, SelectField)
from wtforms.validators import NoneOf


class ResponseCellForm(FlaskForm):
    cell_type = SelectField('Tipo de celula:', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    cyto_morph = SelectField('Forma', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    cyto_size = SelectField('Tamaño', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    cyto_color = SelectField('Color', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    core_morph = SelectField('Forma', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    core_size = SelectField('Tamaño', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    core_chroma = SelectField('Cromatina', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    submit = SubmitField('Enviar')

class ResponseMicroForm(FlaskForm):
    backgr_type = SelectField('Tipo de fondo', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    flora_type = SelectField('Tipo de flora', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    cell_predominance = StringField('Predominio de celulas', validators=[NoneOf(values=['0'], message='Debe seleccionar una opción.')])
    submit = SubmitField('Enviar')
