# hydra-python-agent [![Build Status](https://travis-ci.com/HTTP-APIs/hydra-python-agent.svg?branch=master)](https://travis-ci.com/HTTP-APIs/hydra-python-agent)

For a general introduction to Hydra Ecosystem, see [hydraecosystem.org](http://hydraecosystem.org).

`hydra-python-agent` is a smart Hydra client implemented in Python which works with [hydrus](https://github.com/HTTP-APIs/hydrus). Reference implementation is [Heracles.ts](https://github.com/HydraCG/Heracles.ts). Smart clients are generic automated clients that establish resilient connected data networks leveraging knowledge graphs.

## Quick Start
Our Hydra Agent has different interfaces that you can try:

- [A Web-based GUI](https://github.com/HTTP-APIs/hydra-python-agent-gui/tree/agent-gui-1.0/console-frontend) - which shows how Hydra APIs are connected and how the Smart Agent is generic and can automatically build requests.  
- [A Python package](https://github.com/HTTP-APIs/hydra-python-agent/#user-content-agent-package) - so you can use to communicate with a Hydra API in your code/software. 
- [Natural-language-like command line tool](#natural-language-like-command-line-tool) - this is still a GET only implementation

## General characteristics

The Agent is *designed* to:
* Provide a seamless Client that can be used to communicate with Hydra APIs
* Cache metadata from the Hydra server it connects to, to allow querying on the client-side
* Maintain a syncrhonization mechanism which makes sure cached resources are consistent
* The graph can be queried using OpenCypher.

The final goal is to create a Client that can connected to multiple hydrus servers and operate between them while caching information in a graph-based database(Redis). This should enable the client to have an "aggregated view" of the connected network (the network of all the servers it connects to) and make complex sematic queries to it.

## Installation

**NOTE:** You'll need to use python3. Using venv(virtual environment) is recommended.

Clone and setup a virtual environment:
   
    git clone https://github.com/HTTP-APIs/hydra-python-agent.git
    cd hydra-python-agent
    python3 -m venv venv
    source venv/bin/activate

Install dependencies and setup Agent:

    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    python3 setup.py install

Setup Redis which is used as caching layer(if permission denied use `sudo`):

    ./redis_setup.sh

**Setup hydrus**
Since this is an API Client, we need an appropriate Hydra Server to query to. To setup a localhost follow the instructions at https://github.com/HTTP-APIs/hydrus#demo. You might want to run `hydrus serve --no-auth` to skip setting up headers.

#### Agent package 
After installing the Agent and running Redis, [as per instructions above](https://github.com/HTTP-APIs/hydra-python-agent/#user-content-installation), you can do something like:

```
from hydra_agent.agent import Agent 

agent = Agent("http://localhost:8080/serverapi/") # <- hydrus Server URL 
agent.get("http://localhost:8080/serverapi/DroneCollection/")
```

The agent supports GET, PUT, POST or DELETE:

- **GET** - used to READ resources or collections
- **PUT** - used to CREATE new resources in the Server
- **POST** - used to UPDATE resources in the Server
- **DELETE** - used to DELETE resources in the Server

**To GET** a existing resource you should:
```
agent.get("http://localhost:8080/serverapi/<ResourceType>/<Resource-ID>")
agent.get("http://localhost:8080/serverapi/<CollectionType>/")
agent.get("http://localhost:8080/serverapi/<CollectionType>/<Collection-ID>")
```

**To PUT** a new resource say on a Drone endpoint, you should:
```
new_resource = {
    "@type": "Drone",
    "DroneState": {
        "@type": "State",
        "Battery": "50%",
        "Direction": "N",
        "Position": "50.34",
        "SensorStatus": "Active",
        "Speed": "100"
    },
    "MaxSpeed": "500",
    "Sensor": "Active",
    "model": "Drone_1",
    "name": "Drone1"
}
agent.put("http://localhost:8080/serverapi/Drone/", new_resource)
```

**To UPDATE** a resource you should:
```
existing_resource["name"] = "Updated Name"
agent.post("http://localhost:8080/serverapi/<ResourceType>/<Resource-ID>", existing_resource)
```

**To DELETE** a resource you should:
```
agent.delete("http://localhost:8080/serverapi/<ResourceType>/<Resource-ID>")
```
**To ADD** members in collection:
```
request_body = {
    "@type": "<CollectionType>",
    "members": [
        {
            "@id": "<ResourceID>",
            "@type": "<ResourceType>"
        },
        {
            "@id": "<ResourceID>",
            "@type": "<ResourceType>"
        },
    ]
}
agent.put("http://localhost:8080/serverapi/<CollectionType>", request_body)
```
NOTE: \<ResourceType\> can be different in given request body. 

**TO GET** members of specific Collection:
```
agent.get("http://localhost:8080/serverapi/<CollectionType>/<CollectionID>")
```
**TO UPDATE** members of specific collection:
```
updated_collection = {
    "@type": "<CollectionType>",
    "members": [
        {
            "@id": "<ResourceID>",
            "@type": "<ResourceType>"
        },
        {
            "@id": "<ResourceID>",
            "@type": "<ResourceType>"
        },
    ]
}
agent.post("http://localhost:8080/serverapi/<CollectionType>/<CollectionID>",updated_collection )
```
**TO DELETE** members of specific Collection:
```
agent.delete("http://localhost:8080/serverapi/<CollectionType>/<CollectionID>")
```
More than that, Agent extends Session from https://2.python-requests.org/en/master/api/#request-sessions, so all methods like auth, cookies, headers and so on can also be used.

### Natural-language-like Command Line Tool
If you've followed the [installation](#installation) instructions you can run: 

    python hydra_agent/querying_mechanism.py

Another alternative to run the CLT is using docker componse. To run **both Redis server and the client**(stop any Redis instance before), you can run the command:
    
        docker-compose run client

To query you should provide a hydrus URL first:

```
     url>>> http://localhost:8080/serverapi/ 
   
```

**Obs.: If failing to connect to localhost** running the Agent via Docker, head to [issue #104](https://github.com/HTTP-APIs/hydra-python-agent/issues/104#issuecomment-497381440).

- **Natural Language querying format**

Run help inside the CLT to get the querying format.

        >>>help # it will provide the querying format

You can query the server with the following format:


> Get all endpoints:- **show endpoints**
Get all class_endpoints:- **show classEndpoints**
Get all collection_endpoints:- **show collectionEndpoints**
Get all members of collection_endpoint:- **show < collection_endpoint > members**
Get all properties of objects:- **show objects< endpoint_type > properties**
Get all properties of any member:- **show object< id_of_member > properties **
Get all classes properties:- **show class< class_endpoint > properties**
Get data with compare properties:- **show < key > < value > and/or < key1 > < value1 >**
Get data by using both opeartions(and,or)  you should use brackets like:- **show model xyz and (name Drone1 or name Drone2) or, show < key > < value > and (< key > < value > or < key > < value >)**

For more detail take a look at [wiki file](https://github.com/HTTP-APIs/http-apis.github.io/blob/master/hydra-agent-redis-graph.md)

### Missing bits at the moment
* For the Web GUI there's a list of [future enhacements here](https://github.com/HTTP-APIs/hydra-python-agent-gui/issues/3).
* For now the Natural language CLT it is a proof-of-concept, only `GET` functionality

References
----------

[Hydra-Enabled smart client](http://www.hydra-cg.com/)

[Hydra core vocabulary](http://www.hydra-cg.com/spec/latest/core/)

