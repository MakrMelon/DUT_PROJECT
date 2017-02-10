# _*_ coding:utf-8 _*_

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer   #邮箱验证token
from flask import current_app

from . import db, login_manager


#Flask-Login 要求程序实现一个回调函数,使用指定的标识符加载用户
#如果能找到用户,这个函数必须返回用户对象;否则应该返回 None。
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#权限常量	
class Permission:
	FOLLOW = 0X01
	COMMENT = 0X02
	WRITE_ARTICLES = 0X04
	MODERATE_COMMENTS = 0X08
	ADMIN = 0X80


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	users = db.relationship('User',backref='role',lazy='dynamic')
	default = db.Column(db.Boolean,default=False,index=True)
	permissions = db.Column(db.Integer)

	def __repr__(self):
		return '<Role %r>' % self.name

	@staticmethod
	def insert_roles():
		roles = {
			'User': (Permission.FOLLOW|
					Permission.COMMENT|
					Permission.WRITE_ARTICLES, True),
			'Moderator': (Permission.FOLLOW|
						Permission.COMMENT|
						Permission.WRITE_ARTICLES|
						Permission.MODERATE_COMMENTS,False),
			'Admin': (0Xff,False)

		}
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if(role is None):
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()



class User(UserMixin,db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(64),unique=True,index=True)
	age = db.Column(db.Integer,unique=False,default=10)
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(64),unique=True,index=True)
	confirmed = db.Column(db.Boolean,default=False)   #用户邮箱验证 

	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first() 
			else:
				self.role = Role.query.filter_by(default=True).first()

	def __repr__(self):
		return '<User %r>' % self.username

	@property
	def password(self):
		raise AttributeError('password is not a readble attribute')

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	def generate_token(self,expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'confirm':self.id})

	def confirm(self,token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True

	def can(self,permissions):
		return self.role is not None and (self.role.permissions & permissions)==permissions

	def is_admin(self):
		return self.can(Permission.ADMIN)


'''
这个对象继承自 Flask-Login 中的 AnonymousUserMixin 类,
并将其设为用户未登录时 current_user 的值。这样程序不用先检查用户是否登录,
就能自由调用 current_user.can() 和 current_user.is_administrator()。
'''
class AnonymousUser(AnonymousUserMixin):
	def can(self,permissions):
		return False

	def is_admin(self):
		return False


login_manager.anonymous_user = AnonymousUser
