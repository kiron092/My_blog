from blog_post import *
from forms import *
from flask_gravatar import Gravatar
from functools import wraps


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


def admin_only(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        # If id is 1 continue with the route function
        if current_user.id == 1:
            return f(*args, **kwargs)
        #Otherwise  return abort with 403 error
        else:
            return abort(403)
    return decorator_function


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():
        new_user = Users(
            email=form.email.data,
            password=generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8),
            name=form.name.data
        )

        user = Users.query.filter_by(email=form.email.data).first()

        if not user:
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for('get_all_posts'))

        else:
            flash('Email already exist. Log In instead')

            return redirect(url_for('login'))
    return render_template("register.html", form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        entered_email = form.email.data
        entered_password = form.password.data

        user = Users.query.filter_by(email=entered_email).first()

        if user and check_password_hash(user.password, entered_password):
            login_user(user)
            return redirect(url_for('get_all_posts'))

        elif not user:
            flash('Email does not exist. Please try again')

        else:
            flash('Incorrect Password')

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['POST', 'GET'])
def show_post(post_id):

    requested_post = BlogPost.query.get(post_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():

        if not current_user.is_authenticated:
            flash('You need to login or register first')
            return redirect(url_for('login'))

        comment = Comment(comment=comment_form.comment.data,
                          comment_author=current_user,
                          parent_post=requested_post)

        db.session.add(comment)
        db.session.commit()

    return render_template("post.html", post=requested_post, form=comment_form, current_user=current_user,
                           gravatar=gravatar)


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=['POST', 'GET'])
@admin_only
def add_new_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=['POST', 'GET'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, current_user=current_user)


@app.route("/delete/<int:post_id>", methods=['POST', 'GET'])
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
