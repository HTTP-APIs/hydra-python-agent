# python-hydra-agent

For a general introduction to Hydra Ecosystem, see [hydraecosystem.org](http://hydraecosystem.org).

`python-hydra-agent` is a smart Hydra client implemented in Python which works with [hydrus](https://github.com/HTTP-APIs/hydrus). Reference implementation is [Heracles.ts](https://github.com/HydraCG/Heracles.ts). Smart clients are generic automated clients that establish resilient connected data networks leveraging knowledge graphs.

## General characteristics

The client is designed to:
* Cache metadata from the Hydra server it connects to, to allow querying on the client-side;
* Use Redis as a graph-store leveraging `redisgraph` (see [here](https://oss.redislabs.com/redisgraph/));
* simply, metadata and data are loaded from the server and stored in Redis;
* The graph can be queried using OpenCypher.

The starting objective is to create a querying layer that is able to reach data in one or more Hydra srever/s. Leveraging Redis, clients can construct their own representation of the data stored in one or more Hydra servers; querying the data as they need it, and respond complex semantic queries. This will allow any client connected to any server to have access to an "aggregated view" of the connected network (the network of all the servers it connects to). 

## Missing bits at the moment
* For now it is a proof-of-concept, only `GET` functionality
* Soon to develop, a reliable synchronization mechanism to allow strong consistency between server-side data and client-side representation.

## Installation

**NOTE:** You'll need to use python3.

To install or setup the client environment, you have to run:

     python3 setup.py install

or,

To install only requirements:
   
    pip3 install -r requirements.txt

To install Redis and start Redis server:

    cd hydra_redis
    ./redis_setup.sh

## Quickstart

### Demo

To run the demo for python-hydra-agent, you have to follow the instructions:

* Clone the repo:

        git clone https://github.com/HTTP-APIs/python-hydra-agent.git
    
* Change directory and switch to the develop branch:

        cd python-hydra-agent
        git checkout -b develop origin/develop

* Now to install the requirements or setup the environment:

    you should follow the instructions of [installation](#installation).

After setup the environment and run the Redis server. You can query or run the client. 

* To run the client you should run querying_mechanism.py like:

        cd hydra_redis
        python3 querying_mechanism.py


    and provide a valid URL and then you can query in querying format.

        `>>>url` #here url should be a valid link, for testing you can use https://storage.googleapis.com/api3/api
        `>>>help` # it will provide the querying format

#### Code simplification

To create the graph in Redis memory, use(hydra_graph.py) :
```
    import redis
    from redisgraph import Graph, Node, Edge
    redis_con = redis.Redis(host='localhost', port=6379)
    self.redis_graph = Graph("apidoc", redis_con)
```

For querying, URL should be provided first:

```
    url = input("url>>>")
    
    return query(apidoc, url) # apidoc is vocab file provided by url.
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
    print("for endpoint:- show endpoint")
    print("for class_endpoint:- show classEndpoint")
    print("for collection_endpoint:- show collectionEndpoint")
    print("for members of collection_endpoint:-",
          "show <collection_endpoint> members")
    print("for properties of any member:-",
          "show object<id_of_member> properties ")
    print("for properties of objects:-show objects<endpoint_type> properties")
    print("for collection properties:-",
          "show <collection_endpoint> properties")
    print("for classes properties:- show class<class_endpoint> properties")
    print("for compare properties:-show <key> <value> and/or <key1> <value1>")
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

References
----------

[Hydra-Enabled smart client](http://www.hydra-cg.com/)

[Hydra core vocabulary](http://www.hydra-cg.com/spec/latest/core/)

