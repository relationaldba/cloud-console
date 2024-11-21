# Cloud Admin

Cloud Admin is a web application that provides a user interface to manage infrastructure, applications, and services.

## Features

* **User Management**: Ability to create, read, update and delete users.
* **User Authentication**: Ability to authenticate users using username and password.
* **Team Management**: Ability to create, read, update and delete teams.
* **Deployment Management**: Ability to create, read, update and delete deployments.
* **Stack Management**: Ability to create, read, update and delete stacks.
* **Product Management**: Ability to create, read, update and delete products.
* **Service Management**: Ability to create, read, update and delete services.

## Installation

### Prerequisites

* Python 3.13+
* pip
* Docker

### Install

* Clone the repository
* Create a virtual environment
* Install the dependencies
* Create a `.env` file with environment variables
* Run the application

### Environment Variables

* `SECRET_KEY`: Secret key for the application
* `SQLALCHEMY_DATABASE_URI`: URI for the database
* `JWT_SECRET_KEY`: Secret key for the JWT tokens
* `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for the JWT tokens

## Running the Application

* Run `docker-compose up` to start the application
* Run `docker-compose exec web python manage.py migrate` to migrate the database
* Run `docker-compose exec web python manage.py seed` to seed the database
* Run `docker-compose exec web python manage.py run` to start the application

## API Documentation

The API documentation is available at `<http://localhost:8000/docs>`.

## Road Map

(will soon convert the below items into a trello board)

* Implement Sign in with Google and Microsoft
* Implement Remember Me functionality at login
* Implement User Roles and Permission checks on all routes
* Implement MFA using TOTP
* Implement integration with AWS Cloudwatch metrics and Azure Monitor
* Implement support for collecting and analyzing OTEL metrics
* Implement Auditing user actions
* Implement active search functionality on all screens
* Implement pagination/load more on all pages
* Implement Refresh tokens for automatically refresh of auth tokens
* Implement support for Server side events/notifications
* Implement a job scheduler for maintenance tasks/scheduled tasks
* Implement Message Queue/Kafka for async tasks
* Implement Automatic CIDR block management
* Standardize and Centralize Error handling on all routes
* Standardize and Centralize Logging
* Implement History and URL-push to allow users to navigate to the previous page
* Implement protection against CSRF attacks
* Implement protection against XSS attacks
* Implement protection against MITM attacks
* Implement Inactive filter on results on all pages
* Create the necessary indexes in the SQLAlchemy Database models
* Implement htmx transition animations on all the screens
* Implement loading spinners on the login/search/ajax calls
* Implement the functionality to collapse the sidebar into icon bar
* Add docstrings to all Classes and Functions
* Create user manual for the application
* Optimize the Docker Image size using multi stage build process
