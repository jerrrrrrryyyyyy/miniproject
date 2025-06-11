from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder = 'templates')  # Create a Flask web application

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'  # Configuration of database connection (SQLite)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Turn off modification tracking (improves performance)

db = SQLAlchemy(app)  # Create a database object that will be used to manage the database

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