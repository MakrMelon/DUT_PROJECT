# _*_ coding:utf-8 _*_

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer   #邮箱验证token
from flask import current_app
from datetime import datetime
import random
from .. import db, login_manager
from .permission import Permission
from .role import Role
from .follow import Follow
from .comment import Comment

#Flask-Login 要求程序实现一个回调函数,使用指定的标识符加载用户
#如果能找到用户,这个函数必须返回用户对象;否则应该返回 None。
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(UserMixin,db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(64),unique=True,index=True)
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(64),unique=True,index=True)
	confirmed = db.Column(db.Boolean,default=False)   #用户邮箱验证
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(),default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
	from .post import Post
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	image_id = db.Column(db.String(32))
	#关注相关
	'''
		某个用户关注了 100 个用户,调用 user.followed.all() 后会返回一个列 表,其中包含 100 个 Follow 实例,每一
	个实例的 follower 和 followed 回引属性都指向相 应的用户。设定为 lazy='joined' 模式,就可在一次数据库查询中
	完成这些操作。如果把 lazy 设为默认值 select,那么首次访问 follower 和 followed 属性时才会加载对应的用户, 而
	且每个属性都需要一个单独的查询,这就意味着获取全部被关注用户时需要增加 100 次 额外的数据库查询。这两个关系中,User
	一侧设定的 lazy 参数作用不一样。lazy 参数都在“一”这一侧设定, 返回的结果是“多”这一侧中的记录。
		cascade 参数配置在父对象上执行的操作对相关对象的影响。比如,层叠选项可设定为: 将用户添加到数据库会话后,要自
	动把所有关系的对象都添加到会话中。	层叠选项的默认 值能满足大多数情况的需求,但对这个多对多关系来说却不合用。删除
	对象时,默认的层 叠行为是把对象联接的所有相关对象的外键设为空值。但在关联表中,删除记录后正确的行为应该是把指向该记录
	的实体也删除,因为这样能有效销毁联接。这就是层叠选项值 delete-orphan 的作用。cascade 参数的值是一组由逗号分隔的
	层叠选项,这看起来可能让人有 点困惑,但 all 表示除了 delete-orphan 之外的所有层叠选项。设为 all, delete-orphan 
	的意思是启用所有默认层叠选项,而且还要删除孤儿记录。
	'''
	#followed 和 followers 关系都定义为单独的一对多关系。
	followed = db.relationship('Follow',
								#为了消除外键间的歧义,定义关系时必须使用可选参数 foreign_keys 指定的外键
								foreign_keys=[Follow.follower_id],
								#并不是指定这两个关系之间的引用关系,而是回引Follow 模型。回引中的 lazy 
								#参数指定为 joined。这个 lazy 模式可以实现立即从联结查询中加载相关对象
								backref=db.backref('follower', lazy='joined'),
								#关系属性不会直 接返回记录,而是返回查询对象,所以在执行查询之前还可以添加额外的过滤器。
								lazy='dynamic',
								cascade='all, delete-orphan')
	followers = db.relationship('Follow',
								foreign_keys=[Follow.followed_id],
								backref=db.backref('followed', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first() 
			else:
				self.role = Role.query.filter_by(default=True).first()
		if self.email is not None and self.image_id is None:
			self.image_id = str(random.randint(1,10)) + 'image.jpg'
		self.follow(self)

	def __repr__(self):
		return '<User %r>' % self.username

	@property
	def password(self):
		raise AttributeError('密码不可读')

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

	#关注辅助方法
	def is_following(self,user):
		#关注者是self，被关注的人是user
		return self.followed.filter_by(followed_id=user.id).first() is not None

	def is_followed_by(self,user):
		#被关注者是self,关注者是user
		return self.followers.filter_by(follower_id=user.id).first() is not None

	#关注
	def follow(self,user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)

	#取消关注
	def unfollow(self,user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	#获取所关注用户的文章
	def followed_posts(self):
		from .post import Post
		return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
				.filter(Follow.follower_id == self.id)

	@staticmethod
	def add_self_follows():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()
		

#并将其设为用户未登录时 current_user 的值。这样程序不用先检查用户是否登录,
#就能自由调用 current_user.can() 和 current_user.is_administrator()。
class AnonymousUser(AnonymousUserMixin):
	def can(self,permissions):
		return False

	def is_admin(self):
		return False
login_manager.anonymous_user = AnonymousUser
