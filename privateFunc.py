from jwt.exceptions import ExpiredSignatureError, DecodeError
from datetime import datetime, timedelta
import jwt

SECRET_KEY = '1234456'

def validate_user(userID, token):
    # status code:
    # 200 OK, 201 expired, 202 decode error/wrong ID
    try:
        user_info = jwt.decode(token, SECRET_KEY)
        if userID == user_info['userID']:
            return 200
        else:
            return 201
    except ExpiredSignatureError as e:
        return 201
    except DecodeError as e:
        return 202


def register_token(userID, app):
    token = jwt.encode({'userID': userID,
                        'exp': datetime.utcnow() + timedelta(minutes=app.config.get('HAPYAK_JWT_LIFETIME', 60))},
                       app.config.get('JWT_KEY', SECRET_KEY))
    return token


def set_header(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return resp


def getUserProgress(cursor, userID):
    data = 0
    if userID and userID > 0:
        cursor.callproc('sp_getUserProgress', (userID))
        data = cursor.fetchall()
        data = data[0]
    return data


def set_cookie(response, token, userID, _username):
    response.set_cookie('token', token, max_age=1000 * 60 * 30)
    response.set_cookie('userID', str(userID), max_age=1000 * 60 * 30)
    response.set_cookie('userName', _username, max_age=1000 * 60 * 30)
    return response
