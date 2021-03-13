from flask import Flask,jsonify,  request, json
from flask_cors import CORS
import pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import json

app = Flask(__name__)

#Setup mongodb client to application
#Database available at MongoDB Atlas
myclient = pymongo.MongoClient("mongodb+srv://prasangika:prasangika1234@cluster0.n7wlp.mongodb.net/farmer_ranking?ssl=true&ssl_cert_reqs=CERT_NONE")
mydb = myclient["farmer_ranking"]

#Enable cross origin resource sharing
CORS(app)


#Error Handler
@app.errorhandler(404)
def not_found(error=None):
    #Create error message as JSON
    message = {
        'status': 404,
        'message': 'Not Found' + request.url
    }

    resp = jsonify(message)

    resp.status_code = 404 #Http Service Not found

    return resp


#Retrieve processed data from database
@app.route('/')
def send_data():
    # set database name
    collectionName = mydb['farmer_rankings_collection']
    # Find all records in considering collection and sorting records in descending order
    result = collectionName.find().sort('score', -1)
    # Create results as JSON
    resp = dumps(result)
    return resp


#Retrieve farmers' personal data from database
@app.route('/farmers')
def send_farmers():
    # set database name
    collectionName = mydb['farmers']
    #Find all farmers' personal data from farmers collection
    result = collectionName.find()
    # Create results as JSON
    resp = dumps(result)
    return resp


# create database for processed data
@app.route('/createRanking',  methods=['POST'])
def create_interview():
    #create request
    _json = request.json
    #get data
    _data = _json["data"]

    #set collection name
    collectionName = mydb["farmer_rankings_collection"]

    #check _data has expected values and http method is POST
    if _data and request.method == "POST":
        #Loop whole data set until last record
        for data in _data:
            #insert data set into database
            collectionName.insert_one(data)
        #success response
        resp = jsonify("Data Added Successfully")
        resp.status_code = 200
        return resp
    else:
        return not_found()


#Update candidate ranking score in database
@app.route('/updateScore/<id>/<score>', methods=['PUT'])
def update_candidate(id, score):
    # set collection name
    collectionName = mydb['farmer_rankings_collection']
    #update record if farmer index is matched with id
    collectionName.update_one({"index": id}, {"$set": {"score": float(score + ".0")}})
    #success response
    resp = jsonify("Details updated successfully")
    resp.status_code = 200
    return resp


#Create data object from processed data
def create_json():
    # Create empty list
    final_json = []

    #Read demand.json file and assign values to variable
    with open('./demand.json') as f:
        demand = json.load(f)
    # Read score.json file and assign values to variable
    with open('./score.json') as f:
        score = json.load(f)
    # Read supply.json file and assign values to variable
    with open('./supply.json') as f:
        supply = json.load(f)

    #create JSON object for each record
    for i in range(len(demand)):
        json_obj = {
            'index': "Farmer_" + str(i + 1),
            'score': score[str(i)] * 10,
            'demand': str(demand[str(i)]) + " KG" ,
            'supply': supply[str(i)]
        }
        #Add JSON object to previously created list
        final_json.append(json_obj)

    return final_json

#Run main method
if __name__ == '__main__':
    app.run(debug=True)
