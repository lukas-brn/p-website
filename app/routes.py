from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from blog import app, db
from app.models import Blog_Post, User
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm

# @app.context_processor
# def inject_login_status():
#     return dict(login_status=current_user.is_authenticated)

@app.route("/")
def index():
    return render_template("index.html", title="Startseite")

@app.route("/blog", methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
        post_count = Blog_Post.query.count()
        return render_template("blog.html", title="Blog", post_count=post_count, route="/blog")
    elif request.method == 'POST':
        try:
            post = Blog_Post.query.get_or_404(request.form['blog_id'])
            try:
                user = User.query.get_or_404(post.posted_by).username
            except Exception:
                user = "[deleted]"
            return jsonify({"article": True, "caption": post.caption, "posted_by": user, "body": post.body, "date_created": post.time_created.strftime("%d.%m.%Y")})
        except Exception:
            return jsonify({"article": False})

@app.route("/blog/<string:username>", methods=['POST', 'GET'])
def blog_user_query(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is not None:
            post_count = Blog_Post.query.filter_by(posted_by=user.id).count()
        else: 
            post_count = 0
        return render_template("blog.html", title="Blog / "+username, post_count=post_count, route="/blog/"+username)
    elif request.method == 'POST':
        user = User.query.filter_by(username=username).first()
        if user is not None:
            posts = Blog_Post.query.filter_by(posted_by=user.id).all()
            if posts is not None:
                try:
                    post = posts[int(request.form['blog_id'])-1]
                except Exception:
                    return jsonify({"article": False})
                return jsonify({"article": True, "caption": post.caption, "posted_by": user.username, "body": post.body, "date_created": post.time_created.strftime("%d.%m.%Y")})
            else: 
                return jsonify({"article": False})
        else: 
            return jsonify({})

@app.route("/admin", methods=['POST', 'GET'])
@login_required
def admin():
    if current_user.admin_acc == True:
        if request.method == 'POST':
            try: 
                db.session.add(Blog_Post(caption=request.form['caption'], posted_by=current_user.id, body=request.form['body']))
                db.session.commit()
                return redirect(url_for('admin'))
            except Exception as e: 
                return render_template("error.html", title="Error", error=e)      
        else:
            posts = Blog_Post.query.order_by(Blog_Post.time_created).all()
            users = User.query.order_by(User.id).all()
            return render_template("admin.html", title="Admin", posts=posts, users=users)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    if current_user.admin_acc == True:
        try: 
            db.session.delete(Blog_Post.query.get_or_404(id))
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e: 
                return render_template("error.html", title="Error", error=e)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit(id):
    if current_user.admin_acc == True:
        post = Blog_Post.query.get_or_404(id)

        if request.method == 'POST':
            post.caption = request.form['caption']
            post.body = request.form['body']
            try: 
                db.session.commit()
                return redirect(url_for('admin'))
            except Exception as e: 
                return render_template("error.html", title="Error", error=e)
        else:
            return render_template("edit.html", title="Edit", post=post)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/manage_admins/<int:id>")
@login_required
def manage_admin(id):
    if current_user.admin_acc == True:
        try: 
            user = User.query.get_or_404(id)
            if current_user.id != user.id:
                user.set_admin(not user.admin_acc)
                db.session.commit()
                return redirect(url_for('admin'))
            else:
                raise Exception("Sie können nicht ihren eigenen Admin-Status verändern")
        except Exception as e: 
                return render_template("error.html", title="Error", error=e)
    else:
        return render_template("error.html", title="Error", error="You're not allowed to use that page!")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="404")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('login.html', title='Login', form=form)
    elif request.method == 'POST':
        form = request.form
        user = User.query.filter_by(username=form['username'].strip()).first()
        if user is None or not user.check_password(form['password'].strip()):
            return jsonify({"text": "Benutzername oder Passwort ist falsch.", "redirect": False})
        else: 
            login_user(user, remember=form['remember_me'])
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return jsonify({"text": next_page, "redirect": True})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        form = RegistrationForm()
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('register.html', title='Register', form=form)
    elif request.method == 'POST':
        form = request.form
        if User.query.filter_by(username=form['username'].strip()).first() is not None:
            return jsonify({"text": "Bitte wählen Sie einen anderen Benutzernamen.", "redirect": False})
        elif User.query.filter_by(email=form['email'].strip()).first() is not None:
            return jsonify({"text": "Bitte wählen Sie eine andere Email-Addresse.", "redirect": False})
        else: 
            user = User(username=form['username'].strip(), email=form['email'].strip())
            user.set_password(form['password'].strip())
            db.session.add(user)
            db.session.commit()
            return jsonify({"text": url_for('login'), "redirect": True})

@app.route('/user', methods=['GET'])
@login_required
def user_page():
    return render_template('user_page.html', title='User')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'GET':
        form = ChangePasswordForm()
        return render_template('change_password.html', title='Passwort ändern', form=form)
    else:
        form = request.form
        if current_user.check_password(form['password']):
            if form['password2'] == form['password3']:
                current_user.set_password(form['password2'])
                db.session.commit()
                return jsonify({"text": url_for('user_page'), "redirect": True})
            else:
                return jsonify({"text": "Die 2 neuen Passwörter stimmen nicht überein.", "redirect": False})
        else: 
            return jsonify({"text": "Das ursprüngliche Passwort passt nicht.", "redirect": False})
        