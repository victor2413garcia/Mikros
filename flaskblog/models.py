cfrom datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class FloraType(db.Model):
    __tablename__ = 'floratype'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"FloraType('{self.name}')"

class BgType(db.Model):
    __tablename__ = 'bgtype'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"BgType('{self.id}')"

class CellType(db.Model):
    __tablename__ = 'celltype'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"CellType('{self.name}')"

class MorphCyto(db.Model):
    __tablename__ = 'morphcyto'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"MorphCyto('{self.name}')"

class ColorCyto(db.Model):
    __tablename__ = 'colorcyto'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"ColorCyto('{self.name}')"

class SizeCore(db.Model):
    __tablename__ = 'sizecore'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"SizeCore('{self.name}')"

class ChromatinCore(db.Model):
    __tablename__ = 'chromatincore'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"ChromatinCore('{self.name}')"

class MorphCore(db.Model):
    __tablename__ = 'morphcore'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"MorphCore('{self.name}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    ci = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(11), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    professors = db.relationship('Professor', backref='collaborator', uselist=False)
    students = db.relationship('Student', backref='member', uselist=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.ci}', '{self.email}', '{self.image_file}')"

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(100), nullable=False)
    user = db.relationship('User', backref='user')
    def __repr__(self):
        return f"Post('{self.title}')"

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    classes = db.relationship('Class', backref='subjects')

    def __repr__(self):
        return f"Professor('{self.user_id}', '{self.classes}')"

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    classes = db.relationship('ClassList', backref='classes')
    homework = db.relationship('Assignations', backref='homework')

    def __repr__(self):
        return f"Student('{self.user_id}')"

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(120), nullable=True)
    period = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    members = db.relationship('ClassList', backref='members')
    evaluations = db.relationship('Evaluation', backref='evaluations')
    inv_link = db.relationship('InvitationLink', backref='invlink')

    def __repr__(self):
        return f"Class('{self.name}', '{self.period}', '{self.date_posted}')"

class ClassList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __repr__(self):
        return f"ClassList('{self.class_id}', '{self.student_id}')"

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    date_delivered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_limit = db.Column(db.DateTime, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    images = db.relationship('Microphoto', backref='image')

    def __repr__(self):
        return f"Evaluation('{self.name}', '{self.description}')"

class Microphoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(128), nullable=False, default='default.jpg')
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluation.id'))
    assignations = db.relationship('Assignations', backref='assign')

    def __repr__(self):
        return f'{self.id}'

class Assignations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    microphoto_id = db.Column(db.Integer, db.ForeignKey('microphoto.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    responses = db.relationship('Responses', backref='response')
    assignres = db.relationship('AssignResponses', backref='assres')
    grade = db.Column(db.Float, nullable=True)
    observation = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"{self.id}"

class Cell(db.Model):
    __tablename__ = 'cell'
    id = db.Column(db.Integer, primary_key=True)
    cell_type_id = db.mapped_column(db.Integer, db.ForeignKey('celltype.id'))
    morph_cyto_id = db.mapped_column(db.Integer, db.ForeignKey('morphcyto.id'))
    size_cyto_id = db.mapped_column(db.Integer, db.ForeignKey('sizecore.id'))
    color_cyto_id = db.mapped_column(db.Integer, db.ForeignKey('colorcyto.id'))
    morph_core_id = db.mapped_column(db.Integer, db.ForeignKey('morphcore.id'))
    size_core_id = db.mapped_column(db.Integer, db.ForeignKey('sizecore.id'))
    chromatin_core_id = db.mapped_column(db.Integer, db.ForeignKey('chromatincore.id'))

    cti = db.relationship("CellType", foreign_keys="[Cell.cell_type_id]", backref='one')
    mcyi = db.relationship("MorphCyto", foreign_keys="[Cell.morph_cyto_id]", backref='two')
    cci = db.relationship("ColorCyto", foreign_keys="[Cell.color_cyto_id]", backref='three')
    mcoi = db.relationship("MorphCore", foreign_keys="[Cell.morph_core_id]", backref='four')
    sci = db.relationship("SizeCore", foreign_keys="[Cell.size_core_id]", backref='five')
    chcoi = db.relationship("ChromatinCore", foreign_keys="[Cell.chromatin_core_id]", backref='six')

    
    responses = db.relationship('Responses', backref='cell')
    correction = db.relationship('CorrectionCell', backref='correction')

    def __repr__(self):
        return f"Cell('{self.number}')"

class Responses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignations_id = db.Column(db.Integer, db.ForeignKey('assignations.id'))
    cell_id = db.Column(db.Integer, db.ForeignKey('cell.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.id}"

class AssignResponses(db.Model):
    __tablename__ = 'assignresponses'
    id = db.Column(db.Integer, primary_key=True)
    assignations_id = db.Column(db.Integer, db.ForeignKey('assignations.id'))
    bg_type_id = db.Column(db.Integer, db.ForeignKey('bgtype.id'), nullable=False)
    flora_type_id = db.Column(db.Integer, db.ForeignKey('floratype.id'), nullable=False)
    cell_predominance = db.Column(db.String(120), nullable=True)

    correction = db.relationship('CorrectionRes', backref='correction')


    def __repr__(self):
        return f"{self.id}"

class CorrectionCell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cell = db.Column(db.Integer, db.ForeignKey('cell.id'))
    #Cell
    cell_type = db.Column(db.Boolean, nullable=False)
    morph_cyto = db.Column(db.Boolean, nullable=False)
    size_cyto = db.Column(db.Boolean, nullable=False)
    color_cyto = db.Column(db.Boolean, nullable=False)
    morph_core = db.Column(db.Boolean, nullable=False)
    size_core = db.Column(db.Boolean, nullable=False)
    chromatin_core = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"CorrectionCell('{self.id}')"

class CorrectionRes(db.Model):
    __tablename__ = 'correctionres'
    id = db.Column(db.Integer, primary_key=True)
    #Responses
    bg_type = db.Column(db.Boolean, nullable=False)
    flora_type = db.Column(db.Boolean, nullable=False)
    cell_predominance = db.Column(db.Boolean, nullable=False)

    responses = db.Column(db.Integer, db.ForeignKey('assignresponses.id'))

    def __repr__(self):
        return f"CorrectionRes('{self.id}')"

class InvitationLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(120), nullable=False)
    classes = db.Column(db.Integer, db.ForeignKey('class.id'))

    def __repr__(self):
        return f"InvitationLink('{self.link}')"
