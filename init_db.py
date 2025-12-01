import os
from main import app, db, Role

def initialize_database():
    print("--- Running Database Initialization ---")
    with app.app_context():
        # 1. Create all database tables
        db.create_all()
        print("Database tables created.")

        # 2. Check and create default roles
        if Role.query.count() == 0:
            teacher = Role(name = 'Teacher')
            student = Role(name = 'Student')
            parent = Role(name = 'Parent') 
            db.session.add_all([teacher, student, parent]) 
            db.session.commit()
            print("Default roles created successfully.")
        else:
            print("Default roles already exist.")

if __name__ == '__main__':
    initialize_database()
