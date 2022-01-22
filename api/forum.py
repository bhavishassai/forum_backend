import random
from flask import Blueprint, jsonify, request
import mysql.connector
from ext import token_required
from api.cursor import cursor,conn

forum = Blueprint('forum',__name__)






@forum.route('/user',methods=['GET'])
@token_required
def user(userId):
    cursor.execute("SELECT * FROM users WHERE userId = %s",(userId,))
    res = cursor.fetchone()
    column_names = [i[0] for i in cursor.description]
    row = {}
    for i in range(len(column_names)):
        row[column_names[i]] = res[i]
    row.pop('hashedPassword')
    return jsonify(row),200
    



@forum.route('/question',methods=['POST'])
@token_required
def question(userId):
    try:
        data = request.json
        questionId = random.randint(100,100000)
        cursor.execute("INSERT INTO questions(questionId,title,content,userId) VALUES(%s,%s,%s,%s)",
        (questionId,
        data['title'],
        data['content'],
        userId
        ))
        conn.commit()
        return jsonify({"message":"Question added successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),401



@forum.route('/feed',methods=['GET'])
@token_required
def feed(userId):
    #fetch questions from db
    try:
        cursor.execute("SELECT * FROM questions ORDER BY createdAt DESC LIMIT 10")
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)
        print(res)    
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200

@forum.route('/replies/<questionId>',methods=['GET'])
@token_required
def replies(userId,questionId):
    #fetch replies from db
    print(questionId)
    try:
        cursor.execute("SELECT * FROM replies WHERE questionId = %s ORDER BY createdAt DESC",(questionId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            row.pop('questionId')    
            result.append(row)  
          
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200


@forum.route('/reply/<questionId>',methods=['POST'])
@token_required
def reply(userId,questionId):
    try:
        data = request.json
        replyId = random.randint(100,100000)
        cursor.execute("INSERT INTO replies(replyId,message,userId,questionId) VALUES(%s,%s,%s,%s)",
        (replyId,
        data['message'],
        userId,
        questionId
        ))
        conn.commit()
        return jsonify({"message":"Reply added successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200


@forum.route('/react/<questionId>',methods=['POST'])
@token_required
def react(userId,questionId):
    try:
        data = request.json
        reactionId = random.randint(100,100000)
        cursor.execute("INSERT INTO reactions(reactionId,userId,questionId,reactionType) VALUES(%s,%s,%s,%s)",
        (reactionId,
        userId,
        questionId,
        data['reactionType']
        ))
        conn.commit()
        return jsonify({"message":"Reaction added successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200


    


@forum.route('/unreact/<questionId>',methods=['GET'])
@token_required
def unreact(userId,questionId):
    try:
        cursor.execute("DELETE FROM reactions WHERE userId = %s AND questionId = %s",(userId,questionId))
        conn.commit()
        return jsonify({"message":"Reaction removed successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200




@forum.route('/myquestions',methods=['GET'])
@token_required
def myquestions(userId):
    #fetch questions from db
    try:
        cursor.execute("SELECT * FROM questions WHERE userId = %s ORDER BY createdAt DESC LIMIT 10",(userId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)
        print(res)    
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200


#followers
@forum.route('/followers',methods=['GET'])
def followers(userId):
    try:
        cursor.execute("SELECT * FROM followers where followeeId = %s",(userId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)
        print(res)    
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200



@forum.route('/followings',methods=['GET'])
@token_required
def following(userId):
    try:
        cursor.execute("SELECT * FROM followers where userId = %s",(userId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)
        print(res)    
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200



#search
@forum.route('/search/<name>',methods=['GET'])
@token_required
def search(userId,name):
    try:
        cursor.execute("SELECT * FROM users WHERE firstName LIKE %s OR lastName LIKE %s",('%'+name+'%','%'+name+'%'))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)
        print(res)    
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200


