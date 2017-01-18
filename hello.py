# _*_ coding:utf-8 _*_
from flask import Flask,render_template
from flask import request
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
#时间相关
from datetime import datetime
app = Flask(__name__)

bootstrap = Bootstrap(app)
moment = Moment(app)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'),500

@app.route('/')
def index():
	'''user_agent = request.headers.get('User-Agent')
	print request.headers
	return '<p>Your browser is %s</p>'%user_agent'''
	return render_template('index.html',current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

if __name__ == '__main__':
	app.run(debug=True)