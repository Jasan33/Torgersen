from flask import Flask, render_template, request, redirect, session, url_for, flash
import random
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(
    __name__,
    template_folder="../Frontend/templates",  # Path vei til templates
    static_folder="../Frontend/static"        # Path vei til static
)
app.secret_key = os.getenv("SECRET_KEY")

# Mysql konfigurasjoner for database
app.config['MYSQL_HOST'] = os.getenv("HOST")
app.config['MYSQL_USER'] = os.getenv("USER")
app.config['MYSQL_PASSWORD'] = os.getenv("PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DATABASE")

mysql = MySQL(app)

AES_KEY = os.getenv("AES_KEY")

@app.route("/")
def home():
    navn = session.get('navn')  # Safely get 'navn' from session, default is None
    admin = session.get('admin')  # Safely get 'navn' from session, default is None
    cur = mysql.connection.cursor()  # Open a cursor object to interact with the database
    cur.execute("SELECT navn FROM brukere")
    folk = cur.fetchall()  # Fetch all rows as a list
    cur.close()  # Close the database cursor to free resources
    return render_template('index.html', folk=folk, navn=navn, admin=admin)

@app.route("/index")
def index():
    navn = session.get('navn')  # Safely get 'navn' from session, default is None
    cur = mysql.connection.cursor()  # Open a cursor object to interact with the database
    cur.execute("SELECT navn FROM brukere")
    folk = cur.fetchall()  # Fetch all rows as a list
    cur.close()  # Close the database cursor to free resources
    
    return render_template('index.html', folk=folk, navn=navn)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # sjekker vis brukeren har sent in en form, her feacher den
        navn = request.form['navn']
        epost = request.form['epost']
        passord = request.form['passord']
        bekreft_passord = request.form['bekreft_passord']
         
        # Checks if the passwords matchs
        if passord != bekreft_passord:
            flash("Passordet og bekreft passord ligner ikke hverandre, vær så snill prøv igjen")
            return render_template('register.html')

        # Adds the user to redtype's database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO brukere (navn, epost, password)
            VALUES (%s, %s, AES_ENCRYPT(%s, %s))
        """, (navn, epost, passord, AES_KEY))
        mysql.connection.commit()
        cur.close()
        
        flash("Registration successful! Please log in")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        navn = request.form['navn']
        passord = request.form['passord']

        # Fetch the user from the database
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, navn, AES_DECRYPT(password, %s), role
            FROM brukere
            WHERE navn = %s
        """, (AES_KEY, navn))
        bruker = cur.fetchone()  # Fetch the first user that matches
        cur.close()

        # Verify the user's password
        if bruker and bruker[2].decode('utf-8') == passord:  # Decrypt and compare password
            session['user_id'] = bruker[0]
            session['navn'] = bruker[1]  # Store user name in session
            session['role'] = bruker[3]  # Store user role in session

            if bruker[3] == 'admin':  # Check if the user is an admin
                session['admin'] = True
                flash(f"Velkommen, {bruker[1]}! Du er logget inn som admin.")
            else:
                session['admin'] = False
                flash(f"Velkommen, {bruker[1]}!")

            return redirect(url_for('home'))
        else:
            flash("Feil innloggingsdetaljer, vennligst prøv igjen.")
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out!")
    return redirect(url_for('home'))

@app.route("/bestiling")
def bestiling():
    return render_template("bestiling.html")

@app.route("/om_oss")
def om_oss():
    return render_template("om_oss.html")

@app.route("/tabel")
def tabel():
    if 'username' not in session:
        flash("Vær så snill og login eller register deg før du ser denne siden, den er sensetiv.")
        return redirect(url_for('login'))
    
    username = session['username']
    cur = mysql.connection.cursor() # Opens a cursor object to interact with the database.
    cur.execute("SELECT username, level, total_words FROM user ORDER BY total_words DESC")
    people = cur.fetchall() # Gets all rows as a list
    cur.close() # closes the database to free resources
    return render_template('tabel.html', people=people, username=username)


@app.route("/Admin")
def Admin():
    return render_template("Admin.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)