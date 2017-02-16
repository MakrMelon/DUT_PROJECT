# _*_ coding:utf-8 _*_

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

	SECRET_KEY = 'blog for myself string'   #表单安全
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True #自动提交数据库中的变动
	#验证邮箱配置
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PREFIX = '欢迎来到本博客'
	ADMIN = '879671510@qq.com'
	FLASKY_POSTS_PER_PAGE = 10      #每页最多显示文章数
	BLOG_FOLLOWERS_PER_PAGE = 10

	@staticmethod
	def init_app(app):
		pass


class DevelopConfig(Config):
	DEBUG = True
	MAIL_PORT = 587
	MAIL_USE_TLS = True  #启用传输层安全|
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '879671510@qq.com'
	MAIL_PASSWORD = os.environ.get('MAIL_CODE') or 'ipnokqkszfxubfgb'
	SQLALCHEMY_DATABASE_URI = 'mysql://root:211314@localhost:3306/blog'


class TestConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'mysql://root:211314@localhost:3306/blog_test'


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:211314@localhost:3306/blog'
	

config = {
	'development': DevelopConfig,
	'test': TestConfig,
	'production': ProductionConfig,
	'default': DevelopConfig
}
