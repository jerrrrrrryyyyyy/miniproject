from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder = 'templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#creates database model
class Complaint(db.Model):
    
    complaint_id = db.Column(db.Integer, primary_key = True)
    complaint_headline = db.Column(db.String(120),unique = False, nullable = False)
    complaint_text = db.Column(db.String(500),unique = False, nullable = False)
    complaint_status = db.Column(db.String(50), unique = False, nullable = False)

@app.route('/')
def index():
    comp = Complaint.query.all()
    return render_template('index.html', complaints = comp)

@app.route('/adddata')
def add_data():
    return render_template('adddata.html')

@app.route('/add', methods=['POST'])
def add_complaint(): # Function adds a new complaint to the database and redirects to the home page
    complaint_headline = request.form.get("complaint_headline")
    complaint_text = request.form.get("complaint_text")
    complaint_status = request.form.get("complaint_status")
    
    new_complaint = Complaint (
        complaint_headline = complaint_headline,
        complaint_text = complaint_text,
        complaint_status = complaint_status
    )
    db.session.add(new_complaint)
    db.session.commit()
    return redirect('/') # Redirect to the index page after adding a complaint

@app.route('/delete/<int:id>')
def erase(id):  # Function deletes the data on the basis of unique id and redirects to home page after deletion
    data = Complaint.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/') 

if  __name__ == '__main__':
    with app.app_context():  # Needed for DB operations
        db.create_all()      # Creates database and tables
    app.run(debug=True)