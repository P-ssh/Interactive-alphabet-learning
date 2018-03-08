from flask_wtf import FlaskForm
from wtforms import RadioField


class QuizForm(FlaskForm):
    quizform = RadioField('quiz')