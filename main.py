from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder = 'templates')  # Create a Flask web application

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'  # Configuration of database connection (SQLite)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turn off modification tracking (improves performance)
app.config['SECRET_KEY'] = 'groupproject'

# Initializes a database and login manager
db = SQLAlchemy(app)  
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Users(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("/"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if Users.query.filter_by(username=username).first():
            return render_template("signup.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = Users(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("/"))
    
    return render_template("signup.html")

# Home route
@app.route("/return")
def home():
    return render_template("signup.html")

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# Define a database model for storing complaints
class Complaint(db.Model):
    
    complaint_id = db.Column(db.Integer, primary_key = True)
    complaint_headline = db.Column(db.String(120),unique = False, nullable = False)
    complaint_text = db.Column(db.String(500),unique = False, nullable = False)
    complaint_status = db.Column(db.String(50), unique = False, nullable = False)


# Route to display all complaints on the home page
@app.route('/')
def index():
    comp = Complaint.query.all()
    return render_template('index.html', complaints = comp)

@app.route('/adddata')
def add_data():
    return render_template('adddata.html')

 # Route adds a new complaint to the database and redirects to the home page
@app.route('/add', methods=['POST'])
def add_complaint():
    complaint_headline = request.form.get("complaint_headline")  # Get form input values from the submitted form
    complaint_text = request.form.get("complaint_text")
    complaint_status = request.form.get("complaint_status")
    
    # Create a new Complaint object with the form data
    new_complaint = Complaint (
        complaint_headline = complaint_headline,
        complaint_text = complaint_text,
        complaint_status = complaint_status
    )  
    
    db.session.add(new_complaint)   # Add the new complaint to the database session and commit it
    db.session.commit()
    
    return redirect('/') # Redirect to the index page after adding a complaint

@app.route('/delete/<int:id>')
def erase(id):  # Route to delete a complaint using its unique ID
    data = Complaint.query.get(id)
    db.session.delete(data)
    db.session.commit()
    
    return redirect('/')  # Redirect to the index page after deleting a complaint

if  __name__ == '__main__':
    with app.app_context():  # Needed for DB operations
        db.create_all()      # Creates database and tables
    app.run(debug=True)