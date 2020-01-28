# region imports
from flask import render_template, request, jsonify, url_for, redirect
from flask_login import login_required, current_user
from sqlalchemy import extract
import re
from app.models import Blog_Post, User, Comment
from blog import app, db
# endregion

def max_post_id():
    return Blog_Post.query.order_by(-Blog_Post.id).first().id

def parse_body(input, id):
    style_conv = re.sub( r'\r\n', '<br/>', input )
    style_conv = re.sub( r'\n', '<br/>', style_conv )
    style_conv = re.sub( r"\[bold]", '<span class="fat_span">', style_conv )
    style_conv = re.sub( r"\[italic]", '<span class="italic_span">', style_conv )
    style_conv = re.sub( r"\[underline]", '<span class="underlined_span">', style_conv )

    style_conv = re.sub(  r"(\[/bold])|(\[/italic])|(\[/underline])", '</span>', style_conv )

    style_conv = re.sub( r"\[head]", '</p><h3>', style_conv )
    style_conv = re.sub( r"\[/head]", '</h3><p>', style_conv )

    list_count = len(style_conv.split("[list]"))
    for i in range(1, list_count):
        list_start = style_conv.find( "[list]" )+6
        list_end = style_conv.find( "[/list]" )
        list_string = style_conv[list_start:list_end]
        style_conv = style_conv[0: list_start:] + style_conv[list_end::]
        final_list_string = ""
        item_list = list_string.split(";")
        for list_item in item_list:
            list_item = re.sub( r"\r\n", '', list_item)
            final_list_string += '<li>- '+list_item+'</li>\n'
        style_conv = re.sub( r"\[list]", '<ul class="parse_list">'+final_list_string, style_conv, 1 )
        style_conv = re.sub( r"\[/list]", '</ul>', style_conv, 1 )

    link_count = len(style_conv.split("[link]"))
    for i in range(1, link_count):
        link_start = style_conv.find( "[link]" )+6
        link_end = style_conv.find( "[/link]" )
        link_string = style_conv[link_start: link_end]
        style_conv = re.sub( r"\[link]", '<a class="link_span" href="', style_conv, 1 )
        style_conv = re.sub( r"\[/link]", '">'+link_string+'</a>', style_conv, 1 )

    img_count = len(re.split(r'\[img([0-9]+)', style_conv))
    for i in range(1, img_count):
        img_search = re.search( r'\[img([0-9]+)]', style_conv)
        if img_search is not None:
            img_start = img_search.span()[0]+4
            img_end = img_search.span()[1]-1
            img_link = '/static/blog_images/'+str(parse_images(id)[int(style_conv[img_start:img_end])-1])
            style_conv = re.sub( r'\[img(\d+)]', '</p><a href="'+img_link+'"><img src="'+img_link+'" alt="img"></a><span class="img_text_span">', style_conv, 1 )
            style_conv = re.sub( r'\[/img]', '</span><p>', style_conv, 1 )
    style_conv = remove_empty_tags(style_conv)
    return style_conv

def parse_images(id):
    try:
        post = Blog_Post.query.get_or_404(id)
        image_list = post.images.split(" ; ")
    except:
        image_list = []
    return image_list

def parse_tags(id):
    tagReturn = ''
    try:
        post = Blog_Post.query.get_or_404(id)
        tags = post.tags
        if tags != '':
            tagList = tags.split(' ; ')
            i = 1
            for tag in tagList:
                if i != 1: 
                    tagReturn += ', '
                tagReturn += '<span class="tag_span"><a href="'+url_for('blog_tag_query', tag=tag)+'">#'+tag+'</a></span>'
                i += 1
    except:
        pass
    return tagReturn

def remove_empty_tags(input):
    input = re.sub( r'<p></p>', '', input)
    input = re.sub( r'<span class="img_text_span"></span>', '', input)
    return input

@app.route("/blog", methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
        post_count = Blog_Post.query.count()
        return render_template("blog.html", title="Blog", post_count=post_count, route="/blog")
    elif request.method == 'POST':
        id = int(request.form['blog_id'])
        try:
            post = Blog_Post.query.get_or_404(max_post_id()-id+1)
            try:
                user = User.query.get_or_404(post.posted_by).username
            except Exception:
                user = "[deleted]"
            return jsonify({"article": True, "id": post.id, "caption": post.caption, "tags": parse_tags(post.id), "posted_by": user, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
        except Exception:
            return jsonify({"article": False})

@app.route("/blog/user/<string:username>", methods=['POST', 'GET'])
def blog_user_query(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        post_count = Blog_Post.query.filter_by(posted_by=user.id).count()
    else: 
        post_count = 0
    if request.method == 'GET':
        return render_template("blog.html", title="Blog / "+username, post_count=post_count, route="/blog/user/"+username)
    elif request.method == 'POST':
        if user is not None:
            posts = Blog_Post.query.filter_by(posted_by=user.id).all()
            if posts is not None:
                try:
                    requested_post = post_count-int(request.form['blog_id'])
                    if requested_post>=0:
                        post = posts[requested_post]
                    else:
                        return jsonify({"article": False})
                except:
                    return jsonify({"article": False})
                image_list = parse_images(post.id)
                return jsonify({"article": True, "id": post.id, "caption": post.caption, "tags": parse_tags(post.id), "posted_by": user.username, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
        return jsonify({"article": False})

@app.route("/blog/date/<int:day>-<int:month>-<int:year>", methods=['POST', 'GET'])
def blog_date_query(day, month, year):
    post_count = Blog_Post.query.filter(extract('year', Blog_Post.time_created) == year, extract('month', Blog_Post.time_created) == month, extract('day', Blog_Post.time_created) == day).count()
    if request.method == 'GET':
        return render_template("blog.html", title="Blog / "+str(day)+"."+str(month)+"."+str(year), post_count=post_count, route="/blog/date/"+str(day)+"-"+str(month)+"-"+str(year))
    elif request.method == 'POST':
        posts = Blog_Post.query.filter(extract('year', Blog_Post.time_created) == year, extract('month', Blog_Post.time_created) == month, extract('day', Blog_Post.time_created) == day).all()
        if posts is not None:
            try:
                requested_post = post_count-int(request.form['blog_id'])
                if requested_post>=0:
                    post = posts[requested_post]
                else:
                    return jsonify({"article": False})
                try:
                    user = User.query.get_or_404(post.posted_by).username
                except:
                    user = "[deleted]"
                image_list = parse_images(post.id)
                return jsonify({"article": True, "id": post.id, "caption": post.caption, "tags": parse_tags(post.id), "posted_by": user, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
            except:
                return jsonify({"article": False})
        return jsonify({"article": False})

@app.route('/blog/tag/<string:tag>', methods=['POST', 'GET'])
def blog_tag_query(tag):
    posts = Blog_Post.query.filter(Blog_Post.tags.like('%{}%'.format(tag)))
    post_count = posts.count()
    if request.method == 'GET':
        return render_template("blog.html", title="Blog / #"+str(tag), post_count=post_count, route="/blog/tag/"+str(tag))
    elif request.method == 'POST':
        try:
            requested_post = post_count-int(request.form['blog_id'])
            if requested_post>=0:
                post = posts.all()[requested_post]
            else:
                return jsonify({"article": False})
            try:
                user = User.query.get_or_404(post.posted_by).username
            except:
                user = "[deleted]"
            image_list = parse_images(post.id)
            return jsonify({"article": True, "id": post.id, "info": "Aktuell gibt es noch keine Tags für Kommentare.", "caption": post.caption, "tags": parse_tags(post.id), "posted_by": user, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
        except:
            return jsonify({"article": False})

@app.route('/blog/post/<int:id>', methods=['POST', 'GET'])
def blog_post(id):
    if request.method == 'GET':
        post = Blog_Post.query.get_or_404(id)
        comment_count = Comment.query.filter_by(post=post).count()
        if post is not None:
            return render_template("blog.html", title="Beitrag", post_count=1, comment_count=comment_count, route="/blog/post/"+str(id))
    elif request.method == 'POST':
        try:
            post = Blog_Post.query.get_or_404(id)
            try:
                user = User.query.get_or_404(post.posted_by).username
            except Exception:
                user = "[deleted]"
            image_list = parse_images(id)
            return jsonify({"article": True, "id": id, "is_main_page": True, "caption": post.caption, "tags": parse_tags(id), "posted_by": user, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
        except Exception:
            return jsonify({"article": False})

@app.route('/blog/post_comment/<int:id>', methods=['POST'])
@login_required
def post_comment(id):
    print(id, request.form['body'])
    try:
        post = Blog_Post.query.get_or_404(id)
        db.session.add(
            Comment(
                post = post,
                posted_by = current_user.id,
                body = request.form['body']
            )
        )
        db.session.commit()
        return jsonify({'redirect': True})
    except:
        return jsonify({'redirect': False, 'text': 'Post was not found'})

@app.route('/blog/get_comments/<int:id>', methods=['POST'])
def get_comments(id):
    comment_id = int(request.form['comment_id'])-1
    try: 
        post = Blog_Post.query.get_or_404(id)
        try: 
            comment = post.comments[comment_id]
            try:
                user = User.query.get_or_404(comment.posted_by).username
            except:
                user = "[deleted]"
            return jsonify({"comment": True, "id": comment.id, "posted_by": user, "author_id": comment.posted_by, "body": comment.body, "date_created": comment.time_created.strftime("%d.%m.%Y"), "day": comment.time_created.day, "month": comment.time_created.month, "year": comment.time_created.year})
        except:
            return jsonify({"comment": False, "error": 'comment not found'})
    except:
        return jsonify({"comment": False, "error": 'post not found'})

@app.route('/blog/delete_comment/<int:id>', methods=['POST'])
@login_required
def delete_comment(id):
    try:
        comment = Comment.query.get_or_404(int(request.form['comment_id']))

        if current_user.id == comment.posted_by or User.query.get_or_404(comment.posted_by).admin_acc:
            db.session.delete(comment)
            db.session.commit()
            return jsonify({"comment": True})
        else:
            raise Exception()
    except:
        return jsonify({"comment": False})
