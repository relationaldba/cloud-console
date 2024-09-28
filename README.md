Cloud Admin
============

Cloud Admin is a web application that provides a user interface to manage infrastructure, applications, and services.

Features
--------

*   **User Management**: Ability to create, read, update and delete users.
*   **User Authentication**: Ability to authenticate users using username and password.
*   **Team Management**: Ability to create, read, update and delete teams.
*   **Deployment Management**: Ability to create, read, update and delete deployments.
*   **Stack Management**: Ability to create, read, update and delete stacks.
*   **Product Management**: Ability to create, read, update and delete products.
*   **Service Management**: Ability to create, read, update and delete services.

Installation
------------

### Prerequisites

*   Python 3.8+
*   pip
*   Docker

### Install

*   Clone the repository
*   Create a virtual environment
*   Install the dependencies
*   Create a `.env` file with environment variables
*   Run the application

### Environment Variables

*   `SECRET_KEY`: Secret key for the application
*   `SQLALCHEMY_DATABASE_URI`: URI for the database
*   `JWT_SECRET_KEY`: Secret key for the JWT tokens
*   `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for the JWT tokens

Running the Application
-----------------------

*   Run `docker-compose up` to start the application
*   Run `docker-compose exec web python manage.py migrate` to migrate the database
*   Run `docker-compose exec web python manage.py seed` to seed the database
*   Run `docker-compose exec web python manage.py run` to start the application

API Documentation
-----------------

The API documentation is available at `<http://localhost:8000/docs>`.




## TODO Items (will soon convert them to trello board)

TODO Frontend:

- High:
    - Implement User roles and permission checks on all routes
    - Strip the whitespace using pydantic models
    - Add Google Login
    - Add Microsoft Login
    - Add Remember Me functionality
    - Add active search functionality
    - Add pagination to all pages
    - Add modal to login in case the auth-token cookie is expired or invalid
    - Add refresh tokens to automatically refresh the auth token when it expires
    - Add mechanism to invalidate the refresh token when a new refresh token is issued
    - Add scheduler for jobs
    - Add scheduler for notifications
    - Add queue for jobs
    - Add queue for notifications
    - Add mechanism to invalidate the refresh token when a new refresh token is issued
    - Research the IaC solutions for the backend
    - Create Stacks API

- Medium:
    - Format the 404 messages
    - Add functionality to go back to the previous page (and remember History)
    - Protect against CSRF attacks
    - Protect against XSS attacks
    - Protect against MITM attacks
    - Add pagination to all pages
    - Add htmx:after-htmx to the login modal
    - Add htmx:after-htmx to the login form
    - Add htmx:validation to the login form
    - Add htmx:validation to the search input
    - Add active search functionality
    - User Management: Add functionality to edit user profile

- Low:
    - Add loading spinners on the login page
    - Add loading spinners on the all buttons
    - Add loading spinners on the search input
    - Add htmx:transition to all buttons
    - Sidebar: Add functionality to collapse the sidebar
    - Sidebar: Add icons to the sidebar



- Separate Product and Product Details
- Research storing the child objects in the database