# region imports
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from app.models import Blog_Post, User
from app.routes.blog_pages import parse_images
from blog import ALLOWED_EXTENSIONS, db, app
from werkzeug.utils import secure_filename
import os
import shutil
# endregion


def max_post_id():
    return Blog_Post.query.order_by(-Blog_Post.id).first().id


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/admin", methods=['POST', 'GET'])
@login_required
def admin():
    if current_user.admin_acc == True:
        if request.method == 'POST':
            images = []
            try_image = 0
            while True:
                try:
                    try_image += 1
                    file = request.files['file' + str(try_image)]
                    if file.filename != '':
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            path = 'static/blog_images/' + str(max_post_id() +
                                                               1)
                            if not os.path.exists(path):
                                os.makedirs(path)
                            file.save(path + '/' + filename)
                            images.append(filename)
                except:
                    break
            result_string = ""
            for image in images:
                result_string += str(max_post_id() + 1) + '/' + image + ' ; '
            try:
                db.session.add(
                    Blog_Post(caption=request.form['caption'],
                              posted_by=current_user.id,
                              body=request.form['body'],
                              images=result_string))
                db.session.commit()
                return jsonify({"redirect": True, "url": url_for('admin')})
            except Exception as e:
                return render_template("error.html", title="Error", error=e)
        else:
            posts = Blog_Post.query.order_by(Blog_Post.time_created).all()
            users = User.query.order_by(User.id).all()
            return render_template("admin.html",
                                   title="Admin",
                                   posts=posts,
                                   users=users)
    else:
        return render_template("error.html",
                               title="Error",
                               error="You're not allowed to use that page!")


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    if current_user.admin_acc == True:
        try:
            path_to = 'static/img_waste/' + str(id)
            if os.path.exists(path_to):
                shutil.rmtree(path_to)
                os.makedirs(path_to)
            path_from = 'static/blog_images/' + str(id)
            if os.path.exists(path_from):
                shutil.move(path_from, path_to)
            db.session.delete(Blog_Post.query.get_or_404(id))
            db.session.commit()
            for post in Blog_Post.query.filter(Blog_Post.id > id).all():
                post.id = post.id - 1
                db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            return render_template("error.html", title="Error", error=e)
    else:
        return render_template("error.html",
                               title="Error",
                               error="You're not allowed to use that page!")


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
            image_string = ""
            i = 0
            for image in parse_images(id):
                img_link = '/static/blog_images/' + str(parse_images(id)[i])
                image_string += '<img src="' + img_link + '" alt="img" onclick="delete_img(' + str(
                    id
                ) + ')" style="cursor: pointer;" id="image_delete_' + str(
                    id) + '">'
                i += 1
            try:
                post = Blog_Post.query.get_or_404(id)
                image_sql = post.images
            except:
                image_sql = ""
            return render_template("edit.html",
                                   title="Edit",
                                   post=post,
                                   images=image_string,
                                   image_sql=image_sql)
    else:
        return render_template("error.html",
                               title="Error",
                               error="You're not allowed to use that page!")


@app.route("/manage_admins/<int:id>")
@login_required
def manage_admin(id):
    if current_user.admin_acc == True:
        try:
            user = User.query.get_or_404(id)
            if user.id != current_user.id:
                if user.id != 1:
                    user.set_admin(not user.admin_acc)
                    db.session.commit()
                    return redirect(url_for('admin'))
                else:
                    raise Exception(
                        "Sie können den Admin-Status des Hauptadmins nicht verandern"
                    )
            else:
                raise Exception(
                    "Sie können ihren eigenen Admin-Status nicht verändern")
        except Exception as e:
            return render_template("error.html", title="Error", error=e)
    else:
        return render_template("error.html",
                               title="Error",
                               error="You're not allowed to use that page!")
