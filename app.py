from flask import Flask, request, jsonify, make_response, render_template
from flaskext.mysql import MySQL
from privateFunc import validate_user, register_token, set_header, getUserProgress, set_cookie
from compileAndRun import test


app = Flask(__name__)
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


@app.route('/problemList', methods=['GET', 'POST'])
def problemList():
    return render_template('problemlist.html')

@app.route('/problem/<problemNumber>', methods=['GET', 'POST'])
def problem(problemNumber):
    return render_template('problem.html', problemNumber = problemNumber)


@app.route('/getProblemList', methods=['GET', 'POST'])
def getProblemList():
    try:
        userID = request.cookies.get('userID')
        token = request.cookies.get('token')
        username = request.cookies.get('userName')
    except Exception as e:
        print(e)
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_getProblemList', (0, 20))
        data = cursor.fetchall()
        userProgress = getUserProgress(cursor, userID)
        cursor.close()
        response = make_response(jsonify(code = '200', problemSet=data, progress=userProgress))
        response = set_header(response)
        if userID and userID > 0:
            response = set_cookie(response, token, userID, username)
        return response
    except Exception as e:
        print(e)
        response = make_response(jsonify(code = '202'))
        response = set_header(response)
        return response


@app.route('/login', methods=['POST'])
def userLogin():
    # login code :
    # 200 OK, 201 wrong password, 202 unknown error
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = data['passwd']
        try:
            if username and password:
                # all good, validate userinfo
                cursor = conn.cursor()
                cursor.callproc('sp_validUser', (username, password))
                data = cursor.fetchall()
                if len(data) != 0:
                    # validate successfully
                    userID = data[0][1]
                    token = register_token(userID, app)
                    response = make_response(jsonify(code='200'))
                    response = set_cookie(response, token, userID, username)

                else:
                    # incorrect info
                    response = make_response(jsonify(code='201'))
                response = set_header(response)
                return response
        except Exception as e:
            print(e)
            response = make_response(jsonify(code='202'))
            response = set_header(response)
            return response
        finally:
            cursor.close()


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    if request.method == 'POST':
        data = request.form
        username = data['username']
        email = data['email']
        password = data['passwd']
        try:
            # validate the received values
            if username and email and password:
                # All Good, let's call MySQL
                cursor = conn.cursor()
                cursor.callproc('sp_createUser', (username, password, email))
                data = cursor.fetchall()
                if data[0][0] > 0:
                    # registered successfully
                    userID = data[0][0]
                    conn.commit()
                    token = register_token(userID)
                    response = make_response(jsonify(code='200'))
                    response = set_cookie(response, token, userID, username)

                elif data[0][0] == 0:
                    # existing username
                    response = make_response(jsonify(code='201'))
                elif data[0][0] == -1:
                    #existing email
                    response = make_response(jsonify(code='202'))
                response = set_header(response)
                return response
        except Exception as e:
            print(e)
            response = make_response(jsonify(code='203'))
            response = set_header(response)
            return response
        finally:
            cursor.close()


@app.route('/uploader', methods=['GET', 'POST'])
def compile():
    msg = {0:'Wrong answer', 1: 'Accepted!', 200:'Success',404:'file not found',400:'Compile error',408:'Timeout'}
    if request.method == 'POST':
        try:
            userID = request.cookies.get('userID')
            token = request.cookies.get('token')
            username = request.cookies.get('userName')
            data = request.form
            code = data['code']
            Q_ID = data['Q_ID']

            valid = validate_user(userID, token)
            if valid != 200:
                response = make_response(jsonify(code=valid))
            else:
                cursor = conn.cursor()
                result = test(code,Q_ID,cursor)
                flag = 1 if result == '1' else 0
                cursor.callproc('sp_updateProgress', (userID, Q_ID, flag))
                cursor.commit()
                cursor.close()
                token = register_token(userID)
                response = make_response(jsonify(code=valid, result=msg[result]))
                response = set_cookie(response, token, userID, username)
            response = set_header(response)
            return response

        except Exception as e:
            print(e)
            response = make_response(jsonify(code='202'))
            response = set_header(response)
            return response


@app.route('/problemDetail', methods=['GET', 'POST'])
def pDetail():
    try:
        userID = request.cookies.get('userID')
        token = request.cookies.get('token')
        username = request.cookies.get('userName')
        QID = request.form['QID']

        cursor = conn.cursor()
        cursor.callproc('sp_getProblemDetail', (QID))
        data = cursor.fetchall()[0]
        cursor.close()
        response = make_response(jsonify(
            code='200', QID = data[0],
            title=data[1], description=data[2],
            difficulty=data[3], pSubmitNum=data[4],
            pAcceptNum=data[5], defaultCode=data[6]))
        response = set_header(response)
        if userID and userID > 0:
            response = set_cookie(response, token, userID, username)
        return response
    except Exception as e:
        print(e)
        response = make_response(jsonify(code = '202'))
        response = set_header(response)
        return response


if __name__ == '__main__':
    app.run(host='localhost', port=80)
