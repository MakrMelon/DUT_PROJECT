# _*_ coding:utf-8 _*_
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, abort, flash, request\
				,make_response
from flask.ext.login import current_user, login_required

from . import main
from .forms import NameForm, EditProfileForm, EditAdminProfileForm, PostForm, CommentForm, SearchForm
from .. import db
from ..models import User, Role, Permission, Post, Comment
from ..email import send_email
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		'''
		current_user 由 Flask-Login 提供,和所有上下文变量一样,也是通过线程内的代理对象实 现。
		这个对象的表现类似用户对象,但实际上却是一个轻度包装,包含真正的用户对象。 数据库需要真正的
		用户对象,因此要调用 _get_current_object()方法
		'''
		post = Post(title=form.title.data,body=form.body.data,author=current_user._get_current_object())
		db.session.add(post)
	 	return redirect(url_for('.index'))
	show_followed = False
	if current_user.is_authenticated: #用户已经登录
		show_followed = bool(request.cookies.get('show_followed', ''))
	if show_followed:
		query = current_user.followed_posts()
	else:
		query = Post.query
	page = request.args.get('page', 1, type=int)
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],error_out=False)
	posts = pagination.items
	return render_template('index.html', form=form, posts=posts, pagination=pagination,
							show_followed=show_followed)

@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '', max_age = 30*24*60*60)
	return resp

@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '1', max_age = 30*24*60*60)
	return resp
             
@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.filter_by(author_id=user.id).order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],error_out=False)
	posts = pagination.items
	return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit_profile',methods=['GET','POST'])
@login_required
def  edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('资料已更新')
		return redirect(url_for('main.user',username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html',form=form)

@main.route('/edit_admin_profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_admin_profile(id):
	user = User.query.get_or_404(id)
	form = EditAdminProfileForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('资料已更新.')
		return redirect(url_for('main.user',username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html',form=form,user=user)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data,
							post = post,
							author=current_user._get_current_object())
		db.session.add(comment)
		flash('评论已发布.')
		return redirect(url_for('.post', id=post.id, page=-1))
	page = request.args.get('page', 1, type=int)
	#这是个特殊的页数,用来请求评论的最后一页,所以刚提交的评论才会出现在页面中。程序从查询字符串 
	#中获取页数,发现值为-1时,会计算评论的总量和总页数,得出真正要显示的页数。
	if page == -1:
		#这个计算可以举几个例子  自己计算下
		page = (post.comments.count() - 1)//current_app.config['BLOG_COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc())\
		.paginate(page, per_page=current_app.config['BLOG_COMMENTS_PER_PAGE'], error_out=False)
	comments = pagination.items
	return render_template('post.html',posts=[post], form=form, 
							comments=comments, pagination=pagination)


@main.route('/edit_post/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
	post = Post.query.get_or_404(id)
	if current_user.id != post.author_id and not current_user.can(Permission.ADMIN):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('文章已发布.')
	 	return redirect(url_for('.post',id=post.id))
	form.title.data = post.title
	form.body.data = post.body
	return render_template('edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('未知用户.')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('你已经关注了这个用户.')
		return redirect(url_for('.user', username=username))
	current_user.follow(user)
	flash('你成功关注了这个用户 %s.' % username)
	return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('未知用户.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你并未关注这个用户.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('成功取消关注.')
    return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('未知用户.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(page, 
										per_page=current_app.config['BLOG_FOLLOWERS_PER_PAGE'],
										error_out=False)
	follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
	return render_template('followers.html', user=user, title=" 关注者们",
							endpoint='.followers', pagination=pagination, follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('未知用户.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(page, 
										per_page=current_app.config['BLOG_FOLLOWERS_PER_PAGE'],
										error_out=False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
	return render_template('followers.html', user=user, title="正在关注",
							endpoint='.followed_by', pagination=pagination, follows=follows)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page', 1, type=int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
		page, per_page=current_app.config['BLOG_COMMENTS_PER_PAGE'],error_out=False)
	comments = pagination.items
	return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


@main.route('/moderate/enable<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/search', methods=['GET','POST'])
def search():
	form = SearchForm()
	if  form.validate_on_submit():
		page = request.args.get('page', 1, type=int)
		pagination = Post.query.filter_by(title=form.target.data)\
			.order_by(Post.timestamp.desc()).paginate(
			page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
			error_out=False)
		posts = pagination.items
	 	return render_template('search.html',posts=posts,form=form,
	 		pagination=pagination)
	return render_template('search.html', form=form)

