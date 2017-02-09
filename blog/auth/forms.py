# _*_ coding:utf-8 _*_

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
	email = StringField("Email",validators=[Required(),Email(),Length(1,64)])
	password = PasswordField('Password',validators=[Required(),Length(6,16)])
	remember_me = BooleanField('keep me logged in')
	submit = SubmitField('Login')


class RegistrationForm(Form):
	email = StringField("Email",validators=[Required(),Email(),Length(1,64)])
	username = StringField('Username', validators=[Required(), Length(1, 64), \
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, numbers, dots or underscores')])
	password = PasswordField('Password',validators=\
		[Required(),Length(6,16),EqualTo('password2',message='Password must match.')])
	password2 = PasswordField('Confirm password',validators=[Required()])
	submit = SubmitField('Register')

	#如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法,这个方法就和常规的验证函数一起调用
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('email alread registered')

	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('username alread in use')




	


