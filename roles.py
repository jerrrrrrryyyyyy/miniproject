from main import Role, db, app

def create_roles():
    with app.app_context():
        # Check if roles already exist to avoid duplication
        existing_roles = Role.query.with_entities(Role.name).all()
        existing_role_names = {role.name for role in existing_roles}

        if 'Teacher' not in existing_role_names:
            teacher = Role(name='Teacher')
            db.session.add(teacher)

        if 'Student' not in existing_role_names:
            student = Role(name='Student')
            db.session.add(student)

        db.session.commit()
        print("Roles created successfully!")

if __name__ == '__main__':
    create_roles()
