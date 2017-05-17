# _*_ coding:utf-8 _*_

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField

from ..models import Role, User


class NameForm(Form):
	name = StringField("用户名?",validators=[Required()])
	submit = SubmitField('提交')


class EditProfileForm(Form):
	name = StringField('姓名', validators=[Length(0, 64)]) 
	location = StringField('地址', validators=[Length(0, 64)]) 
	about_me = TextAreaField('关于我')
	submit = SubmitField('提交')

class EditAdminProfileForm(Form):
	email = StringField('邮箱', validators=[Required(),Length(1,64),Email()])
	username = StringField('用户名',validators=[Required(),Length(1,64),\
				Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'必须只包含字母数字标点下划线')])
	confirmed = BooleanField('验证否')
	role = SelectField('角色',coerce=int)
	name = StringField('姓名',validators=[Length(0,64)])
	location = StringField('地址',validators=[Length(0,64)])
	about_me = TextAreaField('关于我')
	submit = SubmitField('提交')

	def __init__(self,user,*args,**kwargs):
		super(EditAdminProfileForm,self).__init__(*args,**kwargs)
		self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self,field):
		if field.data != self.user.email and User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已存在.')

	def validate_username(self,field):
		if field.data != self.user.username and User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已存在.')


class PostForm(Form):
	body = PageDownField("写出你的想法?", validators=[Required()])
	submit = SubmitField('提交')


class CommentForm(Form):
	body = StringField("写出你的评论", validators=[Required()])
	submit = SubmitField('提交')

