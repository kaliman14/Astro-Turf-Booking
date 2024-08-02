from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import traceback

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    print("Initializing database...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            date TEXT,
            time TEXT,
            cost INTEGER,
            user_id INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeslots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            is_available BOOLEAN DEFAULT TRUE
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# def init_timeslots():
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
    
#     from datetime import datetime, timedelta
#     start_date = datetime.now()
#     for i in range(30):
#         date = start_date + timedelta(days=i)
#         for hour in range(24):  # Turf is available 24 hours a day
#             cursor.execute('''
#                 INSERT INTO timeslots (date, time)
#                 VALUES (?, ?)
#             ''', (date.strftime('%Y-%m-%d'), f'{hour:02d}:00'))
    
#     conn.commit()
#     conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user_id' not in session:
        flash('Login to book a spot', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve form data using .get() to avoid KeyError
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        user = session.get('user_id')


        # Debug: Print form data
        print(f"Booking attempt: {user}, {date}, {start_time}, {end_time}")

        # Check if all required fields are present
        if not all([date, start_time, end_time]):
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('booking'))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Check if the timeslot is available
        cursor.execute('''
            SELECT date, starttime, endtime FROM timeslots
        ''')
        timeslot = cursor.fetchall()
        cursor.execute('''
                SELECT * FROM users WHERE id = ?
            ''', (user,))
        users = cursor.fetchone()

        # Debug: Print timeslot availability
        #print(f"Timeslot availability: {timeslot}")

        from datetime import datetime
        format = '%H:%M'

        start_time_obj = datetime.strptime(start_time, format)
        end_time_obj = datetime.strptime(end_time, format)
        
        #calculate cost using time gap bla bla
        diff = end_time_obj - start_time_obj
        time_diff_min = diff.total_seconds() / 60
        time_diff = time_diff_min // 60
        cost = time_diff*100

        def isAvailable(test_date, test_time):
            format = '%H:%M'
            date_format = '%Y-%m-%d'

            now = datetime.now()
            date_now = datetime.strftime(now, date_format)
            date_now_obj = datetime.strptime(date_now, date_format)

            # test_time = booking start_time
            test_time_obj = datetime.strptime(test_time, format)
            test_date_obj = datetime.strptime(test_date, date_format)
            for i in range(0, len(timeslot)):
                #start time in de db
                time = timeslot[i][1]
                #end time in de db
                time2 = timeslot[i][2]
                ndate = timeslot[i][0]
                time_obj = datetime.strptime(time, format)
                time2_obj = datetime.strptime(time2, format)
                ndate_obj = datetime.strptime(ndate, date_format)
                if ((time_obj <= test_time_obj and test_time_obj <= time2_obj) and test_date_obj == ndate_obj) or test_date_obj < date_now_obj:
                    return False
            return True
                
                

        if isAvailable(date, start_time):
            # Proceed with booking
            cursor.execute('''
                INSERT INTO bookings (name, phone, date, starttime, endtime, cost, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (users[2], users[5], date, start_time, end_time, cost, user))
            
            # Update the timeslot to mark it as booked
            cursor.execute('''
                INSERT INTO timeslots (date, starttime, endtime)
                VALUES (?, ?, ?)
            ''', (date, start_time, end_time))
            conn.commit()
            conn.close()
            flash('Booking successful!', 'success')
            return redirect(url_for('home'))
        else:
            # Handle the case where the slot is not available
            flash('Selected time slot is not available.', 'error')
            conn.close()
            return redirect(url_for('booking'))

    # For GET requests, fetch available slots
    # conn = sqlite3.connect('database.db')
    # cursor = conn.cursor()
    # cursor.execute('SELECT * FROM timeslots')
    # available_slots = cursor.fetchall()
    # conn.close()
    
    return render_template('booking.html', available_slots=available_slots)


@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('You do not have access to this page.', 'error')
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, phone, date, starttime, endtime, cost FROM bookings')
    bookings = cursor.fetchall()

    # cursor.execute('SELECT id, name, location FROM turfs')
    # turfs = cursor.fetchall()

    conn.close()

    return render_template('admin.html', bookings=bookings)


@app.route('/register', methods=["GET", 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('Phone')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # hashed_password = generate_password_hash(password, method='sha256')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (fullname, username, email, pwd, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (full_name, username, email, password, phone))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        except Exception as e:
            flash('Error registering user. Please try again.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT * FROM users WHERE username = ? AND pwd = ?
            ''', (username, password))
            user = cursor.fetchone()
            conn.close()

            #and check_password_hash(user[4], password)@:!"£$%^&*()"
            if user:  # Assuming password is the 4th column (index 3)
                session['user_id'] = user[0]
                session['username'] = user[2]
                session['is_admin'] = user[6]
                flash('Login successful', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error logging in. Please try again later. \nError code: {e}', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Logout was successful. See you again soon', 'success')
    return redirect(url_for('home'))

@app.route('/available_slots')
def available_slots():
    date = request.args.get('date')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM timeslots WHERE date = ? AND is_available = 1', (date,))
    available_slots = cursor.fetchall()
    conn.close()
    return jsonify(available_slots)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to be logged in to view this page.', 'error')
        return redirect(url_for('login'))

    user_id = session.get("user_id")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/booking_history', methods=['GET'])
def booking_history():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        conn = sqlite3.connect('database.db')  # Use psycopg2.connect for PostgreSQL
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, phone, date, starttime, endtime, cost
            FROM bookings
            WHERE user_id = ?  
        ''', (session.get('user_id'),))  # Adjust based on how you store user ID in the session

        bookings = cursor.fetchall()
        conn.close()

        return render_template('booking_history.html', bookings=bookings)
    
    except Exception as e:
        # Print the error to the console and display a generic error message
        flash(f"An error occurred: {e}", 'error')
        traceback.print_exc()
        return "An internal error occurred. Please try again later."

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    init_db()
    # init_timeslots()
    app.run(debug=True)
