from flask import Flask, render_template, redirect, request, url_for, flash, session, send_from_directory, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import _
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
from web432.models import Users, News
from web432.database import db
from web432.forms import EditUserForm, CreateUserForm, ChangePasswordForm, NewsForm, NewsFormText
import os
import secrets
import shutil

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.role in roles:
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

def register_routes(app, role_required):
    @app.route('/index')
    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/contacts')
    def contacts():
        return render_template("contacts.html")

    @app.route('/about')
    def about():
        return render_template("about.html")

    @app.route('/facebook')
    def facebook():
        return redirect("https://www.facebook.com/projeto432hz")

    @app.route('/instagram')
    def instagram():
        return redirect("https://www.instagram.com/projeto432hz/")

    @app.route('/email')
    def email():
        return redirect("mailto:projecto432hz@gmail.com")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            # Ensure username and password were submitted
            username = request.form.get("username")
            password = request.form.get("password")

            if not username or not password:
                flash("Must provide both username and password", "danger")
                return redirect(url_for("login"))

            # Query database for username
            user = Users.query.filter_by(username=username).first()

            # Ensure username exists and password is correct
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect("/dashboard")
            else:
                flash("Invalid username and/or password", "danger")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        """Log user out"""
        logout_user()
        flash("Logout successful!", "success")
        return redirect("/")

    @app.route("/admin", methods=['GET'])
    @login_required
    @role_required('admin')
    def admin_dashboard():
        users = Users.query.all()
        return render_template('admin.html', users=Users.query.all(), edit_user_form=EditUserForm(), create_user_form=CreateUserForm())

    @app.route("/admin/change_role", methods=['POST'])
    @login_required
    @role_required('admin')
    def change_role():
        user_id = request.form.get('user_id')
        new_role = request.form.get('role')
        return change_user_role(user_id, new_role)

    @app.route("/admin/edit_user/<int:user_id>", methods=['GET', 'POST'])
    @login_required
    @role_required('admin')
    def edit_user_route(user_id):
        user_to_edit = Users.query.get(user_id)
        if not user_to_edit:
            flash("User not found", "danger")
            return redirect(url_for('admin_dashboard'))

        # Retrieve the current logged-in user
        current_logged_in_user = current_user

        if user_to_edit.id == 1 and current_logged_in_user.id != 1:
            flash("You can't edit this User", "danger")
            return redirect(url_for('admin_dashboard'))

        # Check if the logged-in user is user ID 1
        if current_logged_in_user.id == 1:
            form = EditUserForm(obj=user_to_edit, role_disabled=(user_id == 1))
        else:
            form = EditUserForm(obj=user_to_edit)

        if form.validate_on_submit():
            # Update user details
            user_to_edit.username = form.username.data
            user_to_edit.name = form.name.data
            user_to_edit.email = form.email.data
            user_to_edit.phone = form.phone.data
            
            # If the user to be edited is not user ID 1, allow changing the role
            if user_to_edit.id != 1:
                user_to_edit.role = form.role.data
            
            db.session.commit()
            flash("User details updated", "success")
            return redirect(url_for('admin_dashboard'))

        return render_template('admin.html', users=Users.query.all(), form=form)

    @app.route("/admin/reset_password", methods=['POST'])
    @login_required
    @role_required('admin')
    def reset_password():
        user_id = request.form.get('user_id')
        reset_user_password(user_id)
        return redirect(url_for('admin_dashboard'))

    @app.route("/admin/delete_user/<int:user_id>", methods=['POST'])
    @login_required
    @role_required('admin')
    def delete_user(user_id):
        # Query the database for the user
        user = Users.query.get(user_id)

        if user and user.id != 1:
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully", "success")
        elif user and user.id == 1:
            flash("You can't delete this User", "danger")
        else:
            flash("User not found", "danger")

        return redirect(url_for('admin_dashboard'))

    @app.route("/admin/create_user", methods=['GET', 'POST'])
    @login_required
    @role_required('admin')
    def create_user():
        form = CreateUserForm()

        if form.validate_on_submit():
            # Process form data for creating a new user
            new_user = Users(
                username=form.new_username.data,
                name=form.new_name.data,
                email=form.new_email.data,
                phone=form.new_phone.data,
                password=generate_password_hash("panquecas"),  # Default password
                photo='profile/logo.png'  # Default photo
            )
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully", "success")
            return redirect(url_for('admin_dashboard'))

        return render_template('admin.html', users=Users.query.all(), form=form)

    @app.route("/admin/upload_profile_pic/<int:user_id>", methods=['POST'])
    @login_required
    @role_required('admin')
    def upload_profile_pic(user_id):
        file = request.files['file']
        
        # Check if the file is present and has an allowed extension
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            subpath = 'profile'
            filepath = os.path.join(subpath, filename)
            file.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filepath))

            # Save the filepath in the database
            user = Users.query.get(user_id)
            user.photo = filepath
            db.session.commit()

            flash("Profile picture uploaded successfully", "success")
        else:
            flash("Invalid file or file type", "danger")

        return redirect(url_for('admin_dashboard'))

    @app.route('/serve-image/<subpath>/<filename>')
    def serve_image(subpath, filename):
        load_directory = app.config['LOAD_DIRECTORY']
        target_directory = os.path.join(load_directory, subpath)
        return send_from_directory(target_directory, filename)
    
    @app.route("/dashboard", methods=['GET', 'POST'])
    @login_required
    def dashboard():
        users = Users.query.all()
        change_password_form = ChangePasswordForm()

        if change_password_form.validate_on_submit():
            current_password = change_password_form.current_password.data
            new_password = change_password_form.new_password.data

            # Check if the current password is correct
            if not check_password_hash(current_user.password, current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('dashboard'))

            # Update the user's password
            current_user.password = generate_password_hash(new_password)
            db.session.commit()

            flash('Password changed successfully', 'success')
            return redirect(url_for('dashboard'))

        return render_template('dashboard.html', users=users, change_password_form=change_password_form)

    @app.route("/create_news", methods=["GET", "POST"])
    @login_required
    def create_news():
        form = NewsForm()
        form.date.data = datetime.utcnow().date()

        if form.validate_on_submit():
            try:
                # Convert news_url to file-safe name
                news_url_safe = secure_filename(form.news_url.data)

                #make the news photo directory
                news_photos_directory = os.path.join(app.config['UPLOAD_DIRECTORY'], news_url_safe)
                os.makedirs(news_photos_directory, exist_ok=True)

                # Save the cover image
                cover_image = form.cover_image.data
                cover_image_filename = secure_filename(cover_image.filename)
                cover_image_path = os.path.join(news_photos_directory, cover_image_filename)
                cover_image.save(cover_image_path)

                # Save the photos
                photos = form.photos.data
                photos_filenames = [secure_filename(photo.filename) for photo in photos]

                photos_path = []
                for i, photo in enumerate(photos):
                    photo_filename = photos_filenames[i]
                    photo_path = os.path.join(news_photos_directory, photo_filename)
                    photo.save(photo_path)
                    photos_path.append(photo_filename)

                # Create a new News post
                new_post = News(
                    news_url=news_url_safe,
                    title_en=form.title_en.data,
                    title_pt=form.title_pt.data,
                    summary_en=form.summary_en.data,
                    summary_pt=form.summary_pt.data,
                    body_en=form.body_en.data,
                    body_pt=form.body_pt.data,
                    author=current_user.username,
                    cover=cover_image_filename,
                    photos=' && '.join(photos_path),
                    photographers=form.photographers.data,
                    category=form.category.data,
                    date=form.date.data
                )

                # Save to the database
                db.session.add(new_post)
                db.session.commit()

                flash('News post created successfully!', 'success')
                return redirect(url_for('news_dashboard'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')

        return render_template('create_news.html', form=form)

    @app.route("/news_dashboard", methods=["GET"])
    @login_required
    def news_dashboard():
        all_news = News.query.all()
        return render_template('news_dashboard.html', news_posts=all_news)
    
    @app.route("/delete_news/<int:news_id>", methods=["GET"])
    @login_required
    def delete_news(news_id):
        # Get the news post by ID
        news_post = News.query.get(news_id)
        
        if news_post:
            # Delete the news post from the database
            db.session.delete(news_post)
            db.session.commit()
            
            # Delete the directory containing the news photos
            news_photos_directory = os.path.join(app.config['UPLOAD_DIRECTORY'], news_post.news_url)
            if os.path.exists(news_photos_directory):
                shutil.rmtree(news_photos_directory)
            
            flash("News post deleted successfully", "success")
        else:
            flash("News post not found", "error")
        
        # Redirect back to the news dashboard
        return redirect(url_for("news_dashboard"))

    @app.route("/edit_news/<int:news_id>", methods=["GET", "POST"])
    @login_required
    def edit_news(news_id):
        # Get the news post by ID
        news_post = News.query.get(news_id)

        if news_post:
            form = NewsForm(obj=news_post)
            form.date.data = datetime.utcnow().date()
            
            if form.validate_on_submit():
                try:
                    # Update news_url if necessary
                    if form.news_url.data != news_post.news_url:
                        # Remove the old directory
                        old_news_photos_directory = os.path.join(app.config['UPLOAD_DIRECTORY'], news_post.news_url)
                        if os.path.exists(old_news_photos_directory):
                            shutil.rmtree(old_news_photos_directory)

                        # Create new directory
                        news_url_safe = secure_filename(form.news_url.data)
                        news_photos_directory = os.path.join(app.config['UPLOAD_DIRECTORY'], news_url_safe)
                        os.makedirs(news_photos_directory, exist_ok=True)

                        # Update news post's news_url
                        news_post.news_url = news_url_safe

                    # Update the cover image
                    cover_image = form.cover_image.data
                    if cover_image:
                        cover_image_filename = secure_filename(cover_image.filename)
                        cover_image_path = os.path.join(news_photos_directory, cover_image_filename)
                        cover_image.save(cover_image_path)
                        news_post.cover = cover_image_filename

                    # Update the photos
                    photos = form.photos.data
                    if photos:
                        photos_filenames = [secure_filename(photo.filename) for photo in photos]

                        photos_path = []
                        for i, photo in enumerate(photos):
                            photo_filename = photos_filenames[i]
                            photo_path = os.path.join(news_photos_directory, photo_filename)
                            photo.save(photo_path)
                            photos_path.append(photo_filename)

                        news_post.photos = ' && '.join(photos_path)

                    # Update other fields
                    news_post.title_en = form.title_en.data
                    news_post.title_pt = form.title_pt.data
                    news_post.summary_en = form.summary_en.data
                    news_post.summary_pt = form.summary_pt.data
                    news_post.body_en = form.body_en.data
                    news_post.body_pt = form.body_pt.data
                    news_post.photographers = form.photographers.data
                    news_post.category = form.category.data
                    news_post.date = form.date.data

                    # Commit changes to the database
                    db.session.commit()

                    flash('News post updated successfully!', 'success')
                    return redirect(url_for('news_dashboard'))
                except Exception as e:
                    flash(f'Error: {str(e)}', 'danger')
            
            # Render the edit news template with the pre-filled form
            return render_template('edit_news.html', form=form, news_post=news_post)
        else:
            flash("News post not found", "error")
            return redirect(url_for("news_dashboard"))

    @app.route("/edit_news_text/<int:news_id>", methods=["GET", "POST"])
    @login_required
    def edit_news_text(news_id):
        news_post = News.query.get(news_id)
        if not news_post:
            flash("News post not found", "error")
            return redirect(url_for("news_dashboard"))

        form = NewsFormText(obj=news_post)
        form.date.data = datetime.utcnow().date()

        if form.validate_on_submit():
            try:
                # Update text content fields
                news_post.title_pt = form.title_pt.data
                news_post.title_en = form.title_en.data
                news_post.summary_pt = form.summary_pt.data
                news_post.summary_en = form.summary_en.data
                news_post.body_pt = form.body_pt.data
                news_post.body_en = form.body_en.data
                news_post.category = form.category.data
                news_post.date = form.date.data

                # Check if news_url has changed
                if form.news_url.data != news_post.news_url:
                    old_news_photos_directory = os.path.join(app.config['UPLOAD_DIRECTORY'], news_post.news_url)
                    if os.path.exists(old_news_photos_directory):
                        # Create new directory
                        news_url_safe = secure_filename(form.news_url.data)
                        news_photos_directory = os.path.join(app.config['UPLOAD_DIRECTORY'], news_url_safe)
                        os.makedirs(news_photos_directory, exist_ok=True)

                        # Update news post's news_url
                        news_post.news_url = news_url_safe

                        # Move photos to new directory
                        for filename in os.listdir(old_news_photos_directory):
                            source = os.path.join(old_news_photos_directory, filename)
                            destination = os.path.join(news_photos_directory, filename)
                            shutil.move(source, destination)

                        # Remove the old directory after moving photos
                        shutil.rmtree(old_news_photos_directory)

                db.session.commit()
                flash('Text content updated successfully!', 'success')
                return redirect(url_for('news_dashboard'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')

        return render_template('edit_news_text.html', form=form, news_post=news_post)

    @app.route("/change_status/<int:news_id>/<string:new_status>", methods=["GET", "POST"])
    @login_required
    def change_status(news_id, new_status):
        # Fetch the news post based on the news_id
        news_post = News.query.get(news_id)

        # Check if the news post exists
        if not news_post:
            abort(404)

        # Update the status of the news post
        news_post.status = new_status
        db.session.commit()

        flash(f'News post status changed to {new_status} successfully!', 'success')
        return redirect(url_for('news_dashboard'))

    @app.route("/news")
    def news():
        all_news = News.query.all()
        return render_template('news_all.html', news_posts=all_news)

    @app.route("/news/<news_url>")
    def news_url(news_url):
        # Fetch the news post based on the news_url
        news_post = News.query.filter_by(news_url=news_url).first()

        # Check if the news post exists
        if not news_post:
            abort(404)
        
        # Fetch the author
        author = Users.query.filter_by(username=news_post.author).first()
        if not author:
            abort(404)

        if news_post.status == "draft" and not current_user.is_authenticated:
            abort(404)

        # Split photos string into a list
        photos_list = news_post.photos.split(' && ')

        return render_template('news.html', news_post=news_post, author=author, photos_list=photos_list)

    @app.route("/create_project")
    @login_required
    def create_project():
        return render_template("create_project.html")

    @app.route("/projects")
    def projects():
        return render_template('projects_all.html')

    @app.route("/projects/<project_id>")
    def project_id():
        return render_template('projects_all.html')

    @app.route("/partners")
    def partners():
        return render_template('partners.html')

    @app.route('/setlocale/<lang>')
    def set_locale(lang):
        session['lang'] = lang
        return redirect(request.referrer)

    @app.before_request
    def before_request():
        # Set the language for each request based on the session
        if 'lang' not in session:
            session['lang'] = 'pt'
        request.environ['FLASK_LANG'] = session['lang']

def reset_user_password(user_id):
    # Query the database for the user
    user = Users.query.get(user_id)

    # If the user exists, reset their password to the default
    if user:
        default_password = "panquecas"
        user.password = generate_password_hash(default_password)
        db.session.commit()

def change_user_role(user_id, new_role):
    user = Users.query.get(user_id)

    if not user:
        flash("User not found", "danger")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        # Update user details
        user.role = new_role
        db.session.commit()
        flash(f"User {user.name} role updated to {user.role}", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin.html', users=Users.query.all())

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS