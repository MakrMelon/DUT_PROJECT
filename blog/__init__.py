# _*_ coding:utf-8 _*_
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail 
from config import config


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()

def create_app(config_type):
	app = Flask(__name__)
	app.config.from_object(config[config_type])
	config[config_type].init_app(app)
	bootstrap.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	mail.init_app(app)

	#蓝本
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app
