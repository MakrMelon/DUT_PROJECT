# _*_ coding:utf-8 _*_
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email

@main.route('/', methods=['GET', 'POST'])
def index():
	print current_app.config['ADMIN']
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if	user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			session['known'] = False
			if current_app.config['ADMIN']:
				send_email(current_app.config['ADMIN'],'new user '+form.name.data,'mail/new_user',user=user)
	
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('.index'))
	return render_template('index.html',current_time=datetime.utcnow(),name=session.get('name'),\
		form=form,known=session.get('known',False))

