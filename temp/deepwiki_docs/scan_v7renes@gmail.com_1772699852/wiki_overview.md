# Overview

## What the Project Is and What Problem It Solves

This project is a web application designed to test and demonstrate Cross-Site Scripting (XSS) vulnerabilities. It uses PhantomJS to simulate browser behavior and Flask to serve a web interface. The primary goal is to provide a controlled environment for testing and understanding XSS vulnerabilities, which are a common security issue in web applications.

## Main Components or Modules

### 1. **PhantomJS Script (src/check.js)**
   - **Functionality**: This script uses PhantomJS to open a web page specified by user input and simulates browser events such as 'focus' on elements with 'autofocus' or 'onfocus' attributes. It logs alerts, confirms, and prompts from the page and exits after a delay to ensure all event handlers are processed.
   - **Key Entities**: 
     - `PhantomJS` for headless browser automation.
     - User input for the web page URL.
     - Event simulation and logging.

### 2. **Flask Web Application (src/app.py)**
   - **Functionality**: This file sets up a Flask web application with two main endpoints:
     - **Index Route (`/`)**: Serves the main page of the application.
     - **XSS Challenge Route (`/xss25`)**: Handles both GET and POST requests, checks for blacklisted words, and uses PhantomJS to verify the presence of XSS vulnerabilities in submitted HTML content.
   - **Key Entities**:
     - Flask for web framework.
     - HTTP endpoints for serving content and handling user interactions.
     - PhantomJS integration for XSS testing.

### 3. **Constants and Templates (src/constants.py)**
   - **Functionality**: This file contains HTML content strings and image route mappings used in the web application. These templates are used to render different XSS challenge levels and display status icons.
   - **Key Entities**:
     - HTML content templates for various XSS challenges.
     - Image route mappings for status icons.

## Typical Usage or Runtime Scenario

1. **User Accesses the Application**:
   - The user navigates to the main page of the application by visiting the root URL (`/`).
   - The Flask application serves the main page using the HTML content defined in `src/constants.py`.

2. **User Submits XSS Challenge**:
   - The user submits HTML content to the `/xss25` endpoint via a POST request.
   - The Flask application checks the submitted content for blacklisted words and uses PhantomJS to verify the presence of XSS vulnerabilities.

3. **PhantomJS Simulation**:
   - The `src/check.js` script is invoked to simulate browser behavior on the submitted HTML content.
   - It logs any alerts, confirms, and prompts that occur during the simulation and ensures all event handlers are processed.

4. **Response to User**:
   - The Flask application processes the results from the PhantomJS simulation and returns a response to the user, indicating whether the submitted content contains XSS vulnerabilities.

## Where to Look Next

- **For detailed information on the PhantomJS script and its event simulation capabilities, see the [PhantomJS Script](#phantomjs-script) section.**
- **For a deeper dive into the Flask web application, including its endpoints and security checks, see the [Flask Web Application](#flask-web-application) section.**
- **For a comprehensive list of HTML content templates and image route mappings, see the [Constants and Templates](#constants-and-templates) section.**

By exploring these sections, you will gain a more detailed understanding of the project's architecture and how each component contributes to the overall functionality.