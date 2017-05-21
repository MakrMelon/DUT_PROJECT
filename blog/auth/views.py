# _*_ coding:utf-8 _*_

from flask import render_template, url_for, redirect, flash, request
from flask.ext.login import login_user, logout_user, current_user, login_required

from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User
from .. import db
from ..email import send_email


@auth.route('/register', methods=['GET', 'POST'])
def register():
	registrationForm = RegistrationForm()
	if registrationForm.validate_on_submit():
		user = User(username=registrationForm.username.data,
					email=registrationForm.email.data,
					password=registrationForm.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_token()
		send_email(user.email,'邮箱验证','auth/email/confirm',user=user,token=token)
		flash('一封验证邮件已经发到你的邮箱.')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html',form=registrationForm)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('验证邮箱成功.')
	else:
		flash('未知的token!')
	return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_token()
    send_email(current_user.email,'验证邮箱',
                    'auth/email/confirm',user=current_user,token=token)
    flash('一封验证邮件已经发到你的邮箱.')
    return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		#已经注册并且密码正确
		if user is not None and user.verify_password(form.password.data): 
			#在用户会话中把用户标记为已登录
			login_user(user, form.remember_me.data) 
			#用户访问未授权的URL时会显示登录表单,Flask-Login会把原地址保存在查询字符串的next参数中
			#这个参数可从 request.args 字典中读取。如果查询字符串中没有 next 参数,则重定向到首页
			return redirect(request.args.get('next') or url_for('main.index')) 
		flash('用户名或密码错误.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
	logout_user()
	flash('你已经登出.')
	return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
	'''
	(1) 用户已登录(current_user.is_authenticated() 必须返回 True)。
	(2) 用户的账户还未确认。
	(3) 请求的端点(使用 request.endpoint 获取)不在认证蓝本中。访问认证路由要获取权
 		限,因为这些路由的作用是让用户确认账户或执行其他账户管理操作。
	'''
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed\
			and request.endpoint[:5] != 'auth.'\
			and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')



