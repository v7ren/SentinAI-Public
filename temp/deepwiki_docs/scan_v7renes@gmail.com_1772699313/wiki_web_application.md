# Web Application

This section provides an overview of the Flask web application, including its routes and functionality. The application is designed to serve a main page and handle form submissions to check for Cross-Site Scripting (XSS) vulnerabilities.

## Application Structure

The web application is primarily defined in the `src/app.py` file, which sets up a Flask application and defines the routes. The application uses PhantomJS, as described in `src/check.js`, to simulate browser events and evaluate the submitted content for XSS vulnerabilities.

### Key Files

- **`src/app.py`**: Sets up the Flask application and defines the routes.
- **`src/check.js`**: Uses PhantomJS to simulate browser events and check for XSS vulnerabilities.
- **`src/constants.py`**: Contains HTML content strings and image route mappings for the web application.

## Routes and Functionality

### Index Route

- **Endpoint**: `GET /`
- **Function**: Serves the main page of the application.
- **Implementation**: The index route is defined in `src/app.py` and serves the HTML content defined in `src/constants.py` under the `INDEX_CONTENT` constant.

### XSS Vulnerability Check Route

- **Endpoint**: `POST /page`
- **Function**: Handles form submissions to check for XSS vulnerabilities and returns a response based on the evaluation.
- **Implementation**: This route is also defined in `src/app.py`. When a form is submitted, the application uses the `check.js` script to evaluate the submitted content. The script simulates browser events and logs any alerts, confirms, or prompts from the page. The result is then returned to the user.

### Additional Routes

- **Endpoint**: `GET /page`
- **Function**: Serves an XSS challenge page with a form.
- **Implementation**: This route is defined in `src/app.py` and serves the HTML content defined in `src/constants.py` under the `XSS_CONTENT` constant.

## Interaction Flow

1. **User Accesses the Main Page**:
   - The user navigates to the root URL (`/`).
   - The Flask application serves the main page using the `INDEX_CONTENT` HTML content from `src/constants.py`.

2. **User Submits a Form**:
   - The user navigates to the XSS challenge page by accessing the `/page` route.
   - The Flask application serves the XSS challenge page using the `XSS_CONTENT` HTML content from `src/constants.py`.

3. **Form Submission and Evaluation**:
   - The user submits the form, which triggers a POST request to the `/page` endpoint.
   - The Flask application receives the form data and calls the `check.js` script to evaluate the content for XSS vulnerabilities.
   - The `check.js` script uses PhantomJS to simulate browser events and logs any alerts, confirms, or prompts from the page.
   - The result of the evaluation is returned to the user.

## Security Considerations

- **XSS Vulnerability Checks**: The application uses PhantomJS to simulate browser events and check for XSS vulnerabilities. This ensures that the submitted content is evaluated in a controlled environment.
- **HTML Content**: The HTML content strings in `src/constants.py` are designed to include forms and placeholders for dynamic content, which are used to create the XSS challenge pages.

## Filesystem Operations

- **HTML Content Strings**: The HTML content strings in `src/constants.py` are used to render the web pages. These strings are stored in the file and accessed by the Flask application.
- **Image Routes**: The `IMAGE_ROUTES` dictionary in `src/constants.py` maps different XSS challenge levels to their corresponding image routes, which are used to display images on the challenge pages.

## External HTTP Calls

- **PhantomJS**: The `check.js` script uses PhantomJS to open web pages and simulate browser events. This involves making HTTP requests to the specified URLs.

By following this structure and flow, the web application provides a robust and secure environment for testing and evaluating XSS vulnerabilities.