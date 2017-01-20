# _*_ coding:utf-8 _*_
"""2017-01-20T04:04:59.795365Z 1 [Note] A temporary password is generated for root@localhost: ?_Xy5F,%ihz#

If you lose this password, please consult the section How to Reset the Root Password in the MySQL reference manual."""
from flask import Flask,render_template,session,redirect,url_for,flash
from flask import request
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
#时间相关
from datetime import datetime

#basedir = os.path.adspath(os.path.dirname(__file__)) #获取当前路径
app = Flask(__name__)
app.config['SECRET_KEY'] = 'blog for myself string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:211314@3306/blog'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True #自动提交数据库中的变动
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

class NameForm(Form):
	name = StringField("What's your name?",validators=[Required()])
	submit = SubmitField('Submit')

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(64),unique=True,index=True)

	def __repr__(self):
		return '<User %r>' % self.username

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'),500

@app.route('/',methods=['GET','POST'])
def index():
	form = NameForm()
	if form.validate_on_submit():
		old_name = session.get('name')
		if old_name is not None and old_name != form.name.data:
			flash('Looks like you have changed your name!')
		session['name'] = form.name.data
		return redirect(url_for('index'))
	return render_template('index.html',current_time=datetime.utcnow(),name=session.get('name'),form=form)

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

if __name__ == '__main__':
	app.run(debug=True)