"""
    Database credentials
    Username: a7tPSqJMm4

    Database name: a7tPSqJMm4

    Password: dZRSGZReBY

    Server: remotemysql.com

    Port: 3306
"""
from flask import Flask,render_template,request
from flask_mysqldb import MySQL
import MySQLdb.cursors


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'a7tPSqJMm4'
app.config['MYSQL_PASSWORD'] = 'dZRSGZReBY'
app.config['MYSQL_DB'] = 'a7tPSqJMm4'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register',methods=["POST"])
def register():
    if request.method == 'POST':
        name = request.form['uname']
        email = request.form['mail']
        pwd = request.form['pwd']
        cpwd = request.form['confirmpwd']
        if pwd != cpwd:
            msg = 'Please enter correct password'
            return render_template('index.html',signupmsg=msg)
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO customerdeatils VALUES(null,% s,% s,% s)',(name,email,pwd))
        mysql.connection.commit()
        msg = 'Your registration successfully completed.'
    return render_template('index.html',signupmsg = msg)


if __name__ == '__main__':
    app.run(debug=True)