from typing import Union
from serialize import custom_jsonify
from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)

with open('vizinhos.json') as json_file:
    settings = json.load(json_file)
    myclient = MongoClient(settings['mongo_uri'])
    mydb = myclient[settings['database']]
    mycol = mydb["listingsAndReviews"]

@app.route("/")
def read_root():
    return jsonify(settings)

@app.route("/airbnbs/<int:id>")
def read_airbnbs(id):
    visited = request.args.get('visited')
    retorno = mycol.find_one({"_id": str(id)})
    if retorno:
        return custom_jsonify(retorno)
    else:
        neighbors = settings["vizinhos"]
        visitedNeighbors = visited.split(',') if visited else []
        visitedNeighbors.append(str(settings['id']))
        for neighbor in neighbors:
            if str(neighbor["id"]) not in visitedNeighbors:
                visitedNeighbors.append(str(neighbor["id"]))
                visitedAsString = ','.join(visitedNeighbors)
                try:
                    query = f"?visited={visitedAsString}" if len(visitedAsString) > 0 else ''
                    response = requests.get(f"http://localhost:{neighbor['port']}/airbnbs/{id}{query}").json()
                    print(response)
                except:
                    print("Server not found")
                if "_id" in response:
                    return response
        return {"error": "Airbnb not found"}

if __name__ == "__main__":
    app.run(port= 5004)