from flask import Flask
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '68f9b62d897d9587c6507840cdb69036'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app=app)
db = SQLAlchemy(app=app)
bcrypt = Bcrypt(app)
loginmanager = LoginManager(app)
loginmanager.login_view = 'Login'
loginmanager.login_message_category='info'

from myblog import routes