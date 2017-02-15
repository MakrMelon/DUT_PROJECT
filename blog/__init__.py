# _*_ coding:utf-8 _*_
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail 
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from config import config


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
#设为 'strong' 时,Flask-Login 会记录客户端 IP 地址和浏览器的用户代理信息,如果发现异动就登出用户
login_manager.session_protection = 'strong'
#设置登录页面的端点
login_manager.login_view = 'auth.login'
pagedown = PageDown()

def create_app(config_type):
	app = Flask(__name__)
	app.config.from_object(config[config_type])
	config[config_type].init_app(app)
	bootstrap.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	mail.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)

	#蓝本
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint,url_prefix='/auth')

	return app
 

