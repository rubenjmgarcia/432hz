from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, SelectField, PasswordField, TextAreaField, FileField, FieldList, FormField
from wtforms.validators import DataRequired, EqualTo

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Update')

class CreateUserForm(FlaskForm):
    new_username = StringField('Username', validators=[DataRequired()])
    new_name = StringField('Name', validators=[DataRequired()])
    new_email = StringField('Email', validators=[DataRequired()])
    new_phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Create User')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

class PhotoForm(FlaskForm):
    photo = FileField('Photo Upload', validators=[DataRequired()])
    photographer_name = StringField('Photographer Name', validators=[DataRequired()])

class NewsForm(FlaskForm):
    news_url = StringField('News URL', validators=[DataRequired()])
    title_pt = StringField('Title (PT)', validators=[DataRequired()])
    title_en = StringField('Title (EN)', validators=[DataRequired()])
    summary_pt = CKEditorField('Summary (PT)', validators=[DataRequired()])
    summary_en = CKEditorField('Summary (EN)', validators=[DataRequired()])
    news_cover_image = FileField('News Cover Image', validators=[DataRequired()])
    image_uploads = FieldList(FormField(PhotoForm), min_entries=1, max_entries=10)
    news_text_pt = CKEditorField('News Text (PT)', validators=[DataRequired()])
    news_text_en = CKEditorField('News Text (EN)', validators=[DataRequired()])
    category = SelectField('Category', choices=[('sports', 'Sports'), ('politics', 'Politics'), ('entertainment', 'Entertainment')], validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    submit = SubmitField('Create News Post')