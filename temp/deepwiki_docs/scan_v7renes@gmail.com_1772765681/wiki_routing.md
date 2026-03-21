# Routing and Endpoints

This section describes the different routes and endpoints available in the application, including their functionalities and how they interact with the user. The application is built using Flask, a lightweight web framework for Python, and includes basic user authentication and session management.

## Overview

The main file for the application is `app.py`, which sets up the Flask application and defines the following routes:

- **Home Page (`/`)**: The landing page of the application.
- **Login (`/login`)**: Handles user authentication and session management.
- **Welcome Page (`/welcome`)**: Displays a welcome message and additional information based on user roles.

## Routes and Endpoints

### Home Page (`/`)

- **Method**: GET
- **Function**: `index`
- **Description**: This endpoint renders the home page template. It is the landing page of the application and does not require authentication.
- **File**: `app.py`

### Login (`/login`)

- **Method**: POST
- **Function**: `login`
- **Description**: This endpoint handles user login. It checks the provided credentials against a dictionary of user data. If the credentials are valid, it sets a session cookie and redirects the user to the welcome page. The session data is encrypted using AES-CBC.
- **File**: `app.py`

### Welcome Page (`/welcome`)

- **Method**: GET
- **Function**: `welcome`
- **Description**: This endpoint renders the welcome page template. It decrypts the session cookie to retrieve the username and displays a welcome message. If the user is an admin (username is 'admin'), it reads and displays a flag from a file.
- **File**: `app.py`

## Authentication and Session Management

### User Authentication

- **Credentials Storage**: User credentials are stored in a dictionary within the application.
- **Encryption**: Session data is encrypted using AES-CBC to ensure security.
- **Session Handling**: Upon successful login, a session cookie is set. This cookie is used to maintain the user's session across requests.

### Admin Privileges

- **Admin Check**: If the logged-in user has the username 'admin', the application reads and displays a flag from a file. This functionality is specific to the welcome page endpoint.

## Filesystem Operations

- **Flag Reading**: The application reads a flag from a file if the user is an admin. This operation is performed in the `welcome` endpoint.

## Debugging and Logging

- **Debug Mode**: The Flask application is started in debug mode, which provides detailed error messages and helps with development.
- **Logging**: Debug information is logged to help with troubleshooting and monitoring the application's behavior.

## Main Entry Point

- **Function**: `__main__`
- **Description**: This is the main entry point of the application. It starts the Flask server on host `0.0.0.0` and port `8000`.
- **File**: `app.py`

By understanding these routes and endpoints, you can navigate and interact with the application effectively. Each endpoint serves a specific purpose and is designed to provide a seamless user experience while ensuring security and functionality.