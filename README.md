# hydra-python-agent [![Build Status](https://travis-ci.com/HTTP-APIs/hydra-python-agent.svg?branch=master)](https://travis-ci.com/HTTP-APIs/hydra-python-agent)

For a general introduction to Hydra Ecosystem, see [hydraecosystem.org](http://hydraecosystem.org).

`hydra-python-agent` is a smart Hydra client implemented in Python which works with [hydrus](https://github.com/HTTP-APIs/hydrus). Reference implementation is [Heracles.ts](https://github.com/HydraCG/Heracles.ts). Smart clients are generic automated clients that establish resilient connected data networks leveraging knowledge graphs.

## General characteristics

The client is designed to:
* Cache metadata from the Hydra server it connects to, to allow querying on the client-side;
* Use Redis as a graph-store leveraging `redisgraph` (see [here](https://oss.redislabs.com/redisgraph/));
* simply, metadata and data are loaded from the server and stored in Redis;
* The graph can be queried using OpenCypher.

The starting objective is to create a querying layer that is able to reach data in one or more Hydra srever/s. Leveraging Redis, clients can construct their own representation of the data stored in one or more Hydra servers; querying the data as they need it, and respond complex semantic queries. This will allow any client connected to any server to have access to an "aggregated view" of the connected network (the network of all the servers it connects to). 

## Missing bits at the moment
* For now it is a proof-of-concept, only `GET` functionality
* Soon to develop, a reliable synchronization mechanism to allow strong consistency between server-side data and client-side representation ([#98](https://github.com/HTTP-APIs/hydra-python-agent/issues/98)).
* Allow users to interact with the server using Natural Language which is a processed machine consumable language. **(under development)**

## Installation

**NOTE:** You'll need to use python3.

To install only requirements:
   
    pip3 install -r requirements.txt

or,

To install or setup the client environment, you have to run:

     python3 setup.py install


To install Redis and other Redis modules:

    ./redis_setup.sh

## Quickstart

### Demo

To run the demo for hydra-python-agent, you have to follow the instructions:

* Clone the repo:

        git clone https://github.com/HTTP-APIs/hydra-python-agent.git
    
* Change directory and switch to the develop branch:

        cd hydra-python-agent
        git checkout -b develop origin/develop

* Now to install the requirements or setup the environment:

    you should follow the instructions of [installation](#installation).

After setup the environment. You can query or run the client.

* To run both the things Redis server and the client. You can run the command:
    
        docker-compose run client


    and provide a valid URL and then you can query in querying format.

        `>>>url` #here url should be a valid link, for testing you can use http://35.224.198.158:8080/api
        `>>>help` # it will provide the querying format

**Obs.: If failing to connect to localhost** running the Agent via Docker, head to [issue #104](https://github.com/HTTP-APIs/hydra-python-agent/issues/104#issuecomment-497381440).

#### Code simplification

To create the graph in Redis memory, use(hydra_graph.py) :
```
    import redis
    from redisgraph import Graph, Node, Edge
    redis_con = redis.Redis(host='localhost', port=6379)
    self.redis_graph = Graph("apigraph", redis_con)
```

For querying, URL should be provided first:

```
    url = input("url>>>")
    
    return query(apigraph, url) # apigraph is vocab file provided by url.
```

The client takes the query as input, like:

```
    while True:
        print("press exit to quit")
        query = input(">>>")
        if query == "exit":
            break
        elif query == "help":
            help() # provide querying format
        else:
            print(facades.user_query(query))# query can be done with facades class
```

you can query as following querying formats:

```
    print("querying format")
    print("Get all endpoints:- show endpoints")
    print("Get all class_endpoints:- show classEndpoints")
    print("Get all collection_endpoints:- show collectionEndpoints")
    print("Get all members of collection_endpoint:-",
          "show <collection_endpoint> members")
    print("Get all properties of objects:-",
          "show objects<endpoint_type> properties")
    print("Get all properties of any member:-",
          "show object<id_of_member> properties ")
    print("Get all classes properties:-show class<class_endpoint> properties")
    print("Get data with compare properties:-",
          "show <key> <value> and/or <key1> <value1>")
    print("Get data by using both opeartions(and,or)",
          " you should use brackets like:-",
          "show model xyz and (name Drone1 or name Drone2)",
          "or, show <key> <value> and (<key> <value> or <key> <value>)")

```

Query test can be done like this:

```
    check_data = [['p.id', 'p.operations', 'p.properties', 'p.type'],
                      ['vocab:EntryPoint/Location', 
                       "['POST'", "'PUT'", "'GET']", 
                       "['Location']", 'Location']]
    query = "show classEndpoints"
    self.assertEqual(data,check_data) #data is data retrieve from the Redis.
```

For more detail take a look at [wiki file](https://github.com/HTTP-APIs/http-apis.github.io/blob/master/hydra-agent-redis-graph.md)

#### Agent package 
To use the Agent as a package you can simply do something like:

```
from hydra_agent.agent import Agent 

agent = Agent("http://localhost:8080/serverapi")
agent.get("http://localhost:8080/serverapi/DroneCollection/123-123-123-123")
```

The agent supports GET, PUT, POST or DELETE:

- GET - used to READ resources or collections
- PUT - used to CREATE new resources in the Server
- POST - used to UPDATE resources in the Server
- DELETE - used to DELETE resources in the Server

To GET a existing resource you should:
```
agent.get("http://localhost:8080/serverapi/<CollectionType>/<Resource-ID>")
agent.get("http://localhost:8080/serverapi/<CollectionType>/")
```

To PUT a new resource you should:
```
new_resource = {"@type": "Drone", "name": "Drone 1", "model": "Model S", ...}
agent.put("http://localhost:8080/serverapi/<CollectionType>/", new_resource)
```

To UPDATE a resource you should:
```
existing_resource["name"] = "Updated Name"
agent.post("http://localhost:8080/serverapi/<CollectionType>/<Resource-ID>", existing_resource)
```

To DELETE a resource you should:
```
agent.delete("http://localhost:8080/serverapi/<CollectionType>/<Resource-ID>")
```

More than that, Agent extends Session from https://2.python-requests.org/en/master/api/#request-sessions, so all methods like auth, cookies, headers and so on can also be used.

#### Querying Redis
Reference can be found here: https://oss.redislabs.com/redisgraph/commands/

Entity structure: alias:label {filters}.

Example of MATCH:
(a:actor)-[:act]->(m:movie {title:"straight outta compton"})

GRAPH.QUERY apigraph "MATCH (p) RETURN p" 

Internal Hydra Python Agent naming:

labels:

- collection, classes - 
- objectsDrone - for members

alias:

DroneCollection - alias for collection example
Dronea9d6f083-79dc-48e2-9e4b-fd5e9fc849ab - alias for collection member

To get all nodes from the Graph:
```
GRAPH.QUERY apigraph "MATCH (p) RETURN p" 
```

Get all nodes and filter by label:
```
GRAPH.QUERY apigraph "MATCH (p:collection) RETURN p" 
```

To read all the edges of the graph
```
GRAPH.QUERY apigraph "MATCH ()-[r]->() RETURN type(r)"
```

To read all the edges connected to a node
```
GRAPH.QUERY apigraph "MATCH (p)-[r]->() WHERE p.type = 'DroneCollection' RETURN type(r)"
```

Creating Edges between existing Nodes(Ref: https://github.com/RedisGraph/redisgraph-py/issues/16):
*This is not available yet on the oficial doc*
```
MATCH (f:%s{%s:'%s'}), (t:%s{%s:'%s'}) CREATE (f)-[:in]->(t)
GRAPH.QUERY apigraph "MATCH (s:collection {type:'DroneCollection'} ), (d:objectsDrone {id:'/serverapi/DroneCollection/ea7e438e-a93d-436d-a7e9-994c13d49dc0'} ) CREATE (s)-[:has_Drone]->(d)"
```

To create a node:
```
GRAPH.QUERY apigraph "CREATE (Droneea7e438e-a93d-436d-a7e9-994c13d49dc0:objectsDrone {@id: '/serverapi/DroneCollection/a9d6f083-79dc-48e2-9e4b-fd5e9fc849ab', @type: 'Drone', model: 'Ultra Model S')"

```

References
----------

[Hydra-Enabled smart client](http://www.hydra-cg.com/)

[Hydra core vocabulary](http://www.hydra-cg.com/spec/latest/core/)

