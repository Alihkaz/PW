from flask import Flask, abort, render_template, redirect, url_for, flash 
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user 
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash 


# Importing  forms from the forms.py
from forms import CreatePostForm , RegisterForm , LoginForm , CreateAboutForm , CreateProjectForm


#**************************************************************************#
app = Flask(__name__)
import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
ckeditor = CKEditor(app)
Bootstrap5(app)


#**************************************************************************#

# Configuring Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


#**************************************************************************#

# Creating a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#**************************************************************************#







# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy()
db.init_app(app)


#**************************************************************************#

# CREATE TABLE for users data IN DB
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    
    

#**************************************************************************#

# CONFIGURING TABLE for the skills  data in the db
class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    body = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(1000), nullable=False)

    

# CONFIGURING TABLE for the about_me data in the db
class About(db.Model):
    __tablename__ = "about"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    body = db.Column(db.Text, nullable=False)



#**************************************************************************#

# CONFIGURING TABLE for the projects data in the db
class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    
    
   
#**************************************************************************#





with app.app_context():
    db.create_all()



#**************************************************************************#

#creating only admins decorator 
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if (current_user.id) != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function





#**************************************************************************#


#**************************************************************************#


@app.route('/')
def home():

    Projects=db.session.execute(db.select(Project))
    pdata = Projects.scalars().all()

    Abouts = db.session.execute(db.select(About))
    about = Abouts.scalars().all()

    result = db.session.execute(db.select(Skill))
    skills = result.scalars().all()
  
    users = db.session.execute(db.select(User))
    ussers = users.scalars().all()
    
    return render_template("index.html",
                           all_skill=skills,
                           log_in=current_user.is_authenticated,
                           userdata=ussers,
                           aboutdata=about,
                           projectsdata=pdata)


#**************************************************************************#







@app.route('/register' , methods=["GET", "POST"])
def register():


    form = RegisterForm()
    if form.validate_on_submit():


     # checking if the User already exists

      email=form.email.data
      user= db.session.execute(db.select(User).where(User.email == email)).scalar()
      if user:
          flash("You've already signed up with that email, log in instead!")
          return redirect(url_for('login'))
    


      else:
          new_user = User(
                email=form.email.data,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256',salt_length=8),
                name=form.name.data)
          db.session.add(new_user)
          db.session.commit()
          login_user(new_user)
          return redirect(url_for("home"))
    

    
    return render_template("Register.html", form=form ,log_in=current_user.is_authenticated)






#**************************************************************************#




@app.route('/login' , methods=["GET", "POST"])
def login():

    form=LoginForm()

    if form.validate_on_submit():

          entered_email = form.email.data
          entered_password = form.password.data
          user_data= db.session.execute(db.select(User).where(User.email == entered_email)).scalar()
      
          if not user_data:
              flash("That email does not exist, please try again.")
              return redirect(url_for('login'))



          else: 
            email_saved_hash = user_data.password
            checking_password_hash = check_password_hash(email_saved_hash, entered_password)#returns Bool

            if checking_password_hash :
                login_user(user_data)
                return redirect(url_for("home"))

            elif not checking_password_hash:
                flash('Password incorrect, please try again.')
                return redirect(url_for('login'))
    
            
        

  
    return render_template("login.html" , form=form ,log_in=current_user.is_authenticated)






#**************************************************************************#



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


#**************************************************************************#











#**************************************************************************#


@app.route("/new-skill", methods=["GET", "POST"])
@admin_only
def add_new_skill():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_skill = Skill(
            title=form.title.data,
            body=form.body.data,
            icon=form.icon.data,
        )
        db.session.add(new_skill)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make_skill.html",
                           form=form ,
                           log_in=current_user.is_authenticated ,
                           current_user=current_user,
                           is_edit=False,
                           )











#**************************************************************************#


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_about():
    form = CreateAboutForm()
    if form.validate_on_submit():
        new_about = About(
            title=form.title.data,
            body=form.body.data,
        )
        db.session.add(new_about)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make_skill.html",
                           form=form ,
                           log_in=current_user.is_authenticated ,
                           current_user=current_user,
                           is_edit=False)




#**************************************************************************#





#**************************************************************************#



@app.route("/edit_skill/<int:skill_id>", methods=["GET", "POST"])
@admin_only
def edit_skill(skill_id):
  
    skill_to_edit = db.get_or_404(Skill, skill_id)
  
    edit_form = CreatePostForm(
        title=skill_to_edit.title,
        icon=skill_to_edit.icon,
        body=skill_to_edit.body)

  
    if edit_form.validate_on_submit():
        skill_to_edit.title = edit_form.title.data
        skill_to_edit.icon = edit_form.icon.data
        skill_to_edit.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make_skill.html", form=edit_form,
                                             is_edit=True ,
                                             log_in=current_user.is_authenticated,
                                             current_user=current_user)




#**************************************************************************#



@app.route("/edit_about/<int:about_id>", methods=["GET", "POST"])
@admin_only
def edit_about(about_id):
  
    about_to_edit = db.get_or_404(About,about_id)
  
    edit_form = CreateAboutForm(
        title=about_to_edit.title,
        body=about_to_edit.body)

  
    if edit_form.validate_on_submit():
        about_to_edit.title = edit_form.title.data
        about_to_edit.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("home"))
      
    return render_template("make_skill.html", form=edit_form,
                                             is_edit=True ,
                                             log_in=current_user.is_authenticated,
                                             current_user=current_user)


#**************************************************************************#


@app.route("/new-project", methods=["GET", "POST"])
@admin_only
def add_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        new_project = Project(body=form.body.data)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make_skill.html",
                           form=form ,
                           log_in=current_user.is_authenticated ,
                           current_user=current_user,
                           is_edit=False,
                           )

#**************************************************************************#


@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@admin_only
def edit_project(project_id):
  
    project_to_edit = db.get_or_404(Project, project_id)
  
    edit_form = CreateProjectForm(body=project_to_edit.body)

  
    if edit_form.validate_on_submit():
        project_to_edit.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make_skill.html", form=edit_form,
                                             is_edit=True ,
                                             log_in=current_user.is_authenticated,
                                             current_user=current_user)







#**************************************************************************#


@app.route("/delete/<int:skill_id>")
@admin_only
def delete_skill(skill_id):
    skill_to_delete = db.get_or_404(Skill, skill_id)
    db.session.delete(skill_to_delete)
    db.session.commit()
    return redirect(url_for('home'))






#**************************************************************************#



#**************************************************************************#

if __name__ == "__main__":
    app.run(debug=True, port=5001)




      
  
    
       
     