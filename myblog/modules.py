from datetime import datetime
from myblog import db, loginmanager
from flask_login import UserMixin


@loginmanager.user_loader
def login_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    pfp = db.Column(db.String(20), nullable=False, default="defaultpfp.png")
    pfc = db.Column(db.String(20), nullable=False, default="defaultpfp.png")
    password = db.Column(db.String(16), nullable=False)
    username = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(45), nullable=False)

    description = db.Column(db.String(256), default="", nullable=False)
    activity = db.Column(db.String(126), default="I'm Someone :)", nullable=False)
    followers = db.Column(db.Integer, nullable=False , default = 0)

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='comment_author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.password}','{self.pfp}','{self.pfc}','{self.description}','{self.activity}','{self.followers}')"


class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    smallcontent = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, nullable=False,default=0)

    comments = db.relationship('Comment', backref='mainpost', lazy=True)

    def __repr__(self):
        return f"Post( '{self.title}','{self.time}' )"


class Comment(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post( '{self.mainpost.id}','{self.time}' )"


class Follow(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer,  nullable=False)
    followed_id = db.Column(db.Integer,  nullable=False)

    def __repr__(self):
        return f"Post( '{self.follower_id}','{self.followed_id}' )"


class Like(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    liker_id = db.Column(db.Integer,  nullable=False)
    liked_id = db.Column(db.Integer,  nullable=False)