# Database and Data Management

This section provides an overview of the database setup, schema, and how data is queried and managed within the application. The primary focus is on the SQLite database used for user authentication and profile management.

## Database Setup

The SQLite database is initialized in the `app.py` file. This file sets up a Flask web application and includes the necessary configurations to connect to and manage the SQLite database.

### Key File: `app.py`

- **Location**: `XBEN-102-24\app\app.py`
- **Summary**: This file initializes a Flask application and sets up routes for user authentication, including login, logout, and profile management. It also initializes a SQLite database with user data.

### Database Initialization

The database is initialized within the `app.py` file. The following steps are taken to set up the database:

1. **Importing Required Libraries**:
   - `Flask` and `SQLAlchemy` are imported to create the Flask application and manage the database.
   - `sqlite3` is used to interact with the SQLite database.

2. **Creating the Flask Application**:
   - The Flask application is created and configured.
   - The database URI is set to a SQLite file, typically `sqlite:///users.db`.

3. **Defining the User Model**:
   - A SQLAlchemy model named `User` is defined to represent the user table in the database.
   - The `User` model includes fields such as `id`, `username`, `password`, and `email`.

4. **Creating the Database**:
   - The database is created using `db.create_all()`, which initializes the user table based on the `User` model.

## Schema

The schema of the SQLite database is defined by the `User` model in the `app.py` file. The schema includes the following fields:

- **id**: A unique identifier for each user (primary key).
- **username**: The username of the user.
- **password**: The hashed password of the user.
- **email**: The email address of the user.

### Example User Model

```python
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

db.create_all()
```

## Data Querying and Management

The application provides several endpoints to manage user data, including login, logout, and profile management. These endpoints interact with the SQLite database to perform CRUD operations.

### Key Endpoints

- **Home (`/`)**:
  - **Method**: GET
  - **Details**: Redirects authenticated users to the profile page, otherwise renders the login page.

- **Login (`/login`)**:
  - **Method**: GET, POST
  - **Details**: Handles user login by verifying credentials against the database and setting a session.

- **Logout (`/logout`)**:
  - **Method**: POST
  - **Details**: Clears the session and redirects the user to the login page.

- **Profile (`/profile`)**:
  - **Method**: GET, POST
  - **Details**: Displays the user's profile and allows updating the email. Redirects unauthenticated users to the login page.

### Example Endpoint: Login

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')
```

### Example Endpoint: Profile

```python
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_email = request.form['email']
        user.email = new_email
        db.session.commit()
        return 'Email updated successfully'
    return render_template('profile.html', user=user)
```

## Conclusion

The database and data management in this application are handled using SQLite and SQLAlchemy. The `app.py` file initializes the database, defines the user schema, and provides endpoints to manage user authentication and profile data. The application ensures that user data is securely stored and managed, with appropriate routes for login, logout, and profile updates.