from flask import render_template, abort, redirect, url_for, flash, request, make_response
from . import main
from ..models import User, Role, Comment
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, EditPostForm, CommentForm
from flask_login import current_user
from .. import db
from flask_login import login_required
from ..decorators import admin_required, permission_required
from ..models import Permission, Post
from datetime import datetime


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit() and current_user.can(Permission.WRITE_ARTICLES):
        post = Post(body=form.body.data, author=current_user._get_current_object(), title=form.title.data,
                    category=form.category.data, timestamp=datetime.utcnow())
        db.session.add(post)
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
                                  page, per_page=8, error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination, show_followed=show_followed)


@main.route('/post-category/<category>', methods=['GET'])
def show_category_post(category):
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category=category).order_by(Post.timestamp.desc()).paginate(page, per_page=8,
                                                                                                  error_out=False)
    posts = pagination.items
    return render_template('post_category.html', posts=posts, pagination=pagination, category=category)


@main.route('/user/<username>')
def user(username):
    request_user = User.query.filter_by(username=username).first()
    if request_user is None:
        abort(404)
    posts = request_user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=request_user, posts=posts)


@main.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('You have changed your profile.')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@main.route('/user/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    edit_user = User.query.get_or_404(id)
    form = EditProfileAdminForm(edit_user)
    if form.validate_on_submit():
        edit_user.email = form.email.data
        edit_user.username = form.username.data
        edit_user.confirmed = form.confirmed.data
        edit_user.role = Role.query.get(form.role.data)
        edit_user.name = form.name.data
        edit_user.location = form.location.data
        edit_user.about_me = form.about_me.data
        db.session.add(edit_user)
        flash('You have changed profile.')
        return redirect(url_for('main.user', username=edit_user.username))
    form.email.data = edit_user.email
    form.username.data = edit_user.username
    form.confirmed.data = edit_user.confirmed
    form.role.data = edit_user.role  # 如果是edit_user.role呢？
    form.name.data = edit_user.name
    form.location.data = edit_user.location
    form.about_me = edit_user.about_me

    return render_template('edit_profile_admin.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    posts = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=posts, author=current_user._get_current_object())
        db.session.add(comment)
        flash('You comment has been published......')
        return redirect(url_for('main.post', id=posts.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (posts.comments.count() - 1) / 20 + 1
    pagination = posts.comments.order_by(Comment.timestamp.asc()).paginate(
                                      page, error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[posts], form=form, pagination=pagination, comments=comments)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = EditPostForm()
    posts = Post.query.get_or_404(id)
    if current_user != posts.author and not current_user.can(Permission.ADMINISTER):
        abort(404)
    if form.validate_on_submit():
        posts.body = form.body.data
        db.session.add(posts)
        return redirect(url_for('main.post', id=posts.id))
    form.body.data = posts.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You have follow this user already.')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    flash('Follow user %s successfully' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You have not follow this user.')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    flash('Unfollow user %s successfully' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', follows=follows, pagination=pagination, user=user,
                           endpoint='main.followers', title='Followers of')


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', follows=follows, pagination=pagination, user=user,
                           endpoint='main.followers', title='Followed by')


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/show_followed')
@login_required
def show_followed_posts():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
                                             page, error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))