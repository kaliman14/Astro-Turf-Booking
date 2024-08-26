# Astro Turf Booking System

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Project Overview
The Astro Turf Booking System is a web-based application designed to streamline the process of booking Astro Turf facilities for sports events. The system allows users to create accounts, book for specific time slots, and view their booking history. Administrators can view all bookings, and oversee the overall system operations.

## Features
- **User Registration and Login**: Users can register for an account and log in to access booking features.
- **Turf Booking**: Users can view available turfs and book them for specific dates and times.
- **Admin Panel**: Admins can add new turfs, manage existing ones, and view all bookings.
- **Booking Conflict Resolution**: The system checks for conflicts and informs users if their desired time slot is unavailable.
- **Booking History**: Users can view their past bookings in a dedicated section.

## Technologies Used
- **Backend**: Flask (Python), SQLite
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Database**: SQLite
- **Version Control**: Git

## Installation
To set up the Astro Turf Booking System locally, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/kaliman14/astro-turf-booking.git
    cd astro-turf-booking
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database**:
    ```bash
    python setup_db.py
    ```

5. **Run the application**:
    ```bash
    flask run
    ```

6. **Access the application**:
   - Open your browser and go to `http://127.0.0.1:5000`.

## Usage
- **User Registration**: Sign up with a username, email, phone number, and password.
- **Turf Booking**: After logging in, choose your desired time and book a slot.
- **Admin Panel**: Admins can log in to access additional features like managing turfs and viewing all bookings.

## Database Schema
The database is structured as follows:

- **Users Table**:
    - `id`: Primary key
    - `full_name`: User's full name
    - `username`: Unique username
    - `email`: Unique email address
    - `password`: Hashed password
    - `phone`: User's phone number
    - `is_admin`: Boolean flag for admin users

- **Bookings Table**:
    - `id`: Primary key
    - `name`: Foreign key to the Users table
    - `phone`: Foreign key to the users table
    - `date`: Date of the booking
    - `starttime`: start tiime of the booking
    - `starttime`: end time of the booking
      
## API Endpoints
- **GET /register**: Registration page for new users.
- **POST /register**: Handles user registration.
- **GET /login**: Login page for existing users.
- **POST /login**: Handles user login.
- **GET /bookings**: Displays available turfs and booking options.
- **POST /bookings**: Processes turf booking requests.
- **GET /admin**: Admin panel for managing turfs and viewing bookings.

## Future Enhancements
- **Payment Integration**: Allow users to pay for bookings online.
- **Mobile App**: Develop a mobile application for easier access.
- **Advanced Analytics**: Provide admins with reports and analytics on turf usage.

## Contributing
Contributions are welcome! Please fork this repository and submit a pull request for any features, bug fixes, or enhancements.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
