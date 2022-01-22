from functools import wraps
from flask import jsonify,request
from flask_bcrypt import Bcrypt
import jwt

MY_SECRET_KEY = 'super@secret?=key'
bcrypt = Bcrypt()




def token_required(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    authorisationHeader = request.headers.get("Authorization")
    if not authorisationHeader:
      return jsonify({"message":"Token is missing"}), 401
    token = authorisationHeader.split(" ")[1]
    try:
      data = jwt.decode(token,MY_SECRET_KEY,algorithms=['HS256'])
      userId = data["userId"]
    except:
      return jsonify({"message":"Token is invalid"}), 401
    return f(userId,*args, **kwargs)
  return decorator
