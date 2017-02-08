# _*_ coding:utf-8 _*_

from flask.ext.script import Manager
from flask.ext.script import Shell
from flask.ext.migrate import Migrate,MigrateCommand    #数据库迁移模块

from blog import create_app, db


def make_shell_context():
	return dict(app=app,db=db,User=User,Role=Role)

app = create_app('default')

migrate = Migrate(app,db)
manager = Manager(app)

#单元测试命令
@manager.command
def test():
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
	manager.add_command('shell',Shell(make_context=make_shell_context))  #集成上下文环境
	manager.add_command('db',MigrateCommand)  #数据库迁移shell
	manager.run()