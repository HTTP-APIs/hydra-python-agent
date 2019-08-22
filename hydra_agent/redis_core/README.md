#### CLT Code Basic explanation

To create the graph in Redis memory, use(graph_init.py) :
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

#### Querying Redis - Core Modules

While developing the Agent, it's necessary to constantly communicate with Redis. Below there are some instructions on how to query Redis/other specific info and formatting we've used.

Full Redis command reference can be found here: https://oss.redislabs.com/redisgraph/commands/

Entity structure: alias:label {filters}.

Example of MATCH:
(a:actor)-[:act]->(m:movie {title:"straight outta compton"})

GRAPH.QUERY apigraph "MATCH (p) RETURN p" 

Internal Hydra Python Agent naming:

Labels:

- collection, classes - macro labels
- objects<ObjectType> - for members
- object<ObjectID> - for resources

Aliases:

Alias for collection example:
<ObjectType>Collection
DroneCollection

Alias for collection member:
<ObjectType><ObjectID>
Dronea9d6f083-79dc-48e2-9e4b-fd5e9fc849ab

To get all nodes from the Graph:
```
GRAPH.QUERY apigraph "MATCH (p) RETURN p" 
```

Get all nodes and filter by label:
```
GRAPH.QUERY apigraph "MATCH (p:collection) RETURN p" 
```

Get all nodes and filter by label:
```'
GRAPH.QUERY apigraph "MATCH (p) WHERE(p.id = '/serverapi/DroneCollection/72b53615-a480-4920-b126-4d1e1e107dc6') RETURN p" 
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

To delete a node:
```
GRAPH.QUERY apigraph "MATCH (p) WHERE (p.id = '/serverapi/DroneCollection/2') DELETE p"

```

References
----------

[Hydra-Enabled smart client](http://www.hydra-cg.com/)

[Hydra core vocabulary](http://www.hydra-cg.com/spec/latest/core/)


