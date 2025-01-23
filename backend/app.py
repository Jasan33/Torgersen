from flask import Flask, render_template, request, redirect, session, url_for, flash
import random
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(
    __name__,
    template_folder="../Frontend/templates",  # Fil vei til templates
    static_folder="../Frontend/static"        # Fil vei til static
)
app.secret_key = os.getenv("SECRET_KEY")

# Mysql konfigurasjoner for databasen
app.config['MYSQL_HOST'] = os.getenv("HOST")
app.config['MYSQL_USER'] = os.getenv("USER")
app.config['MYSQL_PASSWORD'] = os.getenv("PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DATABASE")

mysql = MySQL(app)

AES_KEY = os.getenv("AES_KEY")

@app.route("/")
def home():
    navn = session.get('navn')  # Henter navn fra session (0 vis den ikke finner)
    admin = session.get('admin')  # finner fram admin fra seassion, har man en bruker kan man være admin
    cur = mysql.connection.cursor()  # Et "cursor connector" som kobler til databasen
    cur.execute("SELECT navn FROM brukere")
    folk = cur.fetchall()  # Fetcher (henter) alle rader som en liste
    cur.close()  # lukker databsen etter bruke for å spare resurrser
    return render_template('index.html', folk=folk, navn=navn, admin=admin)

@app.route("/index")
def index():
    navn = session.get('navn')
    admin = session.get('admin') 
    cur = mysql.connection.cursor()
    cur.execute("SELECT navn FROM brukere")
    folk = cur.fetchall() 
    cur.close()
    
    return render_template('index.html', folk=folk, navn=navn, admin=admin)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # sjekker vis brukeren har sent in en form, vis ja da for den følgende informasjon
        navn = request.form['navn']
        epost = request.form['epost']
        passord = request.form['passord']
        bekreft_passord = request.form['bekreft_passord']
         
        # sjekker vis passored macher med det krypterte
        if passord != bekreft_passord:
            flash("Passordet ligner ikke hverandre, vær så snill og prøv igjen")
            return render_template('register.html')

        # Legger til brukeren i databasen
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO brukere (navn, epost, password)
            VALUES (%s, %s, AES_ENCRYPT(%s, %s))
        """, (navn, epost, passord, AES_KEY)) # %S er values etter navn, epost, passord og enkrypt key
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

        # Henter eller finner brukeren fra databasen
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, navn, AES_DECRYPT(password, %s), role
            FROM brukere
            WHERE navn = %s
        """, (AES_KEY, navn))
        bruker = cur.fetchone()  # Finner den første medlemen som kyttes til navnet
        cur.close()

        # bekreft og sjekk brukerens passord
        if bruker and bruker[2].decode('utf-8') == passord: 
            session['user_id'] = bruker[0]
            session['navn'] = bruker[1]  # Setter in navn i session 
            session['role'] = bruker[3]  # setter in rolen man har i session ("admin" eller "user")

            if bruker[3] == 'admin':  # sjekk vis brukeren er admin
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
    session.clear() 
    flash("Nå er du logget ut!, takk for besøket")
    return redirect(url_for('home'))

@app.route("/bestiling")
def bestiling():
    navn = session.get('navn')
    admin = session.get('admin')

    return render_template("bestiling.html", navn=navn, admin=admin)

@app.route("/om_oss")
def om_oss():
    navn = session.get('navn')
    admin = session.get('admin')

    return render_template("om_oss.html", navn=navn, admin=admin)

@app.route("/arbeid", methods=["GET", "POST"])
def arbeid():
    if 'navn' not in session:
        flash("Vær så snill og login eller register deg før du ser denne siden, den er sensetiv.")
        return redirect(url_for('login'))
    
    navn = session.get('navn')
    admin = session.get('admin')

    if request.method == "POST":
        navn = request.form['navn']
        passord = request.form['passord']
        message = request.form['message'] 

        # Henter eller finner brukeren fra databasen
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, navn, AES_DECRYPT(password, %s), role
            FROM brukere
            WHERE navn = %s
        """, (AES_KEY, navn))
        bruker = cur.fetchone()  # Finner den første medlemen som kyttes til navnet
        cur.close()

        # bekreft og sjekk brukerens passord
        if bruker and bruker[2].decode('utf-8') == passord: 
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO arbeid (navn, messages, bruker_id)
                VALUES (%s, %s, %s)
            """, (navn, message, bruker[0]))  # bruker[0] is the id from brukere
            mysql.connection.commit()
            cur.close()

            flash("Tusen takk for ditt arbeid, vi vurderer ditt forespørsel og kommer tilbake til deg!")
            return redirect(url_for('home'))
        else:
            flash("Feil innloggingsdetaljer, vennligst prøv igjen.")
    return render_template('arbeid.html', navn=navn, admin=admin)

@app.route("/searbeid")
def searbeid():
    if 'navn' not in session:
        flash("Vær så snill og login eller register deg før du ser denne siden, den er sensetiv.")
        return redirect(url_for('login'))
    
    navn = session.get('navn')
    admin = session.get('admin')
    return render_template('searbeid.html', navn=navn, admin=admin)


@app.route("/Admin")
def Admin():
    if 'admin' not in session:
        flash("Dette er sensetiv informasjon, vis du ikke er admin kan du ikke se dette.")
        return redirect(url_for('home'))
    
    navn = session.get('navn')
    admin = session.get('admin')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, navn, epost, role FROM brukere")
    folk = cur.fetchall()
    cur.close()
    
    return render_template("Admin.html", folk=folk, navn=navn, admin=admin)

if __name__ == "__main__":
    app.run(debug=True, port=4000)