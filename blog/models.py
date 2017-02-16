# _*_ coding:utf-8 _*_

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer   #邮箱验证token
from flask import current_app, request
from datetime import datetime
import hashlib
from markdown import markdown
import bleach

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


class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)


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


class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	'''
	提交表单后,POST 请求只会发送纯 Markdown 文本,页面中显示的 HTML 预览会被丢掉。 
	和表单一起发送生成的 HTML 预览有安全隐患,因为攻击者轻易就能修改 HTML 代码, 让
	其和 Markdown 源不匹配,然后再提交表单。安全起见,只提交 Markdown 源文本,在 服
	务器上使用 Markdown(Markdown 到 HTML 转换程序)将其转换 成 HTML。得到 HTML 
	后,再使用 Bleach 进行清理,确保其中只包含几个允许使用的HTML 标签。把 Markdown 
	格式的博客文章转换成 HTML 的过程可以在 _posts.html 模板中完成,但这 么做效率不
	高,因为每次渲染页面时都要转换一次。为避免重复工作,我们可在创建博 客文章时做一次性
	转换。转换后的博客文章 HTML 代码缓存在 Post 模型的一个新字段中, 在模板中可以直
	接调用。文章的 Markdown 源文本还要保存在数据库中,以防需要编辑。
	'''
	body_html = db.Column(db.Text)

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

	@staticmethod
	def on_changed_body(target, value,oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
						'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
														tags=allowed_tags, strip=True))
		

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


db.event.listen(Post.body, 'set', Post.on_changed_body)
login_manager.anonymous_user = AnonymousUser
