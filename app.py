from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            date TEXT,
            time TEXT
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

def init_timeslots():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    from datetime import datetime, timedelta
    start_date = datetime.now()
    for i in range(30):
        date = start_date + timedelta(days=i)
        for hour in range(24):  # Turf is available 24 hours a day
            cursor.execute('''
                INSERT INTO timeslots (date, time)
                VALUES (?, ?)
            ''', (date.strftime('%Y-%m-%d'), f'{hour:02d}:00'))
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['Phone']
        date = request.form['date']
        time = request.form['time']

        cursor.execute('''
            SELECT is_available FROM timeslots
            WHERE date = ? AND time = ?
        ''', (date, time))
        timeslot = cursor.fetchone()

        if timeslot and timeslot[0]:
            cursor.execute('''
                INSERT INTO bookings (name, phone, date, time)
                VALUES (?, ?, ?, ?)
            ''', (username, phone, date, time))
            
            cursor.execute('''
                UPDATE timeslots SET is_available = 0
                WHERE date = ? AND time = ?
            ''', (date, time))
            conn.commit()
            conn.close()
            return redirect(url_for('home'))
        else:
            flash('Selected time slot is not available.')
            return redirect(url_for('booking'))

    cursor.execute('SELECT * FROM timeslots WHERE is_available = 1')
    available_slots = cursor.fetchall()
    conn.close()
    return render_template('booking.html', available_slots=available_slots)

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('You do not have access to this page.')
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings')
    bookings = cursor.fetchall()
    conn.close()
    return render_template('admin.html', bookings=bookings)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # hashed_password = generate_password_hash(password, method='sha256')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password, phone, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password, phone, False))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            print('Username already exists. Please choose a different username.')
            return redirect(url_for('register'))
        except Exception as e:
            flash('Error registering user. Please try again later.')
            print(e)
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE username = ? and password = ?
        ''', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[5]
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
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
        flash('You need to be logged in to view this page.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/booking_history')
def booking_history():
    if 'user_id' not in session:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE name = (SELECT username FROM users WHERE id = ?)', (user_id,))
    bookings = cursor.fetchall()
    conn.close()

    return render_template('booking_history.html', bookings=bookings)



if __name__ == '__main__':
    init_db()
    init_timeslots()
    app.run(debug = True)
