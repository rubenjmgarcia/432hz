from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, PasswordField, TextAreaField, FileField, FieldList, FormField, MultipleFileField
from wtforms.validators import DataRequired, EqualTo, Email

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Update')

class CreateUserForm(FlaskForm):
    new_username = StringField('Username', validators=[DataRequired()])
    new_name = StringField('Name', validators=[DataRequired()])
    new_email = StringField('Email', validators=[DataRequired(), Email()])
    new_phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Create User')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

class NewsForm(FlaskForm):
    news_url_en = StringField('News URL (EN)', validators=[DataRequired()])
    news_url_pt = StringField('News URL (PT)', validators=[DataRequired()])
    title_pt = StringField('Title (PT)', validators=[DataRequired()])
    title_en = StringField('Title (EN)', validators=[DataRequired()])
    summary_pt = CKEditorField('Summary (PT)', validators=[DataRequired()])
    summary_en = CKEditorField('Summary (EN)', validators=[DataRequired()])
    body_pt = CKEditorField('Body (PT)', validators=[DataRequired()])
    body_en = CKEditorField('Body (EN)', validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[DataRequired()])
    photos = MultipleFileField('Photos Upload', validators=[DataRequired()])
    photographers = StringField('Photographers', validators=[DataRequired()])
    category = SelectField('Category', choices=[('art', 'Art'), ('science', 'Science'), ('community', 'Community')], validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    submit = SubmitField('Create News Post')

class NewsFormText(FlaskForm):
    news_url_en = StringField('News URL (EN)', validators=[DataRequired()])
    news_url_pt = StringField('News URL (PT)', validators=[DataRequired()])
    title_pt = StringField('Title (PT)', validators=[DataRequired()])
    title_en = StringField('Title (EN)', validators=[DataRequired()])
    summary_pt = CKEditorField('Summary (PT)', validators=[DataRequired()])
    summary_en = CKEditorField('Summary (EN)', validators=[DataRequired()])
    body_pt = CKEditorField('Body (PT)', validators=[DataRequired()])
    body_en = CKEditorField('Body (EN)', validators=[DataRequired()])
    category = SelectField('Category', choices=[('art', 'Art'), ('science', 'Science'), ('community', 'Community')], validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    submit = SubmitField('Edit News Post')