# _*_ coding:utf-8 _*_

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer   #邮箱验证token
from flask import current_app, request
from datetime import datetime
import hashlib

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

	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(),default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
	avatar_hash = db.Column(db.String(32))  
	posts = db.relationship('Post', backref='author', lazy='dynamic')

	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first() 
			else:
				self.role = Role.query.filter_by(default=True).first()
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

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

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	def gravatar(self, size=100,default='identicon',rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url, hash=hash, size=size, default=default, rating=rating)

	@staticmethod
	def generate_fake_users(count = 100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
					username=forgery_py.internet.user_name(True),
					password=forgery_py.lorem_ipsum.word(),
					confirmed=True,
					name=forgery_py.name.full_name(),
					location=forgery_py.address.city(),
					about_me=forgery_py.lorem_ipsum.sentence(),
					member_since=forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()


class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	@staticmethod
	def generate_fake_posts(count=100):
		from random import seed, randint
		import forgery_py

		seed()
		user_count = User.query.count()
		for i in range(count):
			u = User.query.offset(randint(0, user_count - 1)).first()
			p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
					timestamp=forgery_py.date.date(True),
					author=u)
			db.session.add(p)
			db.session.commit()
         

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
