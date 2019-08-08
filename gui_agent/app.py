from flask import Flask, request
from hydra_agent.agent import Agent
import json
import jsons
from requests import get

app = Flask(__name__)

@app.route("/start-agent", methods=['POST'])
def start_agent():
    # Receive URL and start the Agent
    body = request.get_data()
    body = body.decode('utf8').replace("'", '"')
    body = json.loads(body)
    agent = Agent(body['url'])
    return "Server started successfully"
    
@app.route("/hydra-doc", methods=['GET'])
def hydra_doc():
    agent = Agent("http://localhost:8080/serverapi")
    print("rsssssss")
    apidoc = agent.fetch_apidoc()
    print( jsons.dump(apidoc))
    return jsons.dump(apidoc)
