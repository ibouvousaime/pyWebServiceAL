#!flask/bin/python
from flask import Flask, request, jsonify
import mysql.connector
import xmltodict
mydb = mysql.connector.connect(
  host="localhost",
  port=3306,
  user="newsite",
  password="passer",
  database="journal"
)
print(mydb)
app = Flask(__name__)
namespaces = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'a': 'http://www.etis.fskab.se/v1.0/ETISws',
}
userAttributes = ["id", "nom", "prenom", "login", "password","type"]

def getUsers(args={}):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM utilisateur")
    myresult = mycursor.fetchall()
    result = []
    print(myresult)
    for user in myresult:
        userInfo = {}
        index = 0
        for attr in user:
            userInfo[userAttributes[index]] = attr
            index += 1
        result.append(userInfo)
    return result;
def insertUser(args={}):
    mycursor = mydb.cursor()
    sql = "INSERT INTO utilisateur (nom, prenom, login, password,type) VALUES (%s, %s,%s, %s,%s)"
    val = (args[userAttributes[1]], args[userAttributes[2]],args[userAttributes[3]],\
        args[userAttributes[4]],args[userAttributes[5]])
    #print(val)
    mycursor.execute(sql, val)
    return mydb.commit()
def updateUser(args={}):
    mycursor = mydb.cursor()
    sql = "UPDATE utilisateur SET nom=%s,prenom=%s, login=%s, password=%s, type=%s WHERE id=%s;";
    val = (args[userAttributes[1]], args[userAttributes[2]],args[userAttributes[3]],\
        args[userAttributes[4]],args[userAttributes[5]],int(args[userAttributes[0]]))
    print("vals",val)
    mycursor.execute(sql, val)
    return mydb.commit()
soapFunctions = {
    "getUsers" : getUsers,
    "insertUser" : insertUser,
    "updateUser" : updateUser
}
@app.route('/soap', methods=['POST'])
def getSoap():
    dom = xmltodict.parse(request.data)
    bodyData = dom['soapenv:Envelope']['soapenv:Body']
    body = next(iter(bodyData))
    #print(bodyData[body])
    #for key in bodyData[body]:
        #print(key, bodyData[body][key])
    print(soapFunctions[body](bodyData[body]))
    return "test"


@app.route('/articles', methods=['GET', 'POST'])
def Users():
    if request.method == 'GET':
        return getUsers();
    elif request.method == 'POST':
        req_data = request.get_json()
        return insertUser(req_data);

if __name__ == '__main__':
    app.run(debug=True)