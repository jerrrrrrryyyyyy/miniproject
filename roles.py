from main import Role, db, app

def create_roles():
    with app.app_context():
        teacher = Role(id=1, name='Teacher')
        student = Role(id=2, name='Student')

        db.session.add(teacher)
        db.session.add(student)

        db.session.commit()
        print("Roles created successfully!")

if __name__ == '__main__':
    create_roles()
    