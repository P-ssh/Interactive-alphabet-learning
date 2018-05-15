from project import db, bcrypt

import datetime


class User(db.Model):

    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
  
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, username, password, admin=False):
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_registeredOn(self):
    	return self.registered_on

    def __repr__(self):
        return '<email {}'.format(self.email)

class Mchedruli(db.Model):
	__tablename__ = "mchedruli"
	__table_args__ = {'extend_existing':True}

	email = db.Column(db.String, primary_key=True, unique=True, nullable=False)
	level = db.Column(db.Integer,nullable=False, default=1)
	maxLevel = db.Column(db.Integer, nullable=False, default=150)
	introLevel = db.Column(db.Integer,nullable=False, default=1)
	introToLevelMap = db.Column(db.String, nullable=False, default='{1: (1, 10), 2: (11, 20), 3: (21, 30), 4: (31, 40), 5: (41, 50), 6: (51, 59), 7: (60, 69), 8: (70, 77), 9: (78, 87), 10: (88, 150)}')
	charStats = db.Column(db.String, nullable=False, default="{u'\u10d1': {'chapter': 4, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d0': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d3': {'chapter': 2, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d2': {'chapter': 5, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d5': {'chapter': 3, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d4': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d7': {'chapter': 4, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d6': {'chapter': 7, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d9': {'chapter': 6, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d8': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10db': {'chapter': 2, 'rate': '', 'total': 0, 'correct': 0}, u'\u10da': {'chapter': 3, 'rate': '', 'total': 0, 'correct': 0}, u'\u10dd': {'chapter': 2, 'rate': '', 'total': 0, 'correct': 0}, u'\u10dc': {'chapter': 3, 'rate': '', 'total': 0, 'correct': 0}, u'\u10df': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}, u'\u10de': {'chapter': 8, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e1': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e0': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e3': {'chapter': 4, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e2': {'chapter': 6, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e5': {'chapter': 7, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e4': {'chapter': 8, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e7': {'chapter': 8, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e6': {'chapter': 9, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e9': {'chapter': 9, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e8': {'chapter': 5, 'rate': '', 'total': 0, 'correct': 0}, u'\u10eb': {'chapter': 9, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ea': {'chapter': 6, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ed': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ec': {'chapter': 7, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ef': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ee': {'chapter': 5, 'rate': '', 'total': 0, 'correct': 0}, u'\u10f0': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}}")
	chapterProgress = db.Column(db.String, nullable=False, default="{1: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 1}, 2: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 11}, 3: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 21}, 4: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 31}, 5: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 41}, 6: {'status': 'Not started', 'progress': {'current': 0, 'total': 9}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 51}, 7: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 60}, 8: {'status': 'Not started', 'progress': {'current': 0, 'total': 8}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 70}, 9: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 78}, 10: {'status': 'Not started', 'progress': {'current': 0, 'total': 63}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 88}}")
	answersHistory = db.Column(db.String, nullable=False, default='{}')
	wrongAnswers = db.Column(db.String, nullable=False, default='[]')

	def __init__(self, email, wrongAnswers="[]", answersHistory="{}", level=1, introLevel=1, maxLevel=150, introToLevelMap="{1: (1, 10), 2: (11, 20), 3: (21, 30), 4: (31, 40), 5: (41, 50), 6: (51, 59), 7: (60, 69), 8: (70, 77), 9: (78, 87), 10: (88, 150)}",\
				charStats="{u'\u10d1': {'chapter': 4, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d0': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d3': {'chapter': 2, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d2': {'chapter': 5, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d5': {'chapter': 3, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d4': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d7': {'chapter': 4, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d6': {'chapter': 7, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d9': {'chapter': 6, 'rate': '', 'total': 0, 'correct': 0}, u'\u10d8': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10db': {'chapter': 2, 'rate': '', 'total': 0, 'correct': 0}, u'\u10da': {'chapter': 3, 'rate': '', 'total': 0, 'correct': 0}, u'\u10dd': {'chapter': 2, 'rate': '', 'total': 0, 'correct': 0}, u'\u10dc': {'chapter': 3, 'rate': '', 'total': 0, 'correct': 0}, u'\u10df': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}, u'\u10de': {'chapter': 8, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e1': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e0': {'chapter': 1, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e3': {'chapter': 4, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e2': {'chapter': 6, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e5': {'chapter': 7, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e4': {'chapter': 8, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e7': {'chapter': 8, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e6': {'chapter': 9, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e9': {'chapter': 9, 'rate': '', 'total': 0, 'correct': 0}, u'\u10e8': {'chapter': 5, 'rate': '', 'total': 0, 'correct': 0}, u'\u10eb': {'chapter': 9, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ea': {'chapter': 6, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ed': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ec': {'chapter': 7, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ef': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}, u'\u10ee': {'chapter': 5, 'rate': '', 'total': 0, 'correct': 0}, u'\u10f0': {'chapter': 10, 'rate': '', 'total': 0, 'correct': 0}}",\
				chapterProgress="{1: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 1}, 2: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 11}, 3: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 21}, 4: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 31}, 5: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 41}, 6: {'status': 'Not started', 'progress': {'current': 0, 'total': 9}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 51}, 7: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 60}, 8: {'status': 'Not started', 'progress': {'current': 0, 'total': 8}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 70}, 9: {'status': 'Not started', 'progress': {'current': 0, 'total': 10}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 78}, 10: {'status': 'Not started', 'progress': {'current': 0, 'total': 63}, 'correct': {'rate': '', 'subtotal': 0, 'correct': 0}, 'repeatLevel': 88}}"):
		self.email = email
		self.level = level
		self.introLevel = introLevel
		self.maxLevel = maxLevel
		self.introToLevelMap = introToLevelMap
		self.charStats = charStats
		self.chapterProgress = chapterProgress
		self.wrongAnswers = wrongAnswers
		self.answersHistory = answersHistory

	def get_level(self):
		return self.level

	def get_introLevel(self):
		return self.introLevel

	def get_maxLevel(self):
		return self.maxLevel

	def get_introToLevelMap(self):
		return self.introToLevelMap

	def get_charStats(self):
		return self.charStats

	def get_chapterProgress(self):
		return self.chapterProgress

	def get_wrongAnswers(self):
		return self.wrongAnswers

	def get_answersHistory(self):
		return self.answersHistory