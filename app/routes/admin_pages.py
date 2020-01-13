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
    post = Blog_Post.query.order_by(-Blog_Post.id).first()
    if post is not None:
        return post.id
    else:
        return 0

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def manage_posted_images(request, blogID):
    images = []
    try_image = 0
    while True:
        try:
            try_image += 1
            file = request.files['file' + str(try_image)]
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path = 'static/blog_images/' + str(blogID)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    file.save(path + '/' + filename)
                    images.append(filename)
        except:
            break
    result_string = ""
    for image in images:
        result_string += ' ; ' + str(blogID) + '/' + image
    return result_string.replace(' ; ', '', 1)

@app.route('/admin/posts', methods=['POST', 'GET'])
@login_required
def admin_posts():
    if current_user.admin_acc == True:
        title = 'Beiträge'
        link = 'posts_link'
        if request.method == 'POST':
            posts = Blog_Post.query.order_by(-Blog_Post.id).all()
            content = f'''
            <a href="{ url_for('admin_create_post') }" class="button" style="border-radius: 50%; display: block; padding: 8px; width: 24px; height: 24px"><img src="{ url_for('static', filename='img/add-24px.svg') }" style="fill: white"/></a>
            '''
            if len(posts) == 0:
                content += '<p>Es sind keine Blogposts verfügbar.</p>'
            else:
                content += '''
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Erstelldatum</th>
                        <th>Titel</th>
                        <th>Aktionen</th>
                    </tr>
                '''
                for post in posts:
                    content += f'''
                    <tr>
                        <td>{ post.id }</td>
                        <td>{ post.time_created.__format__("%d.%m.%Y") }</tds>
                        <td><a href="{ url_for( 'blog_post', id=post.id ) }">{ post.caption }</a></td>
                        <td>
                            <a href="{ url_for( 'delete', id=post.id ) }" ><img src="{ url_for('static', filename='img/delete-24px.svg') }" /></a>
                            <a href="{ url_for( 'edit', id=post.id ) }" ><img src="{ url_for('static', filename='img/edit-24px.svg') }" /></a>
                        </td>
                    </tr>
                    '''
                content += '</table>'
            return jsonify({'body': content, 'title': title, 'url': '/admin/posts', 'link': link})
        elif request.method == 'GET':
            return render_template('user/user.html', start_link=link, title=title)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.admin_acc == True:
        title = 'Nutzer'
        link = 'user_link'
        if request.method == 'POST':
            users = User.query.order_by(User.id).all()
            content = ''
            if len(users) == 0:
                content += '<p>Es sind keine Nutzer verfügbar.</p>'
            else:
                content += '''
                <table>
                    <tr>
                        <th>User_ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Admin</th>
                    </tr>
                '''
                for user in users:
                    content += f'''
                    <tr>
                        <td>{ user.id }</td>
                        <td>{ user.username }</tds>
                        <td>{ user.email }</td>
                        <td>{ user.admin_acc }</td>
                        <td>
                            <a href="{ url_for( 'manage_admin', id=user.id ) }">
                    '''
                    if user.admin_acc:
                        content += 'Remove Admin'
                    else:
                        content += 'Make Admin'
                    content += '''
                            </a>
                        </td>
                    </tr>
                    '''
                content += '</table>'
            return jsonify({'body': content, 'title': title, 'url': '/admin/users', 'link': link})
        elif request.method == 'GET':
        	return render_template('user/user.html', start_link=link, title=title)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route('/admin/create_post', methods=['POST', 'GET'])
@login_required
def admin_create_post():
    if current_user.admin_acc == True:
        if request.method == 'GET':
            return render_template('admin/create_post.html', title='Beitrag erstellen')
        elif request.method == 'POST':
            result_string = manage_posted_images(request, max_post_id() + 1)
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
                return jsonify({"redirect": True, "url": url_for('blog')})
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
            return redirect(url_for('user_page'))
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
            result_string = manage_posted_images(request, id)
            try:
                post.caption=request.form['caption']
                post.posted_by=current_user.id
                post.body=request.form['body']
                post.images=result_string
                db.session.commit()
                return jsonify({"redirect": True, "url": url_for('user_page')})
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
            return render_template("admin/edit.html", title="Post editieren", post=post, image_sql=image_sql, tag_sql=tag_sql)
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
                    return redirect(url_for('user_page'))
                else:
                    raise Exception("Sie können den Admin-Status des Hauptadmins nicht verandern")
            else:
                raise Exception("Sie können ihren eigenen Admin-Status nicht verändern")
        except Exception as e:
            return render_template("errors/error.html", title="Error", error=e)
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")

@app.route('/admin/measurements', methods=['GET', 'POST'])
@login_required
def measurements():
    if current_user.admin_acc:
        title = 'Messungen'
        link = 'measurements_link'
        if request.method == 'GET':
            return render_template('user/user.html', start_link=link, title=title)
        elif request.method == 'POST':
            bme_vals = BME.query.order_by(-BME.id).all()
            mpu_vals = MPU.query.order_by(-MPU.id).all()
            content = ''
            if len(bme_vals) == 0:
                content += '<p>Es sind keine BME-Messungen verfügbar.</p>'
            else:
                content += '''
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Messungszeit</th>
                        <th>Temperatur</th>
                        <th>Luftfeuchte</th>
                        <th>Luftdruck</th>
                    </tr>
                '''
                for bme_val in bme_vals:
                    content += f'''
                    <tr>
                        <td>{ bme_val.id }</td>
                        <td>{ bme_val.time.__format__('%d.%m.%Y' ' ' '%H:%M:%S') }</td>
                        <td>{ bme_val.temperature }</td>
                        <td>{ bme_val.humidity }</td>
                        <td>{ bme_val.pressure }</td>
                        <td>
                        </td>
                    </tr>
                    '''
                content += '</table>'

            if len(mpu_vals) == 0:
                content += '<p>Es sind keine MPU-Messungen verfügbar.</p>'
            else:
                content += '''
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Messungsdatum</th>
                        <th>Gyroskop X</th>
                        <th>Gyroskop Y</th>
                        <th>Gyroskop Z</th>
                        <th>Beschleunigung X</th>
                        <th>Beschleunigung Y</th>
                        <th>Beschleunigung Z</th>
                        <th>Rotation X</th>
                        <th>Rotation Y</th>
                    </tr>
                '''
                for mpu_val in mpu_vals:
                    content += f'''
                    <tr>
                        <td>{ mpu_val.id }</td>
                        <td>{ mpu_val.time.__format__('%d.%m.%Y' ' ' '%H:%M:%S') }</td>
                        <td>{ mpu_val.gyroscope_x }</td>
                        <td>{ mpu_val.gyroscope_y }</td>
                        <td>{ mpu_val.gyroscope_z }</td>
                        <td>{ mpu_val.acceleration_x }</td>
                        <td>{ mpu_val.acceleration_y }</td>
                        <td>{ mpu_val.acceleration_z }</td>
                        <td>{ mpu_val.rot_x }</td>
                        <td>{ mpu_val.rot_y }</td>
                        <td>
                        </td>
                    </tr>
                    '''
                content += '</table>'
            return jsonify({'body': content, 'title': title, 'url': '/admin/measurements', 'link': link})
    else:
        return render_template("errors/error.html", title="Error", error="You're not allowed to use that page!")
