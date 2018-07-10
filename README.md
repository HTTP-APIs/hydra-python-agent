# python-hydra-agent

python-hydra-agent is a smart python hydra client which is working with [hydrus](https://github.com/HTTP-APIs/hydrus).

It caches the server data from hydra server for fast data querying.

It uses Redis to cache the data at the end of the client.

So, Data load from the server and store in Redis memory as a graph using redisgraph.

With the help of Redis, clients become faster and easier to query the data.

## Installation

**NOTE:** The client is using python3.

To install the client, you have to run the following commands:

     python3 setup.py install

or,

To install only requirements:
   
    pip3 install -r requirements.txt

For install Redis and start Redis server::

    cd hydra_redis
    ./redis_setup.sh

## Quickstart

### Demo

To run the demo of python-hydra-agent, you have to follow the instructions:

* Clone the repo:

        git clone https://github.com/HTTP-APIs/python-hydra-agent.git
    
* Change directory and switch to the develop branch:

        cd python-hydra-agent
        git checkout -b develop origin/develop

* Now for install the requirements and setup the environment:

    you should follow the instruction of [installation](#installation).

After setup environment and run the Redis server. You can query or run the client. 

* For run the client you should run querying_mechanism.py like:

        cd hydra_redis
        python3 querying_mechanism.py


    and provide a valid URL and then you can query in querying format.

        `>>>url` #here url should be valid link for testing you can use https://storage.googleapis.com/api3/api
        `>>>help` # it will provide the querying format

#### Code simplification

To create graph in Redis memory use(hydra_graph.py) :
```
    import redis
    from redisgraph import Graph, Node, Edge
    redis_con = redis.Redis(host='localhost', port=6379)
    self.redis_graph = Graph("apidoc", redis_con)
```

For querying, url should be provided first:

```
    url = input("url>>>")
    
    return query(apidoc, url) # apidoc is vocab file provided by url.
```

Query input be like:

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

you can query in various querying formats:

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


