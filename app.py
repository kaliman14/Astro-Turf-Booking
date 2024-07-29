from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/yourdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    turf_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f'<Booking {self.id}>'


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            date TEXT,
            time TEXT,
            cost INTEGER
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

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        user_id = request.form['user_id']
        turf_id = request.form['turf_id']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        # Convert date and times to datetime objects for validation
        try:
            booking_date = datetime.strptime(date, '%Y-%m-%d').date()
            booking_start_time = datetime.strptime(start_time, '%H:%M').time()
            booking_end_time = datetime.strptime(end_time, '%H:%M').time()
        except ValueError as e:
            return jsonify({'error': 'Invalid date or time format'}), 400

        # Perform validation and booking logic here
        if not is_time_slot_available(turf_id, booking_date, booking_start_time, booking_end_time):
            return jsonify({'error': 'Time slot is already booked'}), 400

        # Save the booking to the database
        save_booking(user_id, turf_id, booking_date, booking_start_time, booking_end_time)

        return jsonify({'success': 'Booking confirmed'}), 200

    return render_template('book.html')

def is_time_slot_available(turf_id, date, start_time, end_time):
    overlapping_bookings = Booking.query.filter(
        Booking.turf_id == turf_id,
        Booking.date == date,
        Booking.start_time < end_time,
        Booking.end_time > start_time
    ).all()

    return len(overlapping_bookings) == 0

def save_booking(user_id, turf_id, date, start_time, end_time):
    new_booking = Booking(
        user_id=user_id,
        turf_id=turf_id,
        date=date,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(new_booking)
    db.session.commit()

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

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    init_db()
    init_timeslots()
    app.run(debug=True)