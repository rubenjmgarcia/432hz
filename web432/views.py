from flask import Flask, render_template, redirect, request, url_for, flash, session, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import _
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from web432.models import Users
from web432.database import db
from web432.forms import EditUserForm, CreateUserForm, ChangePasswordForm, NewsForm
import os
import secrets

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

    @app.route("/create_news")
    @login_required
    def create_news():
        form = NewsForm()
        if form.validate_on_submit():
            # Process the form data and save the news post
            flash('News post created successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('create_news.html', form=form)

    @app.route("/news")
    def news():
        return render_template('news_all.html')

    @app.route("/news/<news_id>")
    def news_id():
        return render_template('news_all.html')

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