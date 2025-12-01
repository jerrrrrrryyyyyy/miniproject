from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid
import os 

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/complaints.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['TEACHER_SECRET'] = os.environ.get('TEACHER_SECRET')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

"""
    Restrict access to users with specific roles.
"""

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            user_roles = [role.name for role in current_user.roles]
            if not any(role in user_roles for role in roles):
                return abort(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Association table for many-to-many relationship between users and roles

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# User model representing students or teachers.
class Complaint(db.Model):
    __tablename__ = 'complaint'
    complaint_id = db.Column(db.Integer, primary_key = True)
    complaint_headline = db.Column(db.String(120), nullable = False)
    complaint_text = db.Column(db.String(500), nullable = False)
    complaint_type = db.Column(db.String(50), nullable = False)
    complaint_status = db.Column(db.String(50), nullable = False, default = 'Submitted')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    user = db.relationship("Users", backref = "complaints")
    
class Users(UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), unique=True, nullable = False)
    password = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(80), unique=True, nullable = False)  
    roles = db.relationship('Role', secondary = roles_users, backref = 'users')

# Role model defines the user roles (eg: Student, Teacher).

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True, nullable = False)

class StudentData(db.Model):
    __tablename__ = 'student_data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    firstSem = db.Column(db.Float, nullable=False)
    secondSem = db.Column(db.Float, nullable=False)
    attendance = db.Column(db.Float, nullable=False)
    internalMarks = db.Column(db.Float, nullable=False)
    paidFees = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    user = db.relationship("Users", backref = "student_data")
# Login loader

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Routes

@app.route('/')
def index():  # Hero page with login/signup
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')  # This is now the hero page

@app.route('/home')
@login_required
def home():  # Home page
    role_names = [role.name for role in current_user.roles]
    if 'Teacher' in role_names:
        # Teachers should see ALL complaints
        complaints = Complaint.query.all()
    else:      
        # Students should only see their own submitted complaints
        complaints = Complaint.query.filter_by(user_id=current_user.id).all()
    # Pass the data to the template using a clearer name like 'complaints'
    return render_template('home.html', complaints=complaints, role_names=role_names)

@app.route("/login", methods = ["GET", "POST"])
def login():  # Login route for user authentication (if users already have an account)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username = username).first()

        if not user:
            return render_template("login.html", error = "User not found")

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home")) # Redirect to dashboard after login
        else:
            return render_template("login.html", error = "Invalid credentials")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register(): # Registration route for new users. Teacher accounts require a special password.
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role_access = request.form.get("options")
        
        # Checks for special password for teachers
        if role_access == "Teacher" and password != app.config["TEACHER_SECRET"]:
            return render_template("signup.html", message = "Enter special  password for teachers.")

        # Check if user already exists
        if Users.query.filter_by(username = username).first():
            return render_template("signup.html", error = "Username already taken!")
        
        # Check if email already exists
        if Users.query.filter_by(email = email).first():
            return render_template("signup.html", error = "Email already in use!")

        hashed_password = generate_password_hash(password, method = "pbkdf2:sha256")
        new_user = Users(username = username, email = email, password = hashed_password)
        
        # Assign role
        role = Role.query.filter_by(name = role_access).first()
        if role:
            new_user.roles.append(role)
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout(): # Logs out the current user.
    logout_user()
    return redirect(url_for("index"))

@app.route('/teachers')
@role_required('Teacher')
def teachers():
    teacher_role = Role.query.filter_by(name='Teacher').first()
    teachers_list = teacher_role.users if teacher_role else []
    return render_template("teachers.html", teachers=teachers_list)

@app.route('/students')
@role_required('Teacher')
def students():
    student_role = Role.query.filter_by(name='Student').first()
    students_list = student_role.users if student_role else []
    return render_template("students.html", students=students_list)

@app.route('/adddata')
@login_required
def add_data(): # Renders the StudentData submission form.
    return render_template('adddata.html')

@app.route('/add', methods=['POST'])
@login_required 
def add_complaint(): # Adds a new complaint submitted by a logged-in user.
    complaint_headline = request.form.get("complaint_headline")
    complaint_text = request.form.get("complaint_text")
    complaint_type = request.form.get("complaint_type")

    new_complaint = Complaint(
        complaint_headline = complaint_headline,
        complaint_text = complaint_text,
        complaint_type = complaint_type,
        user_id = current_user.id
    )

    db.session.add(new_complaint)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/update_status/<int:complaint_id>', methods=["GET", "POST"])
@role_required('Teacher')
def update_status(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)

    if request.method == "POST":
        new_status = request.form.get("complaint_status")
        complaint.complaint_status = new_status
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template("update_status.html", complaint=complaint)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])

@role_required("Teacher")
@login_required
def erase(id): # Deletes a StudentData from the database. Only accessible by teachers.
    data = StudentData.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('home'))

# Main block to run the app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if Role.query.count() == 0:
            teacher = Role(name = 'Teacher')
            student = Role(name = 'Student')
            db.session.add_all([teacher, student])
            db.session.commit()
            print("Default roles created.")
        else:
            print("Roles already exist.")
    app.run(debug=True)
    