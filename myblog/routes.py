import secrets
import os
from flask_sqlalchemy import sqlalchemy
from PIL import Image
from flask import url_for, render_template, flash, redirect, request, abort, Markup
from myblog.forms import RegistrationForm, LoginForm, ChangeSettingsForm, PostForm, CommentForm, EditCommentForm
from myblog.modules import User, Post, Comment, Follow , Like
from myblog import app, db, bcrypt, loginmanager
from flask_login import login_user, logout_user, login_required, current_user
import textwrap


def saveimg (img,st = 'ProfilePics',a = 126,b=126):
    rand = secrets.token_hex(8)
    _, ex = os.path.splitext(img.filename)
    newname = rand + ex
    pfpath = os.path.join(app.root_path,'static/assets/img/'+st+'/',newname)
    thunb = Image.open(img)
    thunb.thumbnail((a, b))
    thunb.save(pfpath)
    return newname


def render_html(st):
    return Markup(st)

def simplifyText(st):
    return textwrap.shorten(st,width=516,placeholder="...")


@app.route("/")
@app.route("/Home")
def Home():
    page = request.args.get("page", 1, type=int)
    ordo = request.args.get("order")
    following_only=request.args.get("follow")
    if(not ordo):
        ordo = "time"
    if(following_only == "True"):
        following_only = True
    else:
        following_only = False

    first = Post.time.desc()
    if(ordo == "time"):
        first = Post.time.desc()
    elif (ordo == "title"):
        first = Post.title

    if(following_only and current_user.is_authenticated):
        myfollows = Follow.query.filter_by(follower_id=current_user.id)
        ty = []
        for follow in myfollows:
            ty.append(follow.followed_id)
        myPosts = Post.query.filter((Post.user_id).in_(ty)).order_by(first)
    else:
        myPosts = Post.query.order_by(first)
    myPosts = myPosts.paginate(per_page=8,page=page)

    top= User.query.order_by(User.followers.desc()).limit(10)
    return render_template("Home.html", posts=myPosts, shorten=simplifyText, render_html=render_html,us=top )


@app.route("/Register", methods=['GET', 'POST'])
def Register():
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
    forms = RegistrationForm()
    if forms.validate_on_submit():
        passhashed = bcrypt.generate_password_hash(forms.password.data).decode('utf-8')
        user = User(username=forms.username.data, email=forms.email.data, password=passhashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Account Created For {forms.username.data}', 'success')
        return redirect(url_for('UserProfile', user_name=current_user.username))
    return render_template('Register.html', title='Register', form=forms)


@app.route("/Login", methods=['GET', 'POST'])
def Login():
        if current_user.is_authenticated:
            return redirect(url_for('Home'))
        forms = LoginForm()
        if forms.validate_on_submit():
            user = User.query.filter_by(email=forms.email.data).first()
            if(user and bcrypt.check_password_hash(user.password, forms.password.data)):
                login_user(user, remember=forms.remember.data)
                nextpage = request.args.get('next')
                flash(f'Welcome {forms.email.data}', 'success')
                return redirect(nextpage) if nextpage else redirect(url_for('Home'))
            else:
                flash(f' An Error Has Occured , Check Your Email And Password', 'danger')
        return render_template('Login.html', title='Login', form=forms)


@app.route("/LogOut")
@login_required
def Logout():
    logout_user()
    return redirect(url_for('Home'))


@app.route("/UserProfile/<user_name>/")
@login_required
def UserProfile(user_name):
    _user = None
    if(user_name == current_user.username):
        _user = current_user
    else:
        _user = User.query.filter_by(username = user_name).first()
    myPosts = Post.query.filter_by(author=_user)
    return render_template("Profile.html", posts=myPosts,shorten=simplifyText,render_html=render_html,user = _user)



@app.route("/UserProfile/<user_name>/Follow/")
@login_required
def FollowProfile(user_name):
    _user = User.query.filter_by(username = user_name).first()
    obj = Follow.query.filter_by(follower_id=current_user.id,followed_id=_user.id)
    if current_user != _user:
        if obj.first():
            _user.followers = _user.followers - 1 
            db.session.delete(obj.first())
            db.session.commit()
        else:
            _user.followers = _user.followers + 1 
            fl = Follow(follower_id=current_user.id,followed_id=_user.id)
            db.session.add(fl)
            db.session.commit()
    return redirect(url_for('UserProfile',user_name=user_name))


@app.route("/Settings",methods=['GET', 'POST'])
@login_required
def Settings():
    form = ChangeSettingsForm()
    if form.validate_on_submit():
        if(form.pfp.data):
            newname = saveimg(form.pfp.data)
            current_user.pfp = newname
        if(form.pfc.data):
            newname = saveimg(form.pfc.data,"CoverPics",1920,1080)
            current_user.pfc = newname

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.activity =form.activity.data 
        current_user.description  = form.description.data  

        if form.password.data != "":
            current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
        db.session.commit()
        flash(f'Settings Changed Succefully', 'success')
        return redirect(url_for('UserProfile',user_name=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username  
        form.email.data = current_user.email
        form.activity.data = current_user.activity
        form.description.data = current_user.description      
    return render_template("Settings.html",form=form,user=current_user)


@app.route("/NewPost",methods=['GET', 'POST'])
@login_required
def NewPost():
    form = PostForm()
    if form.validate_on_submit():
        pst = Post(title=form.title.data, content=form.content.data,smallcontent=form.smallcontent.data, author=current_user)
        db.session.add(pst)
        db.session.commit()
        flash(f'Post Added Succecfully', 'success')
        return redirect(url_for('UserProfile',user_name=current_user.username))
    return render_template("NewPost.html",form=form,title="Add A New Post",leg="Add New Post",user=current_user)


@app.route("/Post/<post_id>",methods=['GET', 'POST'])
@login_required
def FullPost(post_id):
    post = Post.query.get(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        cmnt = Comment(content=form.content.data, mainpost=post,comment_author=current_user)
        db.session.add(cmnt)
        db.session.commit()
        flash(f'Comment Added Successfully', 'success')
        return redirect(url_for('FullPost',post_id=post.id))
    elif (form.is_submitted() and (not form.validate())):
        flash(f'An Error Has Occured Please Review Your Comment', 'danger')

    comments = Comment.query.filter_by(mainpost=post)
    return render_template("Post.html",title=post.title,post=post,render_html=render_html,user = post.author,form=form,form2=None,comments = comments)


@app.route("/Post/EditComment/<comment_id>/", methods=['GET', 'POST'])
@login_required
def EditComment(comment_id):

    cmnt2 = Comment.query.get(comment_id)
    post = cmnt2.mainpost

    form2 = EditCommentForm()
    if request.method == "GET":
        form2.content.data = cmnt2.content
    elif (form2.submit2.data and form2.validate()):
        cmnt2.content = form2.content.data
        db.session.commit()
        flash(f'Comment Edited Successfully', 'success')
        return redirect(url_for('FullPost',post_id=post.id))

    form = CommentForm()

    if (form.submit.data and form.validate()):
        cmnt = Comment(content=form.content.data, mainpost=post,comment_author=current_user)
        db.session.add(cmnt)
        db.session.commit()
        flash(f'Comment Added Successfully', 'success')
        return redirect(url_for('FullPost',post_id=post.id))
    elif (form.is_submitted() and (not form.validate())):
        flash(f'An Error Has Occured Please Review Your Comment', 'danger')

    
    comments = Comment.query.filter_by(mainpost=post)
    return render_template("Post.html",title=post.title,post=post,render_html=render_html,user = post.author,form2=form2,form=form,comments = comments)


@app.route("/Post/DeleteComment/<comment_id>")
@login_required
def DeleteComment(comment_id):
    comment = Comment.query.get(comment_id)

    post_id= comment.mainpost.id
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('FullPost',post_id=post_id))

@app.route("/Post/<post_id>/like",methods=["POST"])
@login_required
def LikePost(post_id):
    post = Post.query.get(post_id)
    if(post):
       
        obj = Like.query.filter_by(liker_id=current_user.id, liked_id=post_id)
        if obj.first():
            post.likes -= 1 
            db.session.delete(obj.first())
            db.session.commit()
         
        else:
            post.likes += 1 
            fl = Like.query.filter_by(liker_id=current_user.id, liked_id=post_id)
            db.session.add(fl)
            db.session.commit()
          
    return redirect(url_for('FullPost',post_id=post.id,))


@app.route("/DeletePost/<post_id>")
@login_required
def DeletePost(post_id):
    post = Post.query.get(post_id)
    if(post.author != current_user):
        abort(403)
    else:
        cmns = Comment.query.filter_by(mainpost=post)
        for cm in cmns :
            db.session.delete(cm)
        
        db.session.delete(post)
        db.session.commit()
        flash(f'Post Deleted Successfully', 'succes')
        return redirect(url_for('UserProfile',user_name=current_user.username))

@app.route("/Post/update/<post_id>",methods=['GET', 'POST'])
@login_required
def UpdatePost(post_id):
    post = Post.query.get(post_id)
    if(post.author != current_user):
        abort(403)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post.title=form.title.data
            post.content=form.content.data
            post.smallcontent=form.smallcontent.data
            db.session.commit()
            flash(f'Post Updated Succecfully', 'success')
            return redirect(url_for('FullPost',post_id=post.id))
        elif request.method=="GET":
            form.title.data = post.title
            form.smallcontent.data = post.smallcontent
            form.content.data = post.content
        return render_template("NewPost.html",form=form,title="Update Post :" + str(post_id),leg="Update Poste",user=current_user)