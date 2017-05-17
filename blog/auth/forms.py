# _*_ coding:utf-8 _*_

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
	email = StringField("电子邮件",validators=[Required(),Email(),Length(1,64)])
	password = PasswordField('密码',validators=[Required(),Length(6,16)])
	remember_me = BooleanField('记住密码')
	submit = SubmitField('登入')


class RegistrationForm(Form):
	email = StringField("电子邮件",validators=[Required(),Email(),Length(1,64)])
	username = StringField('用户名', validators=[Required(), Length(1, 64), \
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'必须只包含字母数字标点下划线')])
	password = PasswordField('密码',validators=\
		[Required(),Length(6,16),EqualTo('password2',message='密码必须相同.')])
	password2 = PasswordField('确认密码',validators=[Required()])
	submit = SubmitField('注册')

	#如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法,这个方法就和常规的验证函数一起调用
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已存在')

	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已存在')




	


