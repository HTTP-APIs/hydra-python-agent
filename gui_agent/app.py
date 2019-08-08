from flask import Flask, request, send_from_directory
from flask_cors import CORS
from hydra_agent.agent import Agent
import json, jsons, os
from requests import get

app = Flask(__name__, static_folder='console-frontend/build/')

#Setting CORS so it allows requests from our React app in localhost:3000
CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

# Remove to deploy
agent = Agent("http://localhost:8080/serverapi")

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Receive URL and start the Agent
@app.route("/start-agent", methods=['POST'])
def start_agent():    
    body = request.get_data()
    body = body.decode('utf8').replace("'", '"')
    body = json.loads(body)
    agent = Agent(body['url'])
    return "Server started successfully"

# Serve Hydra Doc
@app.route("/hydra-doc", methods=['GET'])
def hydra_doc():
    apidoc = agent.fetch_apidoc()
    return jsons.dump(apidoc)

# Send Command to Agent
@app.route("/send-command", methods=['POST'])
def send_command():
    return

if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)