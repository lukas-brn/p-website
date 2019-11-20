from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog_posts.db'
db = SQLAlchemy(app)

class Blog_Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.datetime.now() )

    def __repr__(self):
        return '<Blog_Post %r>' % self.id

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/blog")
def blog():
    tasks = Blog_Post.query.order_by(Blog_Post.time_created).all()
    return render_template("blog.html", tasks=tasks)

@app.route("/console", methods=['POST', 'GET'])
def console():

    # TODO: Add login, so only andims can post

    if request.method == 'POST':
        caption_content = request.form['caption']
        body_content = request.form['body']
        new_post = Blog_Post(caption=caption_content, body=body_content)

        try: 
            db.session.add(new_post)
            db.session.commit()
            return redirect("/console")
        except: 

            # TODO: Add detailed error message

            return 'There was an issue adding the post!'

    else:
        tasks = Blog_Post.query.order_by(Blog_Post.time_created).all()
        return render_template("console.html", tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):

    # TODO: Add login, so only andims can delete posts

    to_delete = Blog_Post.query.get_or_404(id)

    try: 
        db.session.delete(to_delete)
        db.session.commit()
        return redirect("/console")
    except: 

        # TODO: Add detailed error message

        return 'There was an issue removing the post!'

@app.route("/edit/<int:id>", methods=['POST', 'GET'])
def edit(id):
    
    # TODO: Add login, so only andims can edit posts

    task = Blog_Post.query.get_or_404(id)

    if request.method == 'POST':
        task.caption = request.form['caption']
        task.body = request.form['body']
        try: 
            db.session.commit()
            return redirect("/console")
        except: 

            # TODO: Add detailed error message

            return 'There was an issue editing the post!'
    else:
        return render_template("edit.html", task=task)

if __name__ == "__main__":
    app.run()
