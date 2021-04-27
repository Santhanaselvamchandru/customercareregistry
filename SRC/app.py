"""
    Database credentials
    Username: a7tPSqJMm4

    Database name: a7tPSqJMm4

    Password: dZRSGZReBY

    Server: remotemysql.com

    Port: 3306

    google client id - 230809809224-6dvmdva24gkp8dgku6bk114dm5gkoes1.apps.googleusercontent.com
    client secret - pYRs5szyt-Yv81ELQnxeRy6c
"""
from flask import Flask,render_template,request,url_for,session,redirect
from flask_mysqldb import MySQL
from sendmail import sendemail
from flask_oauthlib.client import OAuth
import json
from random import randint
app = Flask(__name__)

# database configuration
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'a7tPSqJMm4'
app.config['MYSQL_PASSWORD'] = 'dZRSGZReBY'
app.config['MYSQL_DB'] = 'a7tPSqJMm4'
mysql = MySQL(app)

# Google authenticate configuration
app.config['GOOGLE_ID'] = '230809809224-6dvmdva24gkp8dgku6bk114dm5gkoes1.apps.googleusercontent.com'
app.config['GOOGLE_SECRET'] = 'pYRs5szyt-Yv81ELQnxeRy6c'

app.secret_key = "customercareregistry"

oauth = OAuth(app)
# google client informations
google = oauth.remote_app(
    'google',
    consumer_key = app.config.get('GOOGLE_ID'),
    consumer_secret = app.config.get('GOOGLE_SECRET'),
    request_token_params = {
        'scope' : ['email','https://www.googleapis.com/auth/userinfo.profile'],
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

#home page
@app.route('/')
def home():
    if "google_token" in session:
        return render_template('home.html')
    if "username" in session:
        return render_template('home.html')
    return render_template('index.html')

# manually registration
@app.route('/register',methods=["POST"])
def register():
    if request.method == 'POST':
        name = request.form['uname']
        email = request.form['mail']
        pwd = request.form['pwd']
        cpwd = request.form['confirmpwd']
        if pwd != cpwd:
            msg = 'Please enter correct confirm password'
            return render_template('index.html',signupmsg=msg)
        # check account is exists or not
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * customerdeatils WHERE email = % s',(email),)
        existing_user = cursor.fetchone()
        cursor.close()
        #exits 
        if existing_user:
            msg = 'Account already exists please login.'
            return render_template('index.html',signupmsg = msg)
        #not exists
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO customerdeatils VALUES(null,% s,% s,% s)',(name,email,pwd))
        mysql.connection.commit()
        cursor.close()
        subject = 'Customer care registry account creation.'
        text = 'Account creation successfully.'
        # send mail
        sendemail(email,subject,text)
        msg = 'Your registration successfully completed.'
    return render_template('index.html',signupmsg = msg)
# manually login
@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        mail = request.form['mail1']
        password = request.form['pwd1']
        # check account is exists or not
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM customerdeatils WHERE email=% s AND password=% s',(mail,password))
        user = cursor.fetchone()
        cursor.close()
        #exists
        if user:
            return render_template('home.html')
        else:
            msg = 'mail or password is not valid.'
    return render_template('index.html',signinmsg=msg)
# google account through registration
@app.route('/google_signup')
def google_signup():
    return google.authorize(callback=url_for('google_signup_authorized',_external=True))

# google registration authorization
@app.route('/google_signup/google_signup_authorized')
def google_signup_authorized():
    resp = google.authorized_response()
    if resp:
        session['google_token'] = (resp['access_token'], '') 
        # fetch client information  
        p_json = json.dumps(google.get('userinfo').data) 
        # extract json file
        ex_json = json.loads(p_json)
        # random 6 digit password creation
        password = randint(10 ** 5,10**6)

        name = ex_json['name']
        mail = ex_json['email']
        # check account is already register or not
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM customerdeatils WHERE email LIKE % s',[mail])
        existing_user = cursor.fetchone()
        cursor.close()
        # exists
        if existing_user:
            msg = 'Account already exists please login.'
            return render_template('index.html',signupmsg = msg)
        # doesn't exist
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO customerdeatils VALUES(null,% s,% s,% s)',(name,mail,password))
        mysql.connection.commit()
        cursor.close()
        subject = 'Customer care registry account creation.'
        text = 'Account creation successfully.'
        # send mail
        sendemail(mail,subject,text)
        msg = 'Your registration successfully completed. password is {} please go to login'.format(str(password))
        return render_template('index.html',signupmsg = msg)
    else:
        msg = "Invalid response from google please try again"
        return render_template('index.html',signupmsg = msg)

# google account through login
@app.route('/google_login')
def google_login():
    return google.authorize(callback=url_for('google_login_authorized',_external=True))

#google login authorization
@app.route('/google_login/google_login_authorized')
def google_login_authorized():
    resp = google.authorized_response()
    if resp:
        session['google_token'] = (resp['access_token'], '')   
        p_json = json.dumps(google.get('userinfo').data) 
        ex_json = json.loads(p_json)
        name = ex_json['name']
        email = ex_json['email']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM customerdeatils WHERE email LIKE % s',[email])
        existing_user = cursor.fetchone()
        cursor.close()
        if not existing_user:
            msg = "Account doesn't exist please register"
            return render_template('index.html',signinmsg = msg)
        logo = {'picture' : ex_json['picture']}
        return render_template('home.html',logo = logo)
    else:
        msg = "Invalid response from google please try again"
        return render_template('index.html',signinmsg = msg)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

# logout method
@app.route('/logout')
def logout():
    if "username" in session:
        session.pop("username")
    if "google_token" in session:
        session.pop("google_token")
    return redirect(url_for('home'))

# complaint register
@app.route('/complaint',methods=['POST'])
def complaint():
    if request.method == 'POST':
        complaint_name = request.form['complaint_name']
        name = request.form['name']
        mail = request.form['email']
        against_person = request.form['against_person']
        des = request.form['complaint_des']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO complaints VALUES(NULL,% s,% s,% s,% s,% s)",(complaint_name,name,mail,against_person,des))
        mysql.connection.commit()
        cursor.close()
        msg = 'Complaint registerd you check out complaints section.'
        return render_template('home.html',msg=msg)

# show complaints and progress
@app.route('/showcomplaints')
def showcomplaints():
    return render_template('complaints.html')

# feedback
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

if __name__ == '__main__':
    app.run(port = 8080,debug=True)