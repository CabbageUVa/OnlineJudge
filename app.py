from flask import Flask, request, jsonify, make_response, render_template
from jwt.exceptions import ExpiredSignatureError, DecodeError
from datetime import datetime, timedelta
from flaskext.mysql import MySQL
# from comp_run import test
import os, string, random, jwt, time

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
conn = mysql.connect()

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
                cursor = conn.cursor()
                cursor.callproc('sp_validUser', (_username, _password))
                data = cursor.fetchall()
                if len(data) != 0:
                    # validate successfully
                    userID = data[0][1]
                    token = register_token(userID)
                    response = make_response(jsonify(code='200'))
                    response.set_cookie('token', token, max_age = 1000*60*30)
                    response.set_cookie('userID', str(userID), max_age = 1000*60*30)
                    response.set_cookie('userName', _username, max_age = 1000*60*30)
                else:
                    # incorrect info
                    response = make_response(jsonify(code='201'))
                response = set_header(response)
                return response
        except Exception as e:
            response = make_response(jsonify(code='202'))
            response = set_header(response)
            return response
        finally:
            cursor.close()


@app.route("/logout")
def logout():
    if request.method == 'POST':
        userID = request.cookies.get('userID')
        token = request.cookies.get('token')
        valid = validate_user(userID, token)
        response = make_response(jsonify(code=valid))
        if valid == 200:
            response.set_cookie('token', token, max_age=0)
        response = set_header(response)
        return response


@app.route('/signUp', methods=['POST', 'GET'])
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
                cursor = conn.cursor()
                cursor.callproc('sp_createUser', (_name, _password, _email))
                data = cursor.fetchall()
                if data[0][0] > 0:
                    # registered successfully
                    userID = data[0][0]
                    conn.commit()
                    token = register_token(userID)
                    response = make_response(jsonify(code='200'))
                    response.set_cookie('token', token, max_age=30 * 60 * 1000)
                    response.set_cookie('userName', _name, max_age=1000 * 60 * 30)
                    response.set_cookie('userID', str(userID), max_age=30 * 60 * 1000)
                elif data[0][0] == 0:
                    # existing username
                    response = make_response(jsonify(code='201'))
                elif data[0][0] == -1:
                    #existing email
                    response = make_response(jsonify(code='202'))
                response = set_header(response)
                return response
        except Exception as e:
            response = make_response(jsonify(code='203'))
            response = set_header(response)
            return response
        finally:
            cursor.close()


@app.route('/uploader', methods=['GET', 'POST'])
def compile():
    if request.method == 'POST':
        userID = request.cookies.get('userID')
        token = request.cookies.get('token')
        data = request.form
        code = data['code']
        Q_ID = data['Q_ID']

        valid = validate_user(userID, token)
        if valid != 200:
            response = make_response(jsonify(code=valid))
        else:
            cursor = conn.cursor()
            # result = test(code,Q_ID,cursor)
            result = "TEST!"
            cursor.close()
            token = register_token(userID)
            response = make_response(jsonify(code=valid, result=result))
            response.set_cookie('token', token, max_age=30 * 60 * 1000)
            response.set_cookie('userID', str(userID), max_age=30 * 60 * 1000)
        response = set_header(response)
        return response


def validate_user(userID, token):
    # status code:
    # 200 OK, 201 expired, 202 decode error/wrong ID
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


def set_header(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return resp


if __name__ == '__main__':
    app.run(host='localhost')
