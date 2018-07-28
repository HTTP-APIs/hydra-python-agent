# python-hydra-agent

The python-hydra-agent is a smart python hydra client which is working with [hydrus](https://github.com/HTTP-APIs/hydrus).

It caches the server data from hydra server for fast data querying.

It uses Redis to cache the data at the end of the client.

So, Data is loaded from the server and store in Redis memory as a graph using redisgraph.

With the help of Redis, clients become faster and easier to query the data.

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

To run the demo for python-hydra-agent, you have to follow the instructions:

* Clone the repo:

        git clone https://github.com/HTTP-APIs/python-hydra-agent.git
    
* Change directory and switch to the develop branch:

        cd python-hydra-agent
        git checkout -b develop origin/develop

* Now to install the requirements or setup the environment:

    you should follow the instructions of [installation](#installation).

After setup the environment. You can query or run the client.

* To run both the things Redis server and the client. You can run the command:
    
        docker-compose run client


    and provide a valid URL and then you can query in querying format.

        `>>>url` #here url should be a valid link, for testing you can use http://35.224.198.158:8080/api
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

References
----------

[Hydra-Enabled smart client](http://www.hydra-cg.com/)

[Hydra core vocabulary](http://www.hydra-cg.com/spec/latest/core/)

