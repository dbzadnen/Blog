from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField
from myblog import ckeditor, bcrypt
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from myblog.modules import User, Post
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(4, 16)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired(), Length(4, 16)])
    confirmpassword = PasswordField("confirmpassword", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")
  
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if(user):
            raise ValidationError('Username Already Exist , Choose Another One ^^ ??')
                
    def validate_email(self, email):
        user1 = User.query.filter_by(email=email.data).first()
        if(user1):
            raise ValidationError('Email Already Exist , Maybe You Meant To Log In ??')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired(), Length(4, 16)])
    remember = BooleanField("remember")
    submit = SubmitField("Login")


class ChangeSettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(4, 16)])

    email = StringField('Email', validators=[DataRequired(), Email()])
    pfp = FileField("Update Your Profile Picture",validators= [FileAllowed(['png','jpg'])])
    pfc = FileField("Update Your Profile Cover",validators= [FileAllowed(['png','jpg'])])

    activity = StringField('Activity ( Student , Lawyer etc.. ) ', validators=[Length(0, 200)])
    description = StringField('Describe yourself in few words :)  ', validators=[Length(0, 326) ])

    password = PasswordField("Password")
    submit = SubmitField("Change Settings")
  
    def validate_username(self, username):
        if(current_user.username != username.data):
            user = User.query.filter_by(username=username.data).first()
            if(user):
                raise ValidationError('Username Already Exist , Choose Another One ^^ ??')
                
    def validate_email(self, email):
        if(current_user.email != email.data):
            user1 = User.query.filter_by(email=email.data).first()
            if(user1):
                raise ValidationError('Email Already Exist , Change Your Email ??')

    def validate_password(self, password):
        if (password.data != "" and not (len(password.data) > 3 and len(password.data) <= 16)):
            raise ValidationError('Field need to be between 4 and 16 characters ')
        

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(3, 36)])
    smallcontent = TextAreaField('Content Presentation', validators=[DataRequired(),Length(3,320)])
    content = CKEditorField('Full Content', validators=[DataRequired(),Length(12)])
    submit = SubmitField("Post Article")

    
class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(),Length(3, 356)])
    submit = SubmitField("Submit Comment")


class EditCommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(),Length(3, 356)])
    submit2 = SubmitField("Edit Comment")