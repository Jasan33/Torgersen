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
    return render_template("index.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

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

@app.route("/login")
def login():
    if request.method == "POST":
        navn = request.form['navn']
        passord = request.form['passord']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, navn, AES_DECRYPT(passord, %s)
            FROM brukere
            WHERE navn = %s
        """, (AES_KEY, navn))
        brukere = cur.fetchone() # finner den første brukeren som macher med navnet
        cur.close()

        if brukere and brukere[2].decode('utf-8') == passord:  # dekrypterer og sammenligner passord
            session['user_id'] = brukere[0]
            session['navn'] = brukere[1]  # Setter bruker i session for 24 timer så man slipper å logge in
            flash("suksess, velkommen", navn)
            return redirect(url_for('home'))
        else:
            flash("Feil innloggings matterial, venligst prøv igjen")
    
    return render_template('login.html')

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)