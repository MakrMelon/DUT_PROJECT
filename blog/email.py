# _*_ coding:utf-8 _*_

from flask import current_app,render_template
from flask.ext.mail import Message  
from threading import Thread
from . import mail

#异步发送电子邮件
def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)

#发送电子邮件
def send_email(to,subject,template,**kwargs):
	app = current_app._get_current_object()
	msg = Message(app.config['MAIL_PREFIX'] + subject,sender=app.config['MAIL_USERNAME'],recipients=[to])
	msg.body = render_template(template + '.txt',**kwargs)
	#msg.body = 'text body'
	msg.html = render_template(template + '.html',**kwargs)
	#msg.html = '<b>HTML</b> body'
	thr = Thread(target=send_async_email,args=[app,msg])
	thr.start()
	return thr

