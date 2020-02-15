# region imports
from blog import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# endregion

class Blog_Post(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String, nullable=False)

    posted_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    time_created = db.Column(db.DateTime, default=datetime.now())
    tags = db.Column(db.String)
    comments = db.relationship('Comment', backref='post')

    body = db.Column(db.String, nullable=False)
    images = db.Column(db.String)

    def __repr__(self):
        return '<Blog_Post %r>' % self.id

@login.user_loader
def load_user(id):
    return User.query.get(id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(120))
    email = db.Column(db.String, nullable=False, unique=True)
    admin_acc = db.Column(db.Boolean, default=False, nullable=False)
    is_active = True
    is_authenticated = True

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    def set_admin(self, is_admin):
        self.admin_acc = is_admin

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'))
    time_created = db.Column(db.DateTime, default=datetime.now())
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    body = db.Column(db.String)

class BME(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)

    temperature = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    pressure = db.Column(db.Integer)

class MPU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)

    gyroscope_x = db.Column(db.Integer)
    gyroscope_y = db.Column(db.Integer)
    gyroscope_z = db.Column(db.Integer)

    acceleration_x = db.Column(db.Integer)
    acceleration_y = db.Column(db.Integer)
    acceleration_z = db.Column(db.Integer)

    rot_x = db.Column(db.Integer)
    rot_y = db.Column(db.Integer)

class NEO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)

    data = db.Column(db.String)