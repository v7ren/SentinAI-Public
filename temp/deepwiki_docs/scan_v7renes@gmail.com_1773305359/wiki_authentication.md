# Authentication and Authorization

This section provides a detailed guide on how authentication and authorization are implemented in the TaskFlow application. It covers the use of JWT tokens, user roles, and session management.

## Overview

The authentication and authorization system in TaskFlow is designed to secure access to various endpoints and ensure that only authenticated and authorized users can perform specific actions. The system uses JSON Web Tokens (JWT) for session management and role-based access control (RBAC) for authorization.

### Key Components

- **JWT Tokens**: Used for session management and user authentication.
- **User Roles**: Define the permissions and access levels of users.
- **Middleware**: Handles token verification, role checking, and error handling.
- **API Endpoints**: Provide functionalities for user registration, login, token refresh, and logout.

## JWT Tokens

### Token Generation and Verification

- **Token Generation**: JWT tokens are generated upon successful user registration or login. The tokens are signed using a secret key and contain the user's ID and role.
- **Token Verification**: Middleware functions verify the JWT token in the `Authorization` header of incoming requests. If the token is valid, user information is attached to the request object.

### Files Involved

- **`taskflow\backend\src\middleware\authenticate.js`**: Contains the `authenticate` middleware function that checks for a valid JWT token and attaches user information to the request object.
- **`taskflow\backend\src\utils\tokenUtils.js`**: Provides utility functions for generating and verifying JWT access and refresh tokens.

### Example Code Snippet

```javascript
// taskflow\backend\src\middleware\authenticate.js
const jwt = require('jsonwebtoken');
const { verifyAccess } = require('../utils/tokenUtils');

const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ message: 'No token provided' });
  }

  try {
    const decoded = verifyAccess(token);
    req.user = decoded;
    next();
  } catch (err) {
    console.warn('Invalid token:', err);
    res.status(401).json({ message: 'Invalid token' });
  }
};
```

## User Roles and Authorization

### Role-Based Access Control (RBAC)

- **User Roles**: Users can have different roles such as `admin`, `member`, etc. Each role has specific permissions and access levels.
- **Role Checking**: Middleware functions check if the user has the required role to access a resource. If the user is not authenticated or does not have the required role, an appropriate error response is returned.

### Files Involved

- **`taskflow\backend\src\middleware\authorize.js`**: Contains the `authorize` middleware function that checks if the user has the required role to access a resource.

### Example Code Snippet

```javascript
// taskflow\backend\src\middleware\authorize.js
const authorize = (requiredRole) => (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ message: 'Unauthorized' });
  }

  if (req.user.role !== requiredRole) {
    return res.status(403).json({ message: 'Forbidden' });
  }

  next();
};
```

## Authentication Endpoints

### User Registration and Login

- **Registration**: Users can register by providing their full name, email, and password. Upon successful registration, a new user and organization are created, and access and refresh tokens are issued.
- **Login**: Users can log in by providing their email and password. If the credentials are valid, access and refresh tokens are issued.

### Files Involved

- **`taskflow\backend\src\controllers\authController.js`**: Contains the implementation of user registration, login, token refresh, password reset, and logout functionalities.
- **`taskflow\backend\src\routes\authRoutes.js`**: Defines the routes for user registration, login, token refresh, password reset, and logout.

### Example Code Snippet

```javascript
// taskflow\backend\src\controllers\authController.js
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { userModel, orgModel } = require('../models');
const { signAccess, signRefresh } = require('../utils/tokenUtils');

const register = async (req, res) => {
  const { fullName, email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  const user = await userModel.create({ fullName, email, password: hashedPassword });
  const org = await orgModel.create({ name: `${fullName}'s Organization`, ownerId: user.id });

  const accessToken = signAccess({ userId: user.id, role: 'member' });
  const refreshToken = signRefresh({ userId: user.id });

  res.status(201).json({ accessToken, refreshToken });
};

const login = async (req, res) => {
  const { email, password } = req.body;
  const user = await userModel.findByEmail(email);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }

  const accessToken = signAccess({ userId: user.id, role: user.role });
  const refreshToken = signRefresh({ userId: user.id });

  res.json({ accessToken, refreshToken });
};
```

### Token Refresh and Logout

- **Token Refresh**: Users can refresh their access token by providing a valid refresh token.
- **Logout**: Users can log out by invalidating their refresh token.

### Files Involved

- **`taskflow\backend\src\controllers\authController.js`**: Contains the implementation of token refresh and logout functionalities.
- **`taskflow\backend\src\routes\authRoutes.js`**: Defines the routes for token refresh and logout.

### Example Code Snippet

```javascript
// taskflow\backend\src\controllers\authController.js
const refresh = async (req, res) => {
  const { refreshToken } = req.body;
  const decoded = jwt.verify(refreshToken, process.env.REFRESH_SECRET);
  const user = await userModel.findById(decoded.userId);

  if (!user || user.refreshToken !== refreshToken) {
    return res.status(401).json({ message: 'Invalid refresh token' });
  }

  const accessToken = signAccess({ userId: user.id, role: user.role });
  res.json({ accessToken });
};

const logout = async (req, res) => {
  const { refreshToken } = req.body;
  const user = await userModel.findById(req.user.id);

  if (user.refreshToken === refreshToken) {
    user.refreshToken = null;
    await user.save();
  }

  res.json({ message: 'Logged out successfully' });
};
```

## Frontend Integration

### Authentication Context

- **AuthProvider**: Manages the authentication state and provides functions for user login, registration, and logout.
- **useAuth**: A custom hook that allows components to access the authentication context.

### Files Involved

- **`taskflow\frontend\src\context\AuthContext.jsx`**: Defines the `AuthProvider` and `useAuth` hook for managing authentication state.
- **`taskflow\frontend\src\hooks\useAuth.js`**: Re-exports the `useAuth` hook from `AuthContext`.

### Example Code Snippet

```javascript
// taskflow\frontend\src\context\AuthContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import { authApi } from '../api';

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          const response = await authApi.verifyToken(token);
          setUser(response.data.user);
        } catch (error) {
          console.error('Token verification failed:', error);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    const response = await authApi.login(credentials);
    localStorage.setItem('accessToken', response.data.accessToken);
    localStorage.setItem('refreshToken', response.data.refreshToken);
    setUser(response.data.user);
  };

  const logout = async () => {
    await authApi.logout();
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext, AuthProvider };
```

### Authentication in Routes

- **Private Routes**: Routes that require user authentication are protected using the `useAuth` hook. Unauthenticated users are redirected to the login page.

### Files Involved

- **`taskflow\frontend\src\App.jsx`**: Sets up routing for various pages, including public and private routes.
- **`taskflow\frontend\src\api\client.js`**: Configures an Axios client for making HTTP requests, including interceptors for adding authentication tokens.

### Example Code Snippet

```javascript
// taskflow\frontend\src\App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import TasksPage from './pages/TasksPage';
import TaskDetailPage from './pages/TaskDetailPage';
import SettingsPage from './pages/SettingsPage';
import AdminPage from './pages/AdminPage';
import NotFoundPage from './pages/NotFoundPage';

const PrivateRoute = ({ component: Component, ...rest }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  return (
    <Route
      {...rest}
      render={(props) => user ? <Component {...props} /> : <Redirect to="/login" />}
    />
  );
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Switch>
          <Route path="/" exact component={LandingPage} />
          <Route path="/login" component={LoginPage} />
          <Route path="/register" component={RegisterPage} />
          <PrivateRoute path="/dashboard" component={DashboardPage} />
          <PrivateRoute path="/projects" component={ProjectsPage} />
          <PrivateRoute path="/projects/:projectId" component={ProjectDetailPage} />
          <PrivateRoute path="/tasks" component={TasksPage} />
          <PrivateRoute path="/tasks/:taskId" component={TaskDetailPage} />
          <PrivateRoute path="/settings" component={SettingsPage} />
          <PrivateRoute path="/admin" component={AdminPage} />
          <Route path="*" component={NotFoundPage} />
        </Switch>
      </Router>
    </AuthProvider>
  );
};

export default App;
```

## Conclusion

The authentication and authorization system in TaskFlow is robust and secure, leveraging JWT tokens for session management and role-based access control for authorization. The system ensures that only authenticated and authorized users can access and perform specific actions, providing a secure and user-friendly experience.