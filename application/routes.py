from flask import render_template, redirect, url_for, flash,request
from flask_login import login_user, login_required, logout_user, current_user
from application import app
from application.models import *
from application.forms import *
from application.utils import save_image
import os
import sqlite3

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            return redirect(url_for('profile', username=current_user.username))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', title="Login", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))

    form = SignUpForm()  

    if form.validate_on_submit():
        username = form.username.data
        fullname = form.fullname.data 
        email    = form.email.data
        password = form.password.data



        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
        else:

            user = User(username=username, fullname=fullname,email=email, password=password)

            db.session.add(user)
            db.session.commit()

            login_user(user)

            return redirect(url_for('profile', username=current_user.username))

    return render_template('signup.html', title="Signup", form=form)


# @app.route('/profile')
# @login_required
# def perofile():
#     return render_template('profile.html', title=f'{current_user.fullname} Profile')

@app.route('/<string:username>')
@login_required
def profile(username):
    default_picture_url = "/static/images/profile.png"
    return render_template('profile.html',default_picture_url=default_picture_url)
    


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = CreatePostForm()

    if form.validate_on_submit():
        post = Post(
            author_id = current_user.id,
            caption = form.caption.data
        )
        post.photo = save_image(form.post_pic.data)
        db.session.add(post)
        db.session.commit()
        flash('Your image has been posted ❤!', 'success')
    
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author_id = current_user.id)\
            .order_by(Post.post_date.desc())\
            .paginate(page=page, per_page=3)

    return render_template('index.html', title='Home', form=form, posts=posts)





@app.route('/forgotpassword')
def forgotpassword():
    form = ForgotPasswordForm()
    return render_template('forgotpassword.html', title='Forgot Password', form=form)


@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = EditProfileForm()

    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        if form.username.data != user.username:
            user.username = form.username.data
        user.fullname = form.fullname.data
        user.bio = form.bio.data

        if form.profile_pic.data:
            pass

        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    form.username.data = current_user.username
    form.fullname.data = current_user.fullname
    form.bio.data = current_user.bio
    
    return render_template('editprofile.html', title=f'Edit {current_user.username} Profile', form=form)


@app.route('/resetpassword')
def resetpassword():
    form = ResetPasswordForm()
    return render_template('resetpassword.html', title='Reset Password', form=form)

@app.route('/verificationpassword')
def verificationpassword():
    form = VerificationResetPasswordForm()
    return render_template('verificationpassword.html', title='Verification Password', form=form)

@app.route('/createpost')
def createpost():
    form = CreatePostForm()

    if form.validate_on_submit():
        post = Post(
            author_id = current_user.id,
            caption = form.caption.data
        )
        post.photo = save_image(form.post_pic.data)
        db.session.add(post)
        db.session.commit()
        flash('your image has been posted ❤️','success')

    posts = Post.query.filter_by(author_id = current_user.id).all()

    return render_template('index.html', title='Home', form=form, posts=posts)


@app.route('/editpost')
def editpost():
    form = EditPostForm()
    return render_template('editpost.html', title='Edit Post', form=form)

@app.route('/about')
def about():
    return render_template('about.html', title='About')



if __name__ == '__main__':
    app.run(debug=True)