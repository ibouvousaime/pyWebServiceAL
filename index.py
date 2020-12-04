#!flask/bin/python
from flask import Flask, request, jsonify, Response
import mysql.connector
import xmltodict
import random
mydb = mysql.connector.connect(
  host="localhost",
  port=3306,
  user="newsite",
  password="passer",
  database="journal"
)
app = Flask(__name__)
namespaces = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'a': 'http://www.etis.fskab.se/v1.0/ETISws',
}
userAttributes = ["id", "nom", "prenom", "login", "password","type"]
alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
def veriferToken(token):
    mycursor = mydb.cursor()
    #print(args[userAttributes[2]], args[userAttributes[3]])
    mycursor.execute("SELECT * FROM tokens where token = '" + token +"'")
    myresult = mycursor.fetchall()
    return len(myresult) > 0

def inventerToken():
    result = ""
    for i in range(20):
        result += random.choice(alphabet)
    return result;
    
def getUsers(token, args={}):
    if not veriferToken(token):
        return Response("operation non permise", status=401)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM utilisateur")
    myresult = mycursor.fetchall()
    result = []
    #print(myresult)
    for user in myresult:
        userInfo = {}
        index = 0
        for attr in user:
            userInfo[userAttributes[index]] = attr
            index += 1
        result.append(userInfo)
    return {"user" : result};

def userLogin(token = "",args={}):
    mycursor = mydb.cursor()
    #print(args[userAttributes[2]], args[userAttributes[3]])
    mycursor.execute("SELECT * FROM utilisateur where login = %s and password = %s", (args[userAttributes[3]], args[userAttributes[4]]))
    myresult = mycursor.fetchall()
    if len(myresult) > 0 :
        sql = "INSERT INTO tokens (token, userID) VALUES (%s,%s)"
        vals = (inventerToken(), myresult[0][0])
        mycursor.execute(sql, vals) 
        return mydb.commit()
    else : 
        return len(myresult)

def insertUser(token,args={}):
    if not veriferToken(token):
        return Response("operation non permise", status=401)
    mycursor = mydb.cursor()
    sql = "INSERT INTO utilisateur (nom, prenom, login, password,type) VALUES (%s, %s,%s, %s,%s)"
    val = (args[userAttributes[1]], args[userAttributes[2]],args[userAttributes[3]],\
        args[userAttributes[4]],args[userAttributes[5]])
    #print(val)
    mycursor.execute(sql, val)
    return mydb.commit()
def updateUser(token,args={}):
    if not veriferToken(token):
        return Response("operation non permise", status=401)
    mycursor = mydb.cursor()
    sql = "UPDATE utilisateur SET nom=%s,prenom=%s, login=%s, password=%s, type=%s WHERE id=%s;";
    val = (args[userAttributes[1]], args[userAttributes[2]],args[userAttributes[3]],\
        args[userAttributes[4]],args[userAttributes[5]],int(args[userAttributes[0]]))
    #print("vals",val)
    mycursor.execute(sql, val)
    return mydb.commit()
    
soapFunctions = {
    "getUsers" : getUsers,
    "insertUser" : insertUser,
    "updateUser" : updateUser,
    "userLogin" : userLogin
}
@app.route('/soap', methods=['POST'])
def getSoap():
    dom = xmltodict.parse(request.data)
    headerData = dom['soapenv:Envelope']['soapenv:Header']
    #print(headerData)
    token = headerData['token']
    #print(token)
    bodyData = dom['soapenv:Envelope']['soapenv:Body']
    body = next(iter(bodyData))
    #print(bodyData[body])
    #for key in bodyData[body]:
        #print(key, bodyData[body][key])
    result = {"soapenv:Envelope":{"soapenv:Body":{"return" : soapFunctions[body](token,bodyData[body])}}}
    xmlResult=(xmltodict.unparse(result))
    print(xmlResult)
    return xmlResult


@app.route('/articles', methods=['GET', 'POST'])
def Users():
    if request.method == 'GET':
        return getUsers();
    elif request.method == 'POST':
        req_data = request.get_json()
        return insertUser(req_data);

if __name__ == '__main__':
    app.run(debug=True)