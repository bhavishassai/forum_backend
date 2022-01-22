
from flask import Flask,jsonify, request
from api.cursor import cursor
from api.auth import auth
from api.forum import forum
from ext import bcrypt


app = Flask(__name__)

bcrypt.init_app(app)
app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(forum, url_prefix='/api/forum')

@app.route('/')
def index():
    cursor.execute("SELECT * FROM users LIMIT 4")
    rows = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    result = []
    for j in range(len(rows)):
      row = {}
      for i in range(len(column_names)):
        row[column_names[i]] = rows[j][i]
      result.append(row)
    return jsonify(result)


@app.route('/home',methods=['POST'])
def home():
    print("Request came")
    data = request.json
    return f"Insert {data} successful",200


app.run(debug=True)