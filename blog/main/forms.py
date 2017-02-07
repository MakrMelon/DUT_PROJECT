# _*_ coding:utf-8 _*_

from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required


class NameForm(Form):
	name = StringField("What's your name?",validators=[Required()])
	submit = SubmitField('Submit')
