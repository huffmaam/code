import time

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func, text, update
from sqlalchemy import and_
from flask_wtf import FlaskForm
import random
import string
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:abc123@localhost/social_blog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:abc123@localhost/social_blog'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用追踪修改，提高性能
db = SQLAlchemy(app)

app.secret_key = 'your_secret_key'  # 设置一个用于 session 管理的密钥

# 邮箱配置
app.config['SECRET_KEY'] = 'your_secret_key'  # 用于安全目的，请替换为随机的字符串
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '1659601706@qq.com'  # 请替换为你的 QQ 邮箱
app.config['MAIL_PASSWORD'] = 'acjkfujenbjccgab'  # 请替换为你的 QQ 邮箱密码

mail = Mail(app)


class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_username = StringField('Username', validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password',
                                                                                             message='Passwords must match')])
    submit = SubmitField('Send Verification Code')


class VerifyForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    resend_code = BooleanField('Resend Code')
    submit = SubmitField('Verify Code')


class PersonForm(FlaskForm):
    new_username = StringField('Username', validators=[DataRequired()])
    new_email = StringField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('Password', validators=[DataRequired()])
    new_bio = StringField('Bio', validators=[DataRequired()])
    submit = SubmitField('Send Personal Code')


def generate_verification_code():
    """
    生成随机验证码
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class Blog(db.Model):
    __tablename__ = 'Blog'

    BlogID = db.Column(db.Integer, primary_key=True)
    AuthorID = db.Column(db.Integer, db.ForeignKey('User.UserID'))
    Title = db.Column(db.String(255), nullable=False)

    Content = db.Column(db.Text, nullable=False)
    PublishTime = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    LikesCount = db.Column(db.Integer, default=0)


class User(db.Model):
    __tablename__ = 'User'

    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    RegistrationTime = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    Avatar = db.Column(db.String(255))
    Bio = db.Column(db.Text)


class Comment(db.Model):
    __tablename__ = 'Comment'

    CommentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BlogID = db.Column(db.Integer, db.ForeignKey('Blog.BlogID'))
    CommenterID = db.Column(db.Integer, db.ForeignKey('User.UserID'))
    Content = db.Column(db.Text, nullable=False)
    CommentTime = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    commenter = db.relationship('User', foreign_keys=[CommenterID])


class Follow(db.Model):
    __tablename__ = 'Follow'

    FollowID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FollowerID = db.Column(db.Integer, db.ForeignKey('User.UserID'))
    FollowingID = db.Column(db.Integer, db.ForeignKey('User.UserID'))


class Upvote(db.Model):
    __tablename__ = 'Upvote'

    LikeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('User.UserID'))
    BlogID = db.Column(db.Integer, db.ForeignKey('Blog.BlogID'))


class Message2(db.Model):
    __tablename__ = 'Message'

    MessageID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SenderID = db.Column(db.Integer, db.ForeignKey('User.UserID'))
    RecipientID = db.Column(db.Integer, db.ForeignKey('User.UserID'))
    Content = db.Column(db.Text, nullable=False)
    SendTime = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    IsRead = db.Column(db.Boolean, default=False)


# ... 其他模型类定义 ...

# ... 在这里添加其他扩展和配置，例如 Flask-Login ...

def require_login(view):
    """
    装饰器函数用于检查用户是否已登录。
    如果没有登录，它将重定向到登录页面。
    """

    def wrapped(*args, **kwargs):
        # 检查用户是否已登录
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def before_request():
    """
    在每个请求之前调用，用于检查用户是否已登录。
    """
    if 'user_id' not in session and request.endpoint not in [
        'login', 'static', 'register', 'verify_code',
        'verify_code2', 'check_username', 'reset'
    ]:
        # 用户未登录且访问的不是登录页面或静态资源，则重定向到登录页面
        return redirect(url_for('login'))


@app.route('/')
def index2():
    return redirect(url_for('index'))


@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    # new_username = request.form['new_username']
    # new_email = request.form['new_email']
    # new_password = request.form['new_password']
    new_bio = request.form['new_bio']

    # print(new_username)
    # print(new_bio)
    # 在这里进行一些输入验证，确保新的信息是有效的

    # 根据 user_id 查询用户
    user = User.query.get(user_id)

    # # 更新用户信息
    # if new_username:
    #     user.Username = new_username
    # if new_email:
    #     user.Email = new_email
    # if new_password:
    #     user.Password = new_password
    # if new_bio:
    #     user.new_bio = new_bio

    user.Bio = new_bio

    # 提交到数据库
    db.session.commit()

    flash('用户信息已更新！', 'success')

    # 跳转回用户个人信息页面
    return redirect(url_for('personal_detail', user_id=user_id))


@app.route('/index', methods=['GET', 'POST'])
def index():
    # 检查用户是否已登录
    user_id = session.get('user_id')

    # 获取页数参数，默认为第一页
    page = int(request.args.get('page', 1))

    # 查询热门博客文章（假设 LikesCount 表示点赞数，按点赞数降序排序），分页每页显示 10 条记录
    hot_blogs = Blog.query.order_by(Blog.LikesCount.desc()).paginate(page=page, per_page=10)

    # 查询最新博客文章（按发布时间降序排序）
    latest_blogs = Blog.query.order_by(Blog.PublishTime.desc()).limit(5).all()

    # 随机查询博客
    random_blogs = Blog.query.order_by(func.random()).limit(10).all()

    # 查询推荐关注的用户（假设 Follow 表示用户关注关系）
    recommended_users = User.query.filter(User.UserID != user_id).order_by(User.RegistrationTime.desc()).limit(3).all()

    # 获取登录用户的个人信息
    user_info = None
    if user_id:
        user_info = User.query.get(user_id)

    return render_template('index.html', random_blogs=random_blogs, hot_blogs=hot_blogs, latest_blogs=latest_blogs,
                           recommended_users=recommended_users, user_info=user_info)


@app.route('/hot_blogs', methods=['GET', 'POST'])
def hot_blogs():
    # 检查用户是否已登录
    user_id = session.get('user_id')

    # 获取页数参数，默认为第一页
    page = int(request.args.get('page', 1))

    # 查询热门博客文章（假设 LikesCount 表示点赞数，按点赞数降序排序），分页每页显示 10 条记录
    hot_blogs = Blog.query.order_by(Blog.LikesCount.desc()).paginate(page=page, per_page=10)

    # 查询最新博客文章（按发布时间降序排序）
    latest_blogs = Blog.query.order_by(Blog.PublishTime.desc()).limit(5).all()

    # 随机查询博客
    random_blogs = Blog.query.order_by(func.random()).limit(10).all()

    # 查询推荐关注的用户（假设 Follow 表示用户关注关系）
    recommended_users = User.query.filter(User.UserID != user_id).order_by(User.RegistrationTime.desc()).limit(3).all()

    # 获取登录用户的个人信息
    user_info = None
    if user_id:
        user_info = User.query.get(user_id)

    return render_template('hot_blogs.html', random_blogs=random_blogs, hot_blogs=hot_blogs, latest_blogs=latest_blogs,
                           recommended_users=recommended_users, user_info=user_info)


# @app.route('/hot_blogs', methods=['GET', 'POST'])
# def hot_blogs():
#     # 获取登录用户的id
#     user_id = session.get('user_id')
#
#     # 获取页数参数，默认为第一页
#     page = int(request.args.get('page', 1))
#
#     # 查询热门博客文章（LikesCount 表示点赞数，按点赞数降序排序），分页每页显示 10 条记录
#     hot_blogs = Blog.query.order_by(Blog.LikesCount.desc()).paginate(page=page, per_page=10)
#
#     # 获取登录用户的所有信息
#     user_info = User.query.get(user_id)
#     return render_template('hot_blogs.html', hot_blogs=hot_blogs, user_info=user_info)


@app.route('/latest_blogs', methods=['GET', 'POST'])
def latest_blogs():
    # 检查用户是否已登录
    user_id = session.get('user_id')

    # 获取页数参数，默认为第一页
    page = int(request.args.get('page', 1))

    # 查询热门博客文章（假设 LikesCount 表示点赞数，按点赞数降序排序），分页每页显示 10 条记录
    hot_blogs = Blog.query.order_by(Blog.LikesCount.desc()).paginate(page=page, per_page=10)

    # 查询最新博客文章（按发布时间降序排序）
    latest_blogs = Blog.query.order_by(Blog.PublishTime.desc()).paginate(page=page, per_page=10)

    # 随机查询博客
    random_blogs = Blog.query.order_by(func.random()).limit(10).all()

    # 查询推荐关注的用户（假设 Follow 表示用户关注关系）
    recommended_users = User.query.filter(User.UserID != user_id).order_by(User.RegistrationTime.desc()).limit(3).all()

    # 获取登录用户的个人信息
    user_info = None
    if user_id:
        user_info = User.query.get(user_id)

    return render_template('latest_blogs.html', random_blogs=random_blogs, hot_blogs=hot_blogs,
                           latest_blogs=latest_blogs,
                           recommended_users=recommended_users, user_info=user_info)


@app.route('/follow_list/<int:user_id>')
def follow_list(user_id):
    # 获取关注的用户和被关注的用户
    followers = User.query.join(Follow, User.UserID == Follow.FollowerID).filter(
        Follow.FollowingID == user_id).all()

    following = User.query.join(Follow, User.UserID == Follow.FollowingID).filter(
        Follow.FollowerID == user_id).all()

    return render_template('follow_list.html', user_id=user_id, followers=followers, following=following)


@app.route('/unfollow/<int:user_id>/<int:unfollow_id>', methods=['POST'])
def unfollow(user_id, unfollow_id):
    follow_relationship = Follow.query.filter_by(FollowerID=user_id, FollowingID=unfollow_id).first()

    if follow_relationship:
        db.session.delete(follow_relationship)
        db.session.commit()
        flash('取消关注成功', 'success')
    else:
        flash('未找到关注关系', 'error')

    return redirect(url_for('follow_list', user_id=user_id))


@app.route('/follow/<int:user_id>/<int:follow_id>', methods=['POST'])
def follow(user_id, follow_id):
    new_follow = Follow(FollowerID=user_id, FollowingID=follow_id)
    db.session.add(new_follow)
    db.session.commit()
    return redirect(url_for('follow_list', user_id=user_id))


@app.route('/unfollow2/<int:user_id>/<int:unfollow_id>', methods=['POST'])
def unfollow2(user_id, unfollow_id):
    follow_relationship = Follow.query.filter_by(FollowerID=user_id, FollowingID=unfollow_id).first()

    if follow_relationship:
        db.session.delete(follow_relationship)
        db.session.commit()
        flash('取消关注成功', 'success')
    else:
        flash('未找到关注关系', 'error')

    return redirect(url_for('user_detail', user_id=unfollow_id))


@app.route('/follow2/<int:user_id>/<int:follow_id>', methods=['POST'])
def follow2(user_id, follow_id):
    # 假设 Follow 是表示关注关系的模型
    new_follow = Follow(FollowerID=user_id, FollowingID=follow_id)
    db.session.add(new_follow)
    db.session.commit()

    return redirect(url_for('user_detail', user_id=follow_id))


@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    # 查询指定ID的博客
    blog = Blog.query.get(blog_id)
    user = User.query.get(blog.AuthorID)

    # 获取用户id
    user_id = session['user_id']

    existing_like = Upvote.query.filter_by(UserID=user_id, BlogID=blog_id).first()

    # 构建查询
    # comments_query = (
    #     db.session.query(Comment)
    #         .join(User, Comment.CommenterID == User.UserID)
    #         .options(joinedload(Comment.commenter))  # 使用 Comment 模型中定义的关联属性
    #         .filter(Comment.BlogID == 26)
    # )
    #
    # comments = comments_query.all()
    #
    # for comment in comments:
    #     print(comment.Content, comment.Username)

    sql_query = f"""
    SELECT
        comment.Content,
        comment.CommentTime,
        user.UserID,
        user.Username
    FROM comment
    LEFT JOIN user ON comment.CommenterID = user.UserID
    WHERE BlogID = {blog_id};
    """

    result = db.engine.execute(text(sql_query))
    comments = result.fetchall()

    # # 处理查询结果
    # for row in comments:
    #     print('row[0]' + row[3])
    #     print('--------')
    #     content, comment_time, user_id, username = row
    #     print(f"Content: {content}, Comment Time: {comment_time}, User ID: {user_id}, Username: {username}")

    # for comment in comments:
    #     print(comment.Content,comment.commenter)

    # 查询博客的评论
    # comments = Comment.query.filter_by(BlogID=blog_id).all()
    # comments = Comment.query.filter_by(BlogID=blog_id).options(joinedload(Comment.commenter)).all()

    return render_template('blog_detail.html', blog=blog, author=user, comments=comments, existing_like=existing_like)


# @app.route('/blog/<int:blog_id>')
# def blog_detail(blog_id):
#     # 查询指定ID的博客
#     blog = Blog.query.get(blog_id)
#     # 查询该博客的作者
#     user = User.query.get(blog.AuthorID)
#     # 获取当前用户id
#     user_id = session['user_id']
#     # 查看当前用户是否对该博客进行点赞
#     existing_like = Upvote.query.filter_by(UserID=user_id, BlogID=blog_id).first()
#     # 查询相关信息
#     sql_query = f"""
#     SELECT 
#         comment.Content,
#         comment.CommentTime,
#         user.UserID,
#         user.Username 
#     FROM comment
#     LEFT JOIN user ON comment.CommenterID = user.UserID
#     WHERE BlogID = {blog_id};
#     """
#
#     result = db.engine.execute(text(sql_query))
#     comments = result.fetchall()
#
#     return render_template('blog_detail.html', blog=blog, author=user,
#                            comments=comments, existing_like=existing_like)


@app.route('/add_comment/<int:blog_id>', methods=['POST'])
def add_comment(blog_id):
    # 检查用户是否已登录，如果没有登录则重定向到登录页面
    if 'user_id' not in session:
        flash('请先登录以添加评论。', 'error')
        return redirect(url_for('login'))

    # 获取当前登录用户的ID
    user_id = session['user_id']

    # 获取评论内容
    comment_content = request.form['comment']

    # 创建新的评论
    new_comment = Comment(BlogID=blog_id, CommenterID=user_id, Content=comment_content)
    db.session.add(new_comment)
    db.session.commit()

    flash('评论添加成功！', 'success')
    return redirect(url_for('blog_detail', blog_id=blog_id))


# 处理点赞请求的路由
@app.route('/like_blog/<int:blog_id>', methods=['POST'])
def like_blog(blog_id):
    # 检查用户是否已登录，如果没有登录则返回错误信息
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '用户未登录'}), 401

    # 获取当前登录用户的ID
    user_id = session['user_id']

    # 查询用户是否已经点赞过这篇博客
    existing_like = Upvote.query.filter_by(UserID=user_id, BlogID=blog_id).first()

    if not existing_like:
        upvote_row = Upvote(UserID=user_id, BlogID=blog_id)
        db.session.add(upvote_row)
        db.session.commit()

        blog = Blog.query.get(blog_id)
        updated_likes_count = Blog.LikesCount + 1
        stmt = update(Blog).where(Blog.BlogID == blog_id).values(LikesCount=updated_likes_count)
        db.session.execute(stmt)
        db.session.commit()

        return jsonify({'success': True, 'likes_count': blog.LikesCount})
    else:
        db.session.delete(existing_like)
        db.session.commit()
        blog = Blog.query.get(blog_id)
        updated_likes_count = Blog.LikesCount - 1
        stmt = update(Blog).where(Blog.BlogID == blog_id).values(LikesCount=updated_likes_count)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify({'success': True, 'likes_count': blog.LikesCount})

    # 获取请求中的 is_liked 参数
    # is_liked = request.args.get('is_liked', type=bool)

    # 如果用户已经点赞过且 is_liked 为 False，则取消点赞；如果用户未点赞过且 is_liked 为 True，则点赞
    # if existing_like and not is_liked:
    #     db.session.delete(existing_like)
    #     message = '取消点赞成功'
    # elif not existing_like and is_liked:
    #     new_like = Upvote(UserID=user_id, BlogID=blog_id)
    #     db.session.add(new_like)
    #     message = '点赞成功'

    # 更新博客的点赞数
    # blog = Blog.query.get(blog_id)
    # if blog:
    #     blog.LikesCount = Upvote.query.filter_by(BlogID=blog_id).count()
    #     db.session.commit()
    #     return 'ok'
    #     # return jsonify({'success': True, 'message': message, 'likes_count': blog.LikesCount})
    # else:
    #     return jsonify({'success': False, 'message': '博客不存在'}), 404


@app.route('/publish_blog/<int:user_id>', methods=['GET', 'POST'])
def publish_blog(user_id):
    if request.method == 'POST':
        # 获取表单提交的博客标题和内容
        title = request.form['title']
        content = request.form['content']

        # 创建新的博客
        new_blog = Blog(AuthorID=user_id, Title=title, Content=content)
        db.session.add(new_blog)
        db.session.commit()

        flash('博客发布成功！', 'success')
        return redirect(url_for('index'))

    return render_template('publish_blog.html', user_id=user_id)


@app.route('/search_results/<int:user_id>', methods=['GET'])
def search_results(user_id):
    # 获取搜索条件
    username = request.args.get('username', '')
    title = request.args.get('title', '')
    content = request.args.get('content', '')

    # 获取当前页数，默认为1
    page = request.args.get('page', 1, type=int)

    # 根据条件进行模糊搜索
    search_results = perform_search(username, title, content, page)

    return render_template('search_results.html', user_id=user_id, results=search_results)


# 模糊搜索函数
def perform_search(username, title, content, page):
    blogs_per_page = 10  # 每页显示的博客数量
    query = Blog.query.filter(
        and_(
            (Blog.Title.like(f"%{title}%") if title else True),
            (Blog.Content.like(f"%{content}%") if content else True)
        )
    ).join(User).filter(User.Username.like(f"%{username}%") if username else True)

    # 使用 paginate() 方法分页
    search_results = query.paginate(page=page, per_page=blogs_per_page)

    return search_results


@app.route('/personal_detail/<int:user_id>')
def personal_detail(user_id):
    # 根据用户ID从数据库中获取用户信息
    user = User.query.get(user_id)
    per_blogs = Blog.query.filter_by(AuthorID=user_id)

    return render_template('personal_detail.html', user=user, per_blogs=per_blogs)


# 注意
@app.route('/user_detail/<int:user_id>')
def user_detail(user_id):
    # 根据用户ID从数据库中获取用户信息
    real_user_id = session.get('user_id')
    blog_user = User.query.get(user_id)
    current_user = User.query.get(real_user_id)
    per_blogs = Blog.query.filter_by(AuthorID=user_id)

    if user_id != real_user_id:
        # 我是否关注了他
        follower = Follow.query.filter_by(FollowerID=real_user_id, FollowingID=user_id).first()

        # 他是否关注了我
        followed = Follow.query.filter_by(FollowerID=user_id, FollowingID=real_user_id).first()

        return render_template('user_detail.html', user=blog_user, per_blogs=per_blogs,
                               current_user=current_user, follower=follower, followed=followed)
    return render_template('user_detail.html', user=blog_user, per_blogs=per_blogs,
                           current_user=current_user)


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取用户名和密码
        username = request.form['username']
        password = request.form['password']

        # 查询数据库中是否存在该用户
        user = User.query.filter_by(Username=username, Password=password).first()

        if user:
            # 登录成功，设置 session 中的 user_id
            session['user_id'] = user.UserID
            return redirect(url_for('index'))
        else:
            flash("登录失败，请检查用户名和密码。", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/delete_blog/<int:user_id>/<int:blog_id>', methods=['POST'])
def delete_blog(user_id, blog_id):
    # 删除点赞
    likes = Upvote.query.filter_by(BlogID=blog_id)
    for like in likes:
        db.session.delete(like)
    db.session.commit()

    # 删除评论
    comments = Comment.query.filter_by(BlogID=blog_id)
    for comment in comments:
        db.session.delete(comment)
    db.session.commit()

    # 删除博客
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    # print(f'blog_id:{blog_id}')

    # 重定向到首页或登录页面
    return redirect(url_for('personal_detail', user_id=user_id))


@app.route('/logout', methods=['POST'])
def logout():
    # 清除用户 session
    session.clear()

    # 重定向到首页或登录页面
    return redirect(url_for('login'))


# 忘记密码重新设置页面
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    email_form = EmailForm()
    verify_form = VerifyForm()

    session['new_username'] = email_form.new_username.data
    session['new_password'] = email_form.new_password.data
    session['email'] = email_form.email.data

    if email_form.validate_on_submit():
        email = email_form.email.data
        verification_code = generate_verification_code()

        print('1:' + verification_code)

        # msg = Message('邮箱验证', sender='1659601706@qq.com', recipients=[email])
        msg = Message('邮箱验证')
        msg.sender = '1659601706@qq.com'
        msg.recipients = [email]
        msg.body = f'您的验证码是：{verification_code}，请在页面中输入以完成验证。'

        try:
            mail.send(msg)
            flash('验证码已发送到您的邮箱，请查收。', 'success')
            session['email'] = email

            session['verification_code'] = verification_code
        except Exception as e:
            flash(f'发送验证码失败，请稍后再试。错误信息：{str(e)}', 'error')

    if verify_form.validate_on_submit():
        email = verify_form.email.data
        user_verification_code = verify_form.verification_code.data
        stored_verification_code = session.get('verification_code')

        if stored_verification_code and user_verification_code == stored_verification_code:
            flash('验证码验证通过！', 'success')
        else:
            flash('验证码验证失败，请检查输入的验证码。', 'error')

    return render_template('forget_password.html', email_form=email_form, verify_form=verify_form)


# 重置密码时的验证
@app.route('/verify_code2', methods=['POST'])
def verify_code2():
    verify_form = VerifyForm()

    stored_verification_code = session.get('verification_code')

    user_verification_code = verify_form.verification_code.data

    if stored_verification_code and user_verification_code == stored_verification_code:
        flash('验证码验证通过！', 'success')

        # 获取用户输入的注册信息
        username = session.get('new_username')
        new_password = session.get('new_password')
        email = session.get('email')
        print(username, new_password, email)

        user = User.query.filter_by(Username=username).first()
        user.Password = new_password
        db.session.commit()

        flash('密码重置成功！', 'success')

        # 清除 session 中的验证码和邮箱信息
        session.pop('verification_code', None)
        session.pop('email', None)

        return render_template('login.html')  # 注册成功后重定向到登录页面或其他页面
    else:
        flash('验证码验证失败，请检查输入的验证码。', 'error')
        return redirect(url_for('reset'))  # 验证失败时重定向到注册页面


# 注册功能
@app.route('/register', methods=['GET', 'POST'])
def register():
    email_form = EmailForm()
    verify_form = VerifyForm()

    session['new_username'] = email_form.new_username.data
    session['new_password'] = email_form.new_password.data
    session['email'] = email_form.email.data

    if email_form.validate_on_submit():
        email = email_form.email.data
        verification_code = generate_verification_code()

        print('1:' + verification_code)

        msg = Message('邮箱验证')
        msg.sender = '1659601706@qq.com'
        msg.recipients = [email]
        msg.body = f'您的验证码是：{verification_code}，请在页面中输入以完成验证。'

        try:
            mail.send(msg)
            flash('验证码已发送到您的邮箱，请查收。', 'success')
            session['email'] = email

            session['verification_code'] = verification_code
        except Exception as e:
            flash(f'发送验证码失败，请稍后再试。错误信息：{str(e)}', 'error')

    if verify_form.validate_on_submit():
        user_verification_code = verify_form.verification_code.data
        stored_verification_code = session.get('verification_code')

        if stored_verification_code and user_verification_code == stored_verification_code:
            flash('验证码验证通过！', 'success')
        else:
            flash('验证码验证失败，请检查输入的验证码。', 'error')

    return render_template('register.html', email_form=email_form, verify_form=verify_form)


# 验证
@app.route('/verify_code', methods=['POST'])
def verify_code():
    email_form = EmailForm()
    verify_form = VerifyForm()

    stored_verification_code = session.get('verification_code')

    user_verification_code = verify_form.verification_code.data

    if stored_verification_code and user_verification_code == stored_verification_code:
        flash('验证码验证通过！', 'success')

        # 获取用户输入的注册信息
        new_username = session.get('new_username')
        new_password = session.get('new_password')
        email = session.get('email')
        print(new_username, new_password, email)

        avatar = 'imgs/avatar/avatar1.jpg'
        bio = '这个人很懒，暂无介绍...'
        # 在数据库中创建新用户
        user = User(Username=new_username, Password=new_password, Email=email, Avatar=avatar, Bio=bio)
        db.session.add(user)
        db.session.commit()

        flash('用户注册成功！', 'success')

        # 清除 session 中的验证码和邮箱信息
        session.pop('verification_code', None)
        session.pop('email', None)

        return render_template('redirect_to_login.html')  # 注册成功后重定向到登录页面或其他页面
    else:
        flash('验证码验证失败，请检查输入的验证码。', 'error')
        return redirect(url_for('register'))  # 验证失败时重定向到注册页面


@app.route('/check-username')
def check_username():
    username = request.args.get('username')

    # 在数据库中检查用户名是否存在
    user = User.query.filter_by(Username=username).first()

    return jsonify({'available': user is None})


if __name__ == '__main__':
    app.run(debug=True)
