# Overview

## What the Project Is and What Problem It Solves

The project is a web application designed to help users understand and test for Cross-Site Scripting (XSS) vulnerabilities. It provides a platform where users can submit content and see if it contains XSS vulnerabilities. The application uses Flask for the web framework and PhantomJS for simulating user interactions and detecting potential XSS issues.

## Main Components or Modules

### 1. **Flask Web Application (`app.py`)**

- **Index Route (`/`)**: Serves the main page of the application, which includes links to stylesheets and a form for navigating to the XSS challenge.
- **XSS Challenge Route (`/xss25`)**: Handles both GET and POST requests. It checks for blacklisted words in user input and uses PhantomJS to verify if the input contains XSS attempts. It responds with appropriate feedback to the user.

### 2. **PhantomJS Script (`check.js`)**

- **Main Script Execution**: Reads a URL from standard input, opens the web page using PhantomJS, and simulates user interactions such as focusing on elements with `autofocus` or `onfocus` attributes. It logs alerts, confirms, and prompts to the console and exits after a delay to ensure all event handlers are processed.

### 3. **HTML Content and Image Routes (`constants.py`)**

- **HTML Content Strings**: Defines various HTML content strings for different parts of the web application, including the main index page and multiple XSS challenge pages.
- **Image Routes**: Provides a dictionary mapping different XSS challenge levels to image routes for start, process, error, and success states.

## Typical Usage or Runtime Scenario

1. **User Accesses the Main Page**:
   - The user navigates to the root URL (`/`), which serves the main page of the application. This page includes links to stylesheets and a form for navigating to the XSS challenge.

2. **User Submits Content for XSS Testing**:
   - The user submits content via the form on the main page or directly accesses the XSS challenge route (`/xss25`).
   - The application checks for blacklisted words in the user input.

3. **PhantomJS Simulation**:
   - If the input passes the initial checks, the application uses PhantomJS to open the web page and simulate user interactions.
   - PhantomJS logs any alerts, confirms, and prompts to the console and ensures all event handlers are processed.

4. **Feedback to the User**:
   - The application responds with appropriate feedback based on the results of the PhantomJS simulation. This feedback helps the user understand whether their input contains XSS vulnerabilities.

## Where to Look Next

- **For more details on the Flask web application and its endpoints, see the [Web Application](web_application.md) section.**
- **For a deeper dive into the PhantomJS script and its functionality, see the [PhantomJS Script](phantomjs_script.md) section.**
- **For information on the HTML content strings and image routes, see the [Constants](constants.md) section.**

These sections provide more detailed explanations and code snippets for each component of the project.