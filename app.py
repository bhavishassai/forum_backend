
from flask import Flask,jsonify, request,send_from_directory
from api.cursor import cursor
from api.auth import auth
from api.forum import forum
from ext import bcrypt


app = Flask(__name__)

bcrypt.init_app(app)
app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(forum, url_prefix='/api/forum')

@app.route('/images/profile/<path:path>')
def send_profile_image(path):
    return send_from_directory('fs/profile_images', path)



@app.route('/images/questions/<path:path>')
def send_question_post_image(path):
    return send_from_directory('fs/post_images/questions', path)


@app.route('/home',methods=['POST'])
def home():
    print("Request came")
    data = request.json
    return f"Insert {data} successful",200


app.run(host="0.0.0.0",debug=True)