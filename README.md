# python-hydra-agent

The python-hydra-agent is a smart python hydra client which is working with [hydrus](https://github.com/HTTP-APIs/hydrus).

It caches the server data from hydra server for fast data querying.

It uses Redis to cache the data at the end of the client.

So, Data is loaded from the server and store in Redis memory as a graph using redisgraph.

With the help of Redis, clients become faster and easier to query the data.

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
    print("for using both opeartions(and,or) you should use brackets like:-",
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

