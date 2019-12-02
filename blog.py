# region imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
# endregion

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blog_posts.db',
    DEBUG = True,
    SECRET_KEY = '/x83j/xe7/x97/x9e///xf1/x17/xca/xd2/xde/x8f/xa9S/xca/xce/xad/x7f}/x03/x9d{/x14/xfe/x9b/xb1$/x143/xd5n~',
    SQLALCHEMY_TRACK_MODIFICATIONS = False
)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect()
csrf.init_app(app)
login = LoginManager(app)
login.login_view = 'login'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

from app.routes_main import *
from app.models import *

if __name__ == "__main__":
    db.create_all()

    try: 
        # delete a user by id
        # db.session.delete(User.query.get_or_404(1))
        # db.session.commit()

        User.query.get_or_404(1).admin_acc = True
        db.session.commit()
        pass
    except:
        pass

    app.run(use_evalex=False)  # remove in production version