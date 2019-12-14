# region imports
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from app.models import Blog_Post, User, BME, MPU
from app.routes.blog_pages import parse_images
from blog import ALLOWED_EXTENSIONS, db, app
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime
# endregion

def max_post_id():
    return Blog_Post.query.order_by(-Blog_Post.id).first().id

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def manage_posted_images(request):
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
        result_string += ' ; ' + str(max_post_id() + 1) + '/' + image
    return result_string.replace(' ; ', '', 1)

@app.route('/admin/posts', methods=['GET'])
@login_required
def admin_posts():
    if current_user.admin_acc == True:
        posts = Blog_Post.query.order_by(-Blog_Post.id).all()
        return render_template("admin/posts.html", title="Admin", posts=posts)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    if current_user.admin_acc == True:
        users = User.query.order_by(User.id).all()
        return render_template("admin/users.html", title="Admin", users=users)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route('/admin/create_post', methods=['POST', 'GET'])
@login_required
def admin_create_post():
    if current_user.admin_acc == True:
        if request.method == 'GET':
            return render_template('admin/create_post.html', title='Beitrag erstellen')
        elif request.method == 'POST':
            result_string = manage_posted_images(request)
            try:
                db.session.add(
                    Blog_Post(
                        caption=request.form['caption'],
                        tags=request.form['tags'],
                        posted_by=current_user.id,
                        body=request.form['body'],
                        images=result_string
                    )
                )
                db.session.commit()
                return jsonify({"redirect": True, "url": url_for('admin_posts')})
            except Exception as e:
                return render_template("errors/error.html", title="Error", error=e)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/admin/delete/<int:id>")
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
            return redirect(url_for('admin_posts'))
        except Exception as e:
            return render_template("errors/error.html", title="Error", error=e)
    else:
        return render_template("errors/error.html",
                               title="Error",
                               error="You're not allowed to use that page!")

@app.route("/admin/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def edit(id):
    if current_user.admin_acc == True:
        post = Blog_Post.query.get_or_404(id)
        if request.method == 'POST':
            result_string = manage_posted_images(request)
            try:
                post.caption=request.form['caption']
                post.posted_by=current_user.id
                post.body=request.form['body']
                post.images=result_string
                db.session.commit()
                return jsonify({"redirect": True, "url": url_for('admin_posts')})
            except Exception as e:
                return render_template("errors/error.html", title="Error", error=e)
        else:
            try:
                image_sql = post.images
            except:
                image_sql = ''
            try:
                tag_sql = post.tags
            except:
                tag_sql = ''
            return render_template("admin/edit.html", title="Edit", post=post, image_sql=image_sql, tag_sql=tag_sql)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route("/admin/manage_admins/<int:id>")
@login_required
def manage_admin(id):
    if current_user.admin_acc == True:
        try:
            user = User.query.get_or_404(id)
            if user.id != current_user.id:
                if user.id != 1:
                    user.set_admin(not user.admin_acc)
                    db.session.commit()
                    return redirect(url_for('admin_users'))
                else:
                    raise Exception(
                        "Sie können den Admin-Status des Hauptadmins nicht verandern"
                    )
            else:
                raise Exception(
                    "Sie können ihren eigenen Admin-Status nicht verändern")
        except Exception as e:
            return render_template("errors/error.html", title="Error", error=e)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")


@app.route('/admin/measurements', methods=['GET'])
@login_required
def measurements():
    if current_user.admin_acc:
        bme_vals = BME.query.order_by(-BME.id).all()
        mpu_vals = MPU.query.order_by(-MPU.id).all()
        return render_template("admin/measurements.html", title="Messungen", bme_vals=bme_vals, mpu_vals=mpu_vals)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route('/admin/post_bme', methods=['POST'])
@login_required
def post_bme():
    if current_user.admin_acc:
        try:
            db.session.add(
                BME(
                    time = datetime.strptime(request.form['time'], '%Y-%m-%d %H:%M:%S'),
                    temperature = request.form['temperature'],
                    humidity = request.form['humidity'],
                    pressure = request.form['pressure']
                )
            )
            db.session.commit()
            return jsonify({'time': request.form['time'], 'temperature': request.form['temperature'], 'humidity': request.form['humidity'], 'pressure': request.form['pressure']})
        except Exception as e:
            print(e)
            return render_template("errors/error.html", title="Error", error=e)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route('/admin/post_mpu', methods=['POST'])
@login_required
def post_mpu():
    if current_user.admin_acc:
        try:
            db.session.add(
                MPU(
                    time = datetime.strptime(request.form['time'], '%Y-%m-%d %H:%M:%S'),
                    gyroscope_x = request.form['gyroscope_x'],
                    gyroscope_y = request.form['gyroscope_y'],
                    gyroscope_z = request.form['gyroscope_z'],

                    acceleration_x = request.form['acceleration_x'],
                    acceleration_y = request.form['acceleration_y'],
                    acceleration_z = request.form['acceleration_z'],

                    rot_x = request.form['rot_x'],
                    rot_y = request.form['rot_y']
                )
            )
            db.session.commit()
            return jsonify({'time': request.form['time'], 'temperature': request.form['temperature'], 'humidity': request.form['humidity'], 'pressure': request.form['pressure']})
        except Exception as e:
            print(e)
            return render_template("errors/error.html", title="Error", error=e)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")