from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_bcrypt import Bcrypt
import mysql.connector
import smtplib
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

bcrypt = Bcrypt(app)
socketio = SocketIO(app)

def get_db_connection():
    conn = mysql.connector.connect(
        host="hopper.proxy.rlwy.net",
        user="root",
        password="zxyxhaUVPDNCsUSCEhEtVrPPTdlRnMIe",
        database="Event",
        port=45920
    )
    return conn

def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

def fetch_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.route('/')
def index():
    events = fetch_query("SELECT * FROM event")
    return render_template('index.html', events=events)

@app.route('/post_event', methods=['GET', 'POST'])
def post_event():
    if request.method == 'POST':
        params = (
            request.form.get('name'), request.form.get('address'), request.form.get('date'), 
            request.form.get('time'), request.form.get('phone'), request.form.get('domain'), 
            request.form.get('max_participants')
        )
        query = """
            INSERT INTO event (name, address, date, time, phone, domain, max_participants)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(query, params)
        return redirect(url_for('index'))
    return render_template('post_event.html')

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):
    event = fetch_query("SELECT * FROM event WHERE id = %s", (event_id,))
    if not event:
        return "Event not found", 404
    
    if request.method == 'POST':
        if 'user_id' not in session:
            return "User not logged in", 403
        params = (
            event_id, session['user_id'], request.form['name'], request.form['phone'],
            request.form.get('team_members', ''), request.form['college_name'], 
            request.form['branch'], request.form['year']
        )
        query = """
            INSERT INTO registration (event_id, user_id, name, phone, team_members, college_name, branch, year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            execute_query(query, params)
        except Exception as e:
            return str(e), 500
        return redirect(url_for('event_detail', event_id=event_id))
    
    return render_template('register.html', event=event[0])

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = fetch_query("SELECT * FROM event WHERE id = %s", (event_id,))
    registrations = fetch_query("SELECT * FROM registration WHERE event_id = %s", (event_id,))
    return render_template('event_detail.html', event=event[0], registrations=registrations)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = fetch_query("SELECT * FROM user WHERE email = %s", (request.form['email'],))
        if user and bcrypt.check_password_hash(user[0]['password'], request.form['password']):
            session['user_id'] = user[0]['id']
            return redirect(url_for('index'))
        return 'Invalid email or password', 401
    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        params = (
            request.form['name'], request.form['email'], 
            bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        )
        query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
        try:
            execute_query(query, params)
        except Exception as e:
            return str(e), 500
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = fetch_query("SELECT * FROM user WHERE id = %s", (session['user_id'],))[0]
    upcoming_events = fetch_query("""
        SELECT * FROM event 
        WHERE date >= CURDATE() 
        AND id IN (SELECT event_id FROM registration WHERE user_id = %s)
    """, (user['id'],))
    past_events = fetch_query("""
        SELECT * FROM event 
        WHERE date < CURDATE() 
        AND id IN (SELECT event_id FROM registration WHERE user_id = %s)
    """, (user['id'],))
    badge = 'gold' if len(fetch_query("SELECT * FROM registration WHERE user_id = %s", (user['id'],))) > 10 else 'red' if len(fetch_query("SELECT * FROM registration WHERE user_id = %s", (user['id'],))) > 5 else None
    return render_template('profile.html', user=user, upcoming_events=upcoming_events, past_events=past_events, badge=badge)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    socketio.run(app, host="0.0.0.0", port=port)
