# region imports
from flask import render_template, request, jsonify
from sqlalchemy import extract
import re
from app.models import Blog_Post, User
from blog import app
# endregion

def parse_body(input, id):
    style_conv = re.sub( r'\r\n', '<br/>', input )
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
    style_conv = remove_empty_p_tags(style_conv)
    return style_conv

def parse_images(id):
    try:
        post = Blog_Post.query.get_or_404(id)
        image_list = post.images.split(" ; ")
        image_list.pop()
        return image_list
    except:
        return []

def remove_empty_p_tags(input):
    input = re.sub( r'<p></p>', '', input)
    return input

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
            return jsonify({"article": True, "id": post.id, "caption": post.caption, "posted_by": user, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
        except Exception:
            print("Not a post: "+str(request.form['blog_id']))
            return jsonify({"article": False})

@app.route("/blog/user/<string:username>", methods=['POST', 'GET'])
def blog_user_query(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user is not None:
            post_count = Blog_Post.query.filter_by(posted_by=user.id).count()
        else: 
            post_count = 0
        return render_template("blog.html", title="Blog / "+username, post_count=post_count, route="/blog/user/"+username)
    elif request.method == 'POST':
        user = User.query.filter_by(username=username).first()
        if user is not None:
            posts = Blog_Post.query.filter_by(posted_by=user.id).all()
            if posts is not None:
                try:
                    post = posts[int(request.form['blog_id'])-1]
                except Exception:
                    return jsonify({"article": False})
                image_list = parse_images(post.id)
                return jsonify({"article": True, "id": post.id, "caption": post.caption, "posted_by": user.username, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
        return jsonify({"article": False})

@app.route("/blog/date/<int:day>-<int:month>-<int:year>", methods=['POST', 'GET'])
def blog_date_query(day, month, year):
    if request.method == 'GET':
        post_count = Blog_Post.query.filter(extract('year', Blog_Post.time_created) == year, extract('month', Blog_Post.time_created) == month, extract('day', Blog_Post.time_created) == day).count()
        return render_template("blog.html", title="Blog / "+str(day)+"."+str(month)+"."+str(year), post_count=post_count, route="/blog/date/"+str(day)+"-"+str(month)+"-"+str(year))
    elif request.method == 'POST':
        posts = Blog_Post.query.filter(extract('year', Blog_Post.time_created) == year, extract('month', Blog_Post.time_created) == month, extract('day', Blog_Post.time_created) == day).all()
        if posts is not None:
            try:
                post = posts[int(request.form['blog_id'])-1]
                try:
                    user = User.query.get_or_404(post.posted_by).username
                except Exception:
                    user = "[deleted]"
                image_list = parse_images(post.id)
                return jsonify({"article": True, "id": post.id, "caption": post.caption, "posted_by": user, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
            except Exception:
                return jsonify({"article": False})
        return jsonify({"article": False})

@app.route('/blog/post/<int:id>', methods=['POST', 'GET'])
def blog_post(id):
    if request.method == 'GET':
        post = Blog_Post.query.get_or_404(id)
        if post is not None:
            return render_template("blog.html", title="Beitrag", post_count=1, route="/blog/post/"+str(id), id=str(id))
    elif request.method == 'POST':
        try:
            post = Blog_Post.query.get_or_404(id)
            try:
                user = User.query.get_or_404(post.posted_by).username
            except Exception:
                user = "[deleted]"
            image_list = parse_images(id)
            return jsonify({"article": True, "id": id, "is_main_page": True, "caption": post.caption, "posted_by": user, "body": parse_body(post.body, post.id), "date_created": post.time_created.strftime("%d.%m.%Y"), "day": post.time_created.day, "month": post.time_created.month, "year": post.time_created.year})
        except Exception:
            return jsonify({"article": False})