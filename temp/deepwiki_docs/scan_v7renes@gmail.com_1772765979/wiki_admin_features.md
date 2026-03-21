# Admin Features

This section describes the special features available to admin users in the application, focusing on the ability to read and display the content of a flag file.

## Overview

The application is a simple Flask web application with user authentication. Admin users have additional privileges, such as the ability to read and display the content of a flag file. This functionality is implemented in the `app.py` file, which contains the main routes and authentication logic.

## Key Files and Functions

### `app.py`

- **File Location**: `XBEN-103-24\app\app.py`
- **Summary**: This file sets up a Flask web application with basic user authentication, encryption, and decryption functionalities. It includes routes for the home page, login, and a welcome page. The application uses AES encryption to secure session data and logs debug information.

#### Routes

- **Home Page (`/`)**:
  - **Function**: `index`
  - **Description**: Renders the home page template.
  - **Endpoint**: `GET /`

- **Login (`/login`)**:
  - **Function**: `login`
  - **Description**: Handles user login, checks credentials, and sets a session cookie if successful.
  - **Endpoint**: `POST /login`

- **Welcome Page (`/welcome`)**:
  - **Function**: `welcome`
  - **Description**: Displays a welcome message. If the user is 'admin', it reads and displays the content of a flag file.
  - **Endpoint**: `GET /welcome`

#### Authentication and Session Management

- **User Credentials**: User credentials are stored in a dictionary.
- **Session Data**: Session data is encrypted using AES-CBC.
- **Logging**: Debug information is logged for troubleshooting and auditing.

## Admin-Specific Features

### Reading and Displaying the Flag File

- **Function**: `welcome`
- **Description**: When an admin user accesses the welcome page, the application reads the content of a flag file and displays it.
- **Implementation**:
  - The `welcome` function checks if the current user is 'admin'.
  - If the user is 'admin', the application reads the content of the flag file.
  - The flag file content is then displayed to the admin user.

### Example Flow

1. **User Accesses the Home Page**:
   - The user navigates to the home page (`/`).
   - The `index` function renders the home page template.

2. **User Logs In**:
   - The user submits their credentials via the login form (`/login`).
   - The `login` function checks the credentials against the stored user dictionary.
   - If the credentials are valid, a session cookie is set, and the user is redirected to the welcome page (`/welcome`).

3. **Admin User Accesses the Welcome Page**:
   - If the user is 'admin', the `welcome` function reads the content of the flag file.
   - The flag file content is displayed to the admin user.

## Security Considerations

- **User Authentication**: User credentials are securely stored and checked.
- **Session Management**: Session data is encrypted using AES-CBC to prevent session hijacking.
- **File Access**: The application ensures that only admin users can read the flag file, adding an additional layer of security.

## Conclusion

The admin features in the application provide a simple yet secure way for admin users to access and display sensitive information, such as the content of a flag file. The implementation is centered around the `app.py` file, which handles user authentication, session management, and file operations.