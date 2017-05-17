# _*_ coding:utf-8 _*_

from .permission import Permission
from .. import db
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