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
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data,
					email=form.email.data,
					password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_token()
		send_email(user.email,'Confirm your account','auth/email/confirm',user=user,token=token)

		flash('A confirmation email has been sent to your email.')
		return redirect(url_for('main.index'))

	return render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account.')
	else:
		flash('Invalid token!')
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
		flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
	logout_user()
	flash('You have logged out.')
	return redirect(url_for('main.index'))

