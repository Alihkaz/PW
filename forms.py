from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Skill Title", validators=[DataRequired()])
    icon = StringField("Skill Logo URL", validators=[DataRequired()])
    body = CKEditorField("Skill Description", validators=[DataRequired()])
    submit = SubmitField("Submit Skill")



# WTForm for creating a about caption
class CreateAboutForm(FlaskForm):
    title = StringField("About Title", validators=[DataRequired()])
    body = CKEditorField("About Description", validators=[DataRequired()])
    submit = SubmitField("Submit About")

# WTForm for creating a blog post
class CreateProjectForm(FlaskForm):
    body = CKEditorField("projects Description", validators=[DataRequired()])
    submit = SubmitField("Submit Projects")


# WTForm for creating a registration form 
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up !")



# WTForm for creating a registration form 
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In !")

