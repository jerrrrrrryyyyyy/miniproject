from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'groupproject'
app.config['TEACHER_SECRET'] = 'Vastadmin1'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Role-based Access Helper

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

# Association Table

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# Models

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    roles = db.relationship('Role', secondary=roles_users, backref='users')

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class Complaint(db.Model):
    __tablename__ = 'complaint'
    complaint_id = db.Column(db.Integer, primary_key=True)
    complaint_headline = db.Column(db.String(120), nullable=False)
    complaint_text = db.Column(db.String(500), nullable=False)
    complaint_type = db.Column(db.String(50), nullable=False)

# Login loader

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Routes

@app.route('/')
@login_required
def index():
    comp = Complaint.query.all()
    return render_template('index.html', complaints=comp)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role_id = request.form.get("options")

        user = Users.query.filter_by(username=username).first()

        if not user:
            return render_template("login.html", error="User not found")

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role_access = request.form.get("options")
        
        if role_access == "Teacher" and password != app.config["TEACHER_SECRET"]:
                return render_template("signup.html", message="Enter special  password for teachers.")

        if Users.query.filter_by(username=username).first():
            return render_template("signup.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = Users(username=username, password=hashed_password)
        
        role = Role.query.filter_by(name=role_access).first()
        if role:
            new_user.roles.append(role)
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

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
def add_data():
    return render_template('adddata.html')

@app.route('/add', methods=['POST'])
@login_required
@role_required('Student')
def add_complaint():
    complaint_headline = request.form.get("complaint_headline")
    complaint_text = request.form.get("complaint_text")
    complaint_type = request.form.get("complaint_type")

    new_complaint = Complaint(
        complaint_headline = complaint_headline,
        complaint_text = complaint_text,
        complaint_type = complaint_type
    )

    db.session.add(new_complaint)
    db.session.commit()

    return redirect('/')

@app.route('/delete/<int:id>')
@role_required("Teacher")
@login_required
def erase(id):
    data = Complaint.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('index'))


# Run the app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if Role.query.count() == 0:
            teacher = Role(name='Teacher')
            student = Role(name='Student')
            db.session.add_all([teacher, student])
            db.session.commit()
            print("Default roles created.")
        else:
            print("Roles already exist.")
    app.run(debug=True)
