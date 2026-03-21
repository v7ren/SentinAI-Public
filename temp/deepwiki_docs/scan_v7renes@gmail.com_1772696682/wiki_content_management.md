# Content Management

This section provides an overview of how HTML content and image routes are managed and used in the application. The content management system is designed to handle various forms and challenges, particularly focusing on security aspects such as Cross-Site Scripting (XSS).

## HTML Content Management

### Constants File: `constants.py`

The `constants.py` file is the central repository for HTML content strings and image route mappings. It contains predefined HTML content for different web pages and forms, which are used in various parts of the application. The content is designed to be rendered as web pages and is particularly useful for security challenges and educational contexts.

#### HTML Content Strings

- **INDEX_CONTENT**: HTML content for the main index page of the application.
- **XSS_CONTENT**: HTML content for a form that includes a name input field, used in an XSS challenge.
- **XSS_CONTENT_POST**: HTML content for a form that includes a solution input field and is set to POST method, used in an XSS challenge.
- **XSS_CONTENT_TAG**: HTML content for a form that includes a name input field and an additional tag, used in an XSS challenge.
- **XSS_CONTENT_TAG_POST**: HTML content for a form that includes a solution input field and an additional tag, set to POST method, used in an XSS challenge.
- **XSS_CONTENT_IFRAME**: HTML content for a form that includes a URL input field and an iframe, used in an XSS challenge.
- **XSS_CONTENT_TEXTAREA_POST**: HTML content for a form that includes a textarea for a name input and is set to POST method, used in an XSS challenge.

### Flask Application: `app.py`

The `app.py` file sets up a Flask web application that serves the HTML content defined in `constants.py`. It includes two main HTTP endpoints:

- **Index Route (`/`)**: Serves the main page of the application using the `INDEX_CONTENT` string.
- **XSS Challenge Route (`/xss25`)**: Handles POST and GET requests for an XSS challenge. It processes user input to prevent XSS attacks and uses PhantomJS to verify the presence of XSS.

#### XSS Challenge Route

- **GET Method**: Serves the XSS challenge form using the `XSS_CONTENT` string.
- **POST Method**: Processes the submitted form data, checks for blacklisted words, and uses PhantomJS to verify the presence of XSS. The response is based on the input validation.

### PhantomJS Script: `check.js`

The `check.js` script is used to simulate user interactions with web pages and verify the presence of XSS vulnerabilities. It uses PhantomJS to open a web page provided via standard input, simulate focus events on elements with `autofocus` or `onfocus` attributes, and log alerts, confirms, and prompts to the console. The script exits after a delay to ensure all event handlers are processed.

#### Main Script Execution

- **CLI Entry Point**: The script reads a URL from standard input and uses PhantomJS to open and interact with the web page.

## Image Route Management

### Image Routes in `constants.py`

The `constants.py` file also defines a dictionary of image routes, `IMAGE_ROUTES`, which maps challenge levels to image paths representing different states (start, process, error, success). These images are used to provide visual feedback to users during the challenges.

- **IMAGE_ROUTES**: Dictionary mapping challenge levels to image paths.

## Interaction Flow

1. **User Accesses the Main Page**:
   - The user navigates to the root path (`/`).
   - The Flask application serves the main page using the `INDEX_CONTENT` string from `constants.py`.

2. **User Engages with XSS Challenge**:
   - The user navigates to the XSS challenge route (`/xss25`).
   - The Flask application serves the XSS challenge form using the `XSS_CONTENT` string from `constants.py`.

3. **User Submits Form Data**:
   - The user submits the form data via a POST request to `/xss25`.
   - The Flask application processes the submitted data, checks for blacklisted words, and uses the `check.js` script to verify the presence of XSS vulnerabilities.

4. **PhantomJS Verification**:
   - The `check.js` script opens the web page provided via standard input, simulates user interactions, and logs any alerts, confirms, or prompts.
   - The script exits after a delay to ensure all event handlers are processed.

5. **Response Based on Validation**:
   - The Flask application returns a response based on the input validation and PhantomJS verification.

6. **Visual Feedback**:
   - The application uses the `IMAGE_ROUTES` dictionary to provide visual feedback to the user, indicating the state of the challenge (start, process, error, success).

By following this structured approach, the application ensures that HTML content and image routes are managed effectively, providing a robust and secure user experience.