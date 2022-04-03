from flask_wtf import FlaskForm
from wtforms import SubmitField

class LoginForm(FlaskForm):
    submit = SubmitField(label='Sign in')