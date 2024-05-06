# Ticket Management System

This project is a Ticket Management System built with Django and PostgreSQL, with image uploading functionality integrated with Cloudinary. It provides RESTful APIs for managing tickets and uploading images.

## Prerequisites

Before running the project, ensure you have the following installed:

- Python (3.x recommended)
- PostgreSQL
- Redis (for background job processing)
- Cloudinary account (for image storage)

## Installation

1. Clone the repository:
    ```
    git clone <repository-url>
    cd hopla
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Set up PostgreSQL:

   - Create a PostgreSQL database for the project.
   - Update the database settings in `settings.py`.

4. Set up environment variables:

   - Create a `.env` file in the project root directory.
   - Add the following environment variables to the `.env` file:
     ```
     DATABASE_URL=postgresql://<username>:<password>@localhost/<database-name>
     CLOUDINARY_URL=cloudinary://<api-key>:<api-secret>@<cloud-name>
     ```

5. Apply database migrations:
    ```
    python manage.py migrate
    ```


6. Run the development server:
    ```
    python manage.py runserver
    ```

7. Run the background tasks:
    ```
    python manage.py rqworker default
    ```

8. Run tests:
    ```
    python manage.py test
    ```

The server should now be running locally at `http://localhost:8000/`.

## Usage

### API Documentation

API documentation is provided using Swagger UI. You can access it at the following URLs:

- **Swagger UI**: `http://localhost:8000/documentation/`
- **Swagger redoc Schema**: `http://localhost:8000/redoc`

### API Endpoints

- **Create Ticket**: `POST /api/v1/tickets/`
- **Upload Image to Ticket**: `POST /api/v1/tickets/<ticket-id>/images/`
- **List and Filter Tickets**: `GET /api/v1/tickets/`

### Authentication

- Authentication is token-based. Obtain a token by logging in using the `/api/v1/auth/login/` endpoint.

### Background Image Upload

- Images uploaded to a ticket are processed in the background using `django_rq`. Ensure `redis-server` is running locally.


## License

This project is licensed under the MIT License. See the LICENSE file for details.

# Project Improvements

Here are some potential improvements that can be made to the project:

1. **Pagination and Filtering**: Implement more advanced pagination and filtering options for the list of tickets endpoint. This could include sorting by different fields, filtering by additional criteria, and providing more robust pagination options.

2. **Error Handling**: Enhance error handling throughout the project by providing more informative error messages and handling edge cases more gracefully. This can improve the user experience and make troubleshooting easier.

3. **Logging**: Implement logging throughout the project to track important events, errors, and user actions. This can help with debugging, monitoring, and auditing of the application.

4. **Input Validation**: Strengthen input validation for API endpoints to ensure that invalid or malicious input is rejected early and securely. This can help prevent security vulnerabilities such as SQL injection and cross-site scripting (XSS) attacks.

5. **Unit Tests**: Increase unit test coverage to ensure that all components of the application are functioning correctly and to catch regressions when making changes or adding new features.

6. **Performance Optimization**: Identify and address performance bottlenecks in the application to improve response times and scalability. This could involve optimizing database queries, caching frequently accessed data, and using more efficient algorithms and data structures.

7. **Documentation**: Improve documentation by adding inline comments, docstrings, and README files to provide clear guidance on how to use and contribute to the project. This can make the codebase more understandable and accessible to developers.

8. **Authentication and Authorization**: Enhance authentication and authorization mechanisms to support more granular access control and role-based permissions. This can help enforce security policies and protect sensitive data.

9. **Internationalization and Localization**: Add support for internationalization (i18n) and localization (l10n) to make the application accessible to users from different regions and languages.

10. **Automated Deployment**: Set up automated deployment pipelines to streamline the process of deploying updates to production environments. This can include continuous integration (CI) and continuous deployment (CD) workflows using tools like Jenkins, GitLab CI/CD, or GitHub Actions.

These improvements can help enhance the functionality, security, usability, and maintainability of the project over time.








