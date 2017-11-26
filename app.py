from flask import Flask, request, jsonify, make_response, render_template
from jwt.exceptions import ExpiredSignatureError, DecodeError
from datetime import datetime, timedelta
from flaskext.mysql import MySQL
#from comp_run import test
import os, string, random, jwt

app = Flask(__name__)
SECRET_KEY = '1234456'
app.config['UPLOAD_FOLDER'] = 'uploads'

# MySQL config
app.config['MYSQL_DATABASE_USER'] = 'OJadmin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cloudcomputing'
app.config['MYSQL_DATABASE_DB'] = 'OJDatabase'
app.config['MYSQL_DATABASE_HOST'] = 'ojdb.cz7ykkiaaafu.us-east-1.rds.amazonaws.com'
mysql = MySQL()
mysql.init_app(app)

'''
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!  <a href='/logout'>Logout</a>"
'''
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
@app.route('/login', methods=['POST'])
def userLogin():
    # login code :
    # 200 OK, 201 wrong password, 202 unknown error
    
    if request.method == 'POST':
        data = request.form
        _username = data['username']
        _password = data['passwd']
        
        try:
            if _username and _password:
                # all good, validate userinfo
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.callproc('sp_validUser',(_username,_password))
                data = cursor.fetchall()
                print("validUser")
                if len(data) != 0:
                # validate successfully
                    print("validated")
                    userID = data[0][1]
                    token = register_token(userID)
                    response = make_response(jsonify(code = "200"))
                    print("after json")
                    response.set_cookie('token', token)
                    response.set_cookie('userID', str(userID))
                    response.set_cookie('userName', _username)

                else:
                    # incorrect info
                    response = make_response(jsonify({'code' : 201}))
                
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'

                return response
        except Exception as e:
            print e
            response = make_response(jsonify({'code' : 202})) 
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            return response

        finally:
            cursor.close() 
            conn.close()

@app.route("/logout")
def logout():
    if request.method == 'POST':
        userID = request.cookies.get('userID')
        token = request.cookies.get('token')
        valid = validate_user(userID, token)
        if valid != 200:
            response = make_response(jsonify({'code' : valid}))
        else:
            response.set_cookie('token', token, max_age=0)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@app.route('/signUp', methods=['POST','GET'])
def signUp():
    if request.method == 'POST':
        data = request.form
        _name = data['username']
        _email = data['email']
        _password = data['passwd']

        try:
            # validate the received values
            if _name and _email and _password:
                # All Good, let's call MySQL
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.callproc('sp_createUser',(_name,_password,_email))
                data = cursor.fetchall()

                if len(data) != 0 and data[0][0] != -1:
                # registered successfully
                    userID = data[0][0]
                    conn.commit()
                    token = register_token(userID)
                    response = make_response(jsonify({'code' : 200})) 
                    response.set_cookie('token', token, max_age = 60*60*1000)
                    response.set_cookie('userID', userID, max_age = 60*60*1000)
                else:
                    response = make_response(jsonify({'code' : 201})) 
                    
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
                
        except Exception as e:
            response = make_response(jsonify({'code' : 202})) 
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        finally:
            cursor.close() 
            conn.close()

        
@app.route('/uploader', methods = ['GET', 'POST'])
def compile():
    if request.method == 'POST':
        userID = request.cookies.get('userID')
        token = request.cookies.get('token')
        data = request.form
        code = data['code']
        Q_ID = data['Q_ID']
        
        valid = validate_user(userID, token)
        if valid != 200:
            response = make_response(jsonify({'code' : valid}))
        else:
            conn = mysql.connect()
            cursor = conn.cursor()
            #result = test(code,Q_ID,cursor)
            result = "TEST!"
            cursor.close() 
            conn.close()
            token = register_token(userID)
            response = make_response(jsonify({'result' : result}))
            response.set_cookie('token', token, max_age = 60*60*1000)
            response.set_cookie('userID', userID, max_age = 60*60*1000)

        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

def validate_user(userID, token):
    # status code:
    # 100 OK, 101 expired, 102 decode error/wrong ID
    try:
        user_info = jwt.decode(token, SECRET_KEY)
        if userID == user_info['userID']:
            return 200
        else:
            return 202
    except ExpiredSignatureError as e:
        return 201
    except DecodeError as e:
        return 202
        
def register_token(userID):
    token = jwt.encode({'userID': userID,
                        'exp': datetime.utcnow() + timedelta(minutes=app.config.get('HAPYAK_JWT_LIFETIME', 60))},
                       app.config.get('JWT_KEY', SECRET_KEY))
    return token

if __name__ == '__main__':
    app.run(host='0.0.0.0')
