from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import json
import mimetypes
import random
from flask import Blueprint, jsonify, request
from matplotlib.pyplot import title
import mysql.connector
from mysqlx import Row
from ext import BASE_STRATEGY_DATA_URL, BASE_STRATEGY_PY_URL, BASE_USER_QUESTION_POST_URL_PATH, QUESTION_POST_IMAGE_UPLOAD_PATH, STRATEGIES_DATA_FILE_PATH, STRATEGIES_PY_FILE_PATH, token_required
from api.cursor import cursor,conn
import backtrader as bt
import pandas as pd


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
    cursor.execute("SELECT count(*) as followerCount FROM follows WHERE followeeId = %s",(userId,))
    followerCountRes = cursor.fetchone()
    cursor.execute("SELECT count(*) as followingCount FROM follows WHERE userId = %s",(userId,))
    followingCountRes = cursor.fetchone()
    cursor.execute("SELECT count(*) as postCount FROM questions WHERE userId = %s",(userId,))
    postCountRes = cursor.fetchone()
    row['followerCount'] = followerCountRes[0]
    row['followingCount'] = followingCountRes[0]
    row['postCount'] = postCountRes[0]
    return jsonify(row),200
    



@forum.route('/question',methods=['POST'])
@token_required
def question(userId):
        jsonData = request.values.get('json')
        data = None
        if jsonData:
            data = json.loads(jsonData)
        else:
            data = request.json
        image = request.files.get('image')
        questionId = random.randint(100,100000)
        cursor.execute("SELECT * FROM questions WHERE questionId = %s",(questionId,))
        res = cursor.fetchone()
        imageUrl = None
        if not res:
            if image:
                mimeType = mimetypes.guess_type(image.filename)[0]
                if mimeType == 'image/jpeg' or mimeType == 'image/png':
                    extType = mimeType.split('/')[1]
                    imageUrl = BASE_USER_QUESTION_POST_URL_PATH+"/"+str(questionId)+"."+extType
                    image.save(f"{QUESTION_POST_IMAGE_UPLOAD_PATH}/{questionId}.{mimeType.split('/')[1]}")
                else:
                    return jsonify({"message":"Invalid image format"}),400
            try:
                cursor.execute("INSERT INTO questions(questionId,title,content,userId,imageUrl) VALUES(%s,%s,%s,%s,%s)",
                (questionId,
                data['title'],
                data['content'],
                userId,
                imageUrl,
                ))
                conn.commit()
                return jsonify({"message":"Question added successfully"}),200
            except mysql.connector.Error as err:
                return jsonify({"message":str(err)}),401

        
    



@forum.route('/feed',methods=['GET'])
@token_required
def feed(userId):
    try:
        cursor.execute("SELECT * FROM questions ORDER BY createdAt DESC LIMIT 10")
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                if(column_names[i]=="userId"):
                    cursor.execute("SELECT * FROM users WHERE userId = %s",(res[j][i],))
                    user = cursor.fetchone()
                    column_names_user = [l[0] for l in cursor.description]
                    userRow = {}
                    for k in range(len(column_names_user)):
                        userRow[column_names_user[k]] = user[k]
                    userRow.pop('hashedPassword')
                    row["postedBy"] = userRow

                if(column_names[i]=="questionId"):
                    cursor.execute("SELECT * FROM reactions WHERE questionId = %s AND userId = %s",(res[j][i],userId))
                    reaction = cursor.fetchone()
                    #get the count of reactions
                    cursor.execute("SELECT COUNT(*) FROM REACTIONS WHERE questionId = %s",(res[j][i],))
                    reactionCount = cursor.fetchone()
                    row["reactionCount"] = reactionCount[0]
                    if(reaction):
                        row["isLiked"] = True
                    else:
                        row["isLiked"] = False
                row[column_names[i]] = res[j][i]
            row.pop("userId")
            result.append(row)
           
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200

@forum.route('/replies/<questionId>',methods=['GET'])
@token_required
def replies(userId,questionId):
    #fetch replies from db
    try:
        cursor.execute("SELECT R.*,U.firstName  FROM replies R JOIN users U ON R.userId=U.userId WHERE questionId = %s ORDER BY createdAt DESC",(questionId,))
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
        return jsonify({"message":str(err)}),400


@forum.route('/react/<questionId>',methods=['POST'])
@token_required
def react(userId,questionId):
    try:
        data = request.json
        #reactionId = random.randint(100,100000)
        cursor.execute("INSERT INTO reactions(userId,questionId,reactionType) VALUES(%s,%s,%s)",
        (
        userId,
        questionId,
        data['reactionType']
        ))
        conn.commit()
        return jsonify({"message":"Reaction added successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500


    


@forum.route('/unreact/<questionId>',methods=['GET'])
@token_required
def unreact(userId,questionId):
    try:
        cursor.execute("DELETE FROM reactions WHERE userId = %s AND questionId = %s",(userId,questionId))
        conn.commit()
        return jsonify({"message":"Reaction removed successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500




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
                if(column_names[i]=="questionId"):
                    cursor.execute("SELECT * FROM reactions WHERE questionId = %s AND userId = %s",(res[j][i],userId))
                    reaction = cursor.fetchone()
                    #get the count of reactions
                    cursor.execute("SELECT COUNT(*) FROM REACTIONS WHERE questionId = %s",(res[j][i],))
                    reactionCount = cursor.fetchone()
                    row["reactionCount"] = reactionCount[0]
                    if(reaction):
                        row["isLiked"] = True
                    else:
                        row["isLiked"] = False
                row[column_names[i]] = res[j][i]
            result.append(row)    
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500


#followers
@forum.route('/followers',methods=['GET'])
@token_required
def followers(userId):
    try:
        cursor.execute("SELECT * FROM follows where followeeId = %s",(userId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row) 
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500



@forum.route('/followings',methods=['GET'])
@token_required
def following(userId):
    try:
        cursor.execute("SELECT * FROM follows where userId = %s",(userId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)    
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500



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
                if(column_names[i]=="userId"):
                    if(res[j][i]==userId):
                        continue
                    cursor.execute("SELECT * FROM follows WHERE userId = %s AND followeeId = %s",(userId,res[j][i]))
                    if(cursor.fetchone()):
                        row["isFollowing"] = True
                    else:
                        row["isFollowing"] = False
                row[column_names[i]] = res[j][i]
            result.append(row)
        row.pop('hashedPassword') 
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500


@forum.route('follow/<followeeId>',methods=['GET'])
@token_required
def follow(userId,followeeId):
    try:
        cursor.execute("INSERT INTO follows(userId,followeeId) VALUES(%s,%s)",(userId,followeeId))
        conn.commit()
        return jsonify({"message":"Followed successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),403

@forum.route('unfollow/<followeeId>',methods=['GET'])
@token_required
def unfollow(userId,followeeId):
    try:
        cursor.execute("DELETE FROM follows WHERE userId = %s AND followeeId = %s",(userId,followeeId))
        conn.commit()
        return jsonify({"message":"Unfollowed successfully"}),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500



#notificatios routes
@forum.route('/notifications',methods=['GET'])
@token_required
def notifications(userId):
    try:
        cursor.callproc('getNotifications',(userId,))
        queryResult = cursor.stored_results()
        res =None
        column_names  = None
        for i in queryResult:
            res = i.fetchall()
            column_names = [j[0] for j in i.description]
        result = []
        for k in range(len(res)):
          row = {}
          for i in range(len(column_names)):
            row[column_names[i]] = res[k][i]  
          result.append(row)
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500


#update user profile
@forum.route('/updateprofile',methods=['PUT'])
@token_required
def updateProfile(userId):
    try:
        data = request.get_json()
        cursor.execute("UPDATE users SET firstName = %s,lastName = %s,email = %s,phone = %s,dob = %s,gender = %s WHERE userId = %s",
        (data['firstName'],
        data['lastName'],
        data['email'],
        data['phone'],
        data['dob'],
        data["gender"],
        userId
        ))
        conn.commit()
        return jsonify({"message":"Profile updated successfully"}),200
    except Exception as err:
        return jsonify({"message":str(err)}),500



#backtest startegy
@forum.route('/backtest/<strategyId>',methods=['POST'])
@token_required
def backtest(userId,strategyId):
    # try:
        data = request.json
        csvDataFilePath = STRATEGIES_DATA_FILE_PATH+"\\"+strategyId+".csv"
        initialPortfolioValue = data['initialPortfolioValue']
        commission = data['commission']
        if commission == None:
            commission = 0.00055
        cerebro = bt.Cerebro()
        exec("from fs.strategies.py.s"+str(strategyId)+" import TestStrategy")
        exec("cerebro.addstrategy(TestStrategy)")
        custom_date_parser = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S+05:30")
        data = pd.read_csv(csvDataFilePath,index_col="TIMESTAMP",parse_dates=True,date_parser=custom_date_parser)
        feed = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(feed)
        cerebro.broker.setcash(initialPortfolioValue)
        cerebro.addsizer(bt.sizers.FixedSize, stake=30)
        cerebro.broker.setcommission(commission=commission)
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        res = {
            "finalPortfolioValue":cerebro.broker.getvalue(),
            "strategy":strategyId,
            "initialPortfolioValue":initialPortfolioValue,
        }
        return jsonify(res),200

    # except Exception as err:
    #     return jsonify({"message":str(err)}),400
    
    
    


#add strategy
@forum.route('/addstrategy',methods=['POST'])
@token_required
def addStrategy(userId):
    #get csv file and save it and save url in table
    csvFile = request.files.get('csv')
    strategyFile = request.files.get('py')
    
    jsonData  = request.values.get('json')
    data = json.loads(jsonData)
    if not strategyFile:
        return jsonify({"message":"No strategy file uploaded"}),400
    if not csvFile:
        return jsonify({"message":"No csv file uploaded"}),400
    strategyId = random.randint(1,1000000)
    strategyName = data["strategyName"]
    description = data["description"]
    try:
        csvFile.save(f"{STRATEGIES_DATA_FILE_PATH}/{strategyId}.csv")
        strategyFile.save(f"{STRATEGIES_PY_FILE_PATH}/s{strategyId}.py")
        strategyDataFileUrl = f"{BASE_STRATEGY_DATA_URL}/{strategyId}.csv"
        strategyScriptFileUrl = f"{BASE_STRATEGY_PY_URL}/{strategyId}.py"
        cursor.execute("INSERT INTO strategies(strategyId,strategyName,description,strategyDataFileUrl,strategyScriptFileUrl,userId) VALUES(%s,%s,%s,%s,%s,%s)",
        (strategyId,
        strategyName,
        description,
        strategyDataFileUrl,
        strategyScriptFileUrl,
        userId
        )
        )
        conn.commit()
        return jsonify({"message":"Strategy added successfully"}),200
    except Exception as err:
        return jsonify({"message":str(err)}),500



#get all strategies
@forum.route('/strategies',methods=['GET'])
@token_required
def getStrategies(userId):
    try:
        #join users and questions reactions
        cursor.execute("SELECT * FROM strategies ORDER BY createdAt DESC")
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                if(column_names[i]=="userId"):
                    cursor.execute("SELECT * FROM users WHERE userId = %s",(res[j][i],))
                    user = cursor.fetchone()
                    column_names_user = [l[0] for l in cursor.description]
                    userRow = {}
                    for k in range(len(column_names_user)):
                        userRow[column_names_user[k]] = user[k]
                    userRow.pop("hashedPassword")
                    row["postedBy"] = userRow

                row[column_names[i]] = res[j][i]
            row.pop("userId")
            result.append(row)
           
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),500


@forum.route('userInfo/<userInfoId>', methods=['GET'])
@token_required
def userInfo(userId, userInfoId):
    try:
        cursor.execute(
            'SELECT userId,firstName,lastName from users where userId=%s', (userInfoId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)
        print(res)
        return jsonify(result), 200
    except mysql.connector.Error as err:
        return jsonify({"message": str(err)}), 200


#add a route to display users profile
@forum.route('/user/<userId>',methods=['GET'])
@token_required
def getUser(userId):
    try:
        cursor.execute("SELECT * FROM users WHERE userId = %s",(userId,))
        res = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        result = []
        for j in range(len(res)):
            row = {}
            for i in range(len(column_names)):
                row[column_names[i]] = res[j][i]
            result.append(row)
        return jsonify(result),200
    except mysql.connector.Error as err:
        return jsonify({"message":str(err)}),200
