from functools import wraps
from flask import jsonify,request
from flask_bcrypt import Bcrypt
import jwt
from dotenv import load_dotenv
from os import environ

load_dotenv()


MY_SECRET_KEY = environ.get("MY_SECRET_KEY")
HOST = environ.get("HOST")
bcrypt = Bcrypt()


PROFILE_IMAGE_UPLOAD_PATH = r"D:\PythonProjects\forum_backend\fs\profile_images"
QUESTION_POST_IMAGE_UPLOAD_PATH = r"D:\PythonProjects\forum_backend\fs\post_images\questions"
BASE_USER_PROFILE_URL_PATH = f"http://{HOST}/images/profiles"
BASE_USER_QUESTION_POST_URL_PATH = f"http://{HOST}/images/questions"
BASE_STRATEGY_DATA_URL = f"http://{HOST}/strategies/data"
BASE_STRATEGY_PY_URL = f"http://{HOST}/strategies/py"

STRATEGIES_DATA_FILE_PATH = r"D:\PythonProjects\forum_backend\fs\strategies\data"
STRATEGIES_PY_FILE_PATH = r"D:\PythonProjects\forum_backend\fs\strategies\py"



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
