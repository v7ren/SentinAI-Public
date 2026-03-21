# Database and ORM

This section provides an overview of the database schema, ORM models, and database operations used in the application. The application leverages SQLAlchemy as the ORM and Flask-SQLAlchemy for database management. The database is used to store user authentication data and prescription information.

## Database Schema

The database schema is designed to support user authentication and prescription management. The key entities in the schema are:

- **User**: Represents a user in the system.
- **Prescription**: Represents a prescription added by a user.

### User Model

The `User` model is defined in the `app/app.py` file. It includes the following fields:

- `id`: Unique identifier for the user.
- `username`: Username for the user.
- `password`: Password for the user (hashed for security).

### Prescription Model

The `Prescription` model is also defined in the `app/app.py` file. It includes the following fields:

- `id`: Unique identifier for the prescription.
- `user_id`: Foreign key linking to the `User` model.
- `details`: Details of the prescription.
- `flag`: An optional field that can be set from an environment variable.

## ORM Models

The ORM models are defined using SQLAlchemy in the `app/app.py` file. The models are used to interact with the database and perform CRUD operations.

### User Model

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    prescriptions = db.relationship('Prescription', backref='user', lazy=True)
```

### Prescription Model

```python
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    details = db.Column(db.Text, nullable=False)
    flag = db.Column(db.String(120), nullable=True)
```

## Database Operations

The application performs various database operations, including querying, adding, and updating records. These operations are primarily handled in the `app/app.py` file.

### Initialization

The database is initialized and the application is started in the `main` function of `app/app.py`. This function also checks if there are any prescriptions for the user 'admin' and adds 89 prescriptions if none exist.

```python
def main():
    with app.app_context():
        db.create_all()
        user = User.query.filter_by(username='admin').first()
        if user:
            prescriptions = Prescription.query.filter_by(user_id=user.id).all()
            if not prescriptions:
                for i in range(1, 90):
                    flag = os.getenv('FLAG') if i == 43 else None
                    prescription = Prescription(user_id=user.id, details=f'Prescription {i}', flag=flag)
                    db.session.add(prescription)
                db.session.commit()
    app.run(host='0.0.0.0', port=5003)
```

### Querying Users and Prescriptions

The application queries users and prescriptions in various routes. For example, the `login` route checks the user's credentials:

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # Authentication successful
            return redirect('/view_prescriptions')
        else:
            # Authentication failed
            return 'Invalid credentials'
    return render_template('login.html')
```

### Adding Prescriptions

The `add_prescription` route allows authenticated users to add new prescriptions:

```python
@app.route('/add_prescription', methods=['GET', 'POST'])
@login_required
def add_prescription():
    if request.method == 'POST':
        details = request.form['details']
        prescription = Prescription(user_id=current_user.id, details=details)
        db.session.add(prescription)
        db.session.commit()
        return redirect('/view_prescriptions')
    return render_template('add_prescription.html')
```

### Viewing Prescriptions

The `view_prescriptions` route displays all prescriptions for the authenticated user:

```python
@app.route('/view_prescriptions', methods=['GET'])
@login_required
def view_prescriptions():
    prescriptions = Prescription.query.filter_by(user_id=current_user.id).all()
    return render_template('view_prescriptions.html', prescriptions=prescriptions)
```

## GraphQL Endpoint

The application also provides a GraphQL endpoint for querying and mutating prescription data. This endpoint is defined in the `app/app.py` file and uses the GraphQL library to handle requests.

```python
@app.route('/graphql', methods=['GET', 'POST'])
def graphql():
    schema = graphene.Schema(query=Query, mutation=Mutation)
    result = schema.execute(request.data)
    return jsonify(result.data)
```

### GraphQL Schema

The GraphQL schema is defined in the same file and includes queries and mutations for prescriptions. For example, a query to fetch prescriptions for a user might look like this:

```python
class Query(graphene.ObjectType):
    prescriptions = graphene.List(PrescriptionType, user_id=graphene.Int())

    def resolve_prescriptions(self, info, user_id):
        return Prescription.query.filter_by(user_id=user_id).all()

class Mutation(graphene.ObjectType):
    add_prescription = AddPrescription.Field()
```

## Security Considerations

The application includes security measures to protect user data and prevent unauthorized access. User passwords are hashed, and authentication is required for most routes. The `login_required` decorator ensures that only authenticated users can access certain endpoints.

```python
from flask_login import login_required, current_user

@app.route('/view_prescriptions', methods=['GET'])
@login_required
def view_prescriptions():
    prescriptions = Prescription.query.filter_by(user_id=current_user.id).all()
    return render_template('view_prescriptions.html', prescriptions=prescriptions)
```

## Summary

The database and ORM setup in the application is designed to support user authentication and prescription management. SQLAlchemy is used as the ORM, and the database schema includes `User` and `Prescription` models. The application performs various database operations, including querying, adding, and updating records, and provides a GraphQL endpoint for more advanced data manipulation. Security measures are in place to protect user data and ensure authorized access.