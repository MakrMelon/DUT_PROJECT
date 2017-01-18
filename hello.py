from flask import Flask,render_template
from flask import request
from flask.ext.bootstrap import Bootstrap
app = Flask(__name__)

bootstrap = Bootstrap(app)

@app.route('/')
def index():
	'''user_agent = request.headers.get('User-Agent')
	print request.headers
	return '<p>Your browser is %s</p>'%user_agent'''
	return render_template('index.html')

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

if __name__ == '__main__':
	app.run(debug=True)