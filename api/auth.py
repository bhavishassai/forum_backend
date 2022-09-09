import mimetypes
import os
from flask import Blueprint,request,jsonify
from api.cursor import cursor,conn
import datetime
import jwt
from ext import BASE_USER_PROFILE_URL_PATH, MY_SECRET_KEY, PROFILE_IMAGE_UPLOAD_PATH, bcrypt, token_required
import mysql.connector
import random
from functools import wraps

auth = Blueprint('auth',__name__)


@auth.route('/login',methods=['POST'])
def login():
    data = request.json
    print(data["email"])
    cursor.execute("SELECT * FROM users WHERE email = %s",(data['email'],))
    res = cursor.fetchone()
    userId = res[0]
    hashedPassword = res[4]
    if bcrypt.check_password_hash(hashedPassword,data['password']):
        token = jwt.encode({'email':data['email'],"userId":userId,"exp":datetime.datetime.utcnow()+datetime.timedelta(days=1)}, MY_SECRET_KEY)
        return jsonify({"message":"Login successful","token":token,"userId":userId}),200
    else:
        return jsonify({"message":"Invalid username or password"}),401


@auth.route('/register',methods=['POST'])
def register():
    data = request.json
    password = data['password']
    hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
    email = data['email']
    firstName = data['firstName']
    lastName = data['lastName']
    dob = data['dob']
    phone = data['phone']
    gender = data['gender']
    userId = random.randint(100,100000)
    try:
      cursor.execute("INSERT INTO users(userId,email, firstName, lastName, dob, phone,gender,hashedPassword) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
      (userId,
      email,
      firstName,
      lastName,
      dob,
      phone,
      gender,
      hashedPassword
      ))
      conn.commit()
      token = jwt.encode({'email':data['email'],"userId":userId,"exp":datetime.datetime.utcnow()+datetime.timedelta(days=1)}, MY_SECRET_KEY)
      return jsonify({"message":"Registration successful","token":token,"userId":userId}),200
    except  mysql.connector.Error as err:
      return jsonify({"status":"Registration Failed","message":str(err)}),500
  


#route to set profile image
@auth.route('/setProfileImage',methods=['POST'])
@token_required
def setProfileImage(userId):
  profilePhotoFile = request.files.get("profilePhoto")
  if profilePhotoFile:
    filename = profilePhotoFile.filename
    mimeType = mimetypes.guess_type(filename)
    print(mimeType[0])
    if mimeType[0] == "image/jpeg" or mimeType[0] == "image/png":
      extType = mimeType[0].split("/")[1]
      imageUrl = BASE_USER_PROFILE_URL_PATH+"/"+str(userId)+"."+extType
      print(imageUrl)
      try:
        path = os.path.join(PROFILE_IMAGE_UPLOAD_PATH,str(userId)+"."+extType)
        print(path)
        profilePhotoFile.save(path)
      except Exception as e:
        return jsonify({"message":"Error in uploading profile photo "+str(e)}),400
      cursor.execute("UPDATE users SET imageUrl = %s WHERE userId = %s",(imageUrl,userId))
      conn.commit()  
      return jsonify({"message":"Profile photo uploaded successfully"}),200
    else:
      return jsonify({"message":"Invalid file type"}),400
  else:
    return jsonify({"message":"No profile photo found"}),400



      
    
    
       

@auth.route('/logout',methods=['POST'])
@token_required
def logout():
  # TODO
  return jsonify({"message":"Logout successful"}),200