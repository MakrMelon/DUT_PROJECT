# _*_ coding:utf-8 _*_

from datetime import datetime
from markdown import markdown
import bleach
from .. import db

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
	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	@staticmethod
	def generate_fake_posts(count=100):
		from random import seed, randint
		import forgery_py
		seed()
		user_count = User.query.count()
		for i in range(count):
			from .user import User
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

db.event.listen(Post.body, 'set', Post.on_changed_body)


