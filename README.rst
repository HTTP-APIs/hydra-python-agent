python-hydra-agent
==================

A fork of hydra-py [4]_. The license of the original fork is LGPLv3.


The primary goal is to provide a lib for easily writing Hydra-enabled clients [1]_.

A secondary goal is to provide a client for Triple Patterns Fragments [2]_,
and an RDFlib [3]_ Store backed on any TPF service.

Using Redis to cache the data at the end of client.

So, Data load from the server and store in Redis memory as a graph.

With the help of Redis, clients becomes faster and easier to query the data.

Installation
++++++++++++

To install this library, from the projet directory, type::

    pip install .

or

    python3 setup.py install

NB: developers might want to add the ``-e`` option to the command line above,
so that modifications to the source are automatically taken into account.

For install redis and start redis-server::

    cd hydra_redis
    ./redis_setup.sh

Quick start
+++++++++++

For hydra.__init__.py
---------------------
 
To create a Hydra-enabled resource, use:

.. code:: python

    from hydra import Resource, SCHEMA
    res = Resource.from_iri(the_iri_of_the_resource)

If the resource has an API documentation associated with it,
it will be available as an attribute.
The API documentation provides access to the supported class,
their supported properties and operations.

.. code:: python

    print("Api documentation:")
    for supcls in res.api_documentation.supported_classes:
        print("  %s" % supcls.identifier)
        for supop in supcls.supported_operations:
            print("    %s" % supop.identifier)

Alternatively,
you can query the resource directly for available operations.
For example, the following searches for a suitable operation for creating a new event,
and performs it.

.. code:: python

    create_event = res.find_suitable_operation(SCHEMA.AddAction, SCHEMA.Event)
    resp, body = create_event({
        "@context": "http://schema.org/",
        "@type": "http://schema.org/Event",
        "name": "Halloween",
        "description": "This is halloween, this is halloween",
        "startDate": "2015-10-31T00:00:00Z",
        "endDate": "2015-10-31T23:59:59Z",
    })
    assert resp.status == 201, "%s %s" % (resp.status, resp.reason)
    new_event = Resource.from_iri(resp['location'])

And you can go on with the new event you just created...

Triple Pattern Fragments
++++++++++++++++++++++++

The ``hydra.tpf`` module implements of Triple Pattern Fragments specification [2]_.
In particular, it provides an implementation of Store,
so that TPF services can be used transparently:

.. code:: python

    import hydra.tpf # ensures that the TPFStore plugin is registered
    from rdflib import Graph

    g = Graph('TPFStore')
    g.open('http://data.linkeddatafragments.org/dbpedia2014')

    results = g.query("SELECT DISTINCT ?cls { [ a ?cls ] } LIMIT 10")

Note however that this is experimental at the moment...


For hydra_redis
---------------

For running the client you should run querying_mechanism

    cd hydra_redis

    python3 querying_mechanism.py

and provide a valid url and then you can query in querying format.

    >>>help # it will provide the querying format

Code simplification
^^^^^^^^^^^^^^^^^^^
To create graph in Redis memory use:

.. code:: python

    import redis
    from redisgraph import Graph, Node, Edge
    redis_con = redis.Redis(host='localhost', port=6379)
    self.redis_graph = Graph("apidoc", redis_con)


For querying, url should be provided first:

.. code:: python

    url = input("url>>>")
    
    return query(apidoc, url) # apidoc is vocab file provided by url.

.. code:: python

    while True:
        print("press exit to quit")
        query = input(">>>")
        if query == "exit":
            break
        elif query == "help":
            help() # provide querying format
        else:
            print(facades.user_query(query))# query can be done with facades class


you can query in various formats:

.. code:: python

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


Query can be done like this:

.. code:: python

    check_data = [['p.id', 'p.operations', 'p.properties', 'p.type'],
                      ['vocab:EntryPoint/Location', 
                       "['POST'", "'PUT'", "'GET']", 
                       "['Location']", 'Location']]
    query = "show classEndpoints"
    self.assertEqual(data,check_data) #data is data retrieve from the Redis.

For more detail take a look at [wiki file](https://github.com/HTTP-APIs/http-apis.github.io/blob/master/hydra-agent-redis-graph.md)

References
++++++++++

.. [1] http://www.hydra-cg.com/
.. [2] http://www.hydra-cg.com/spec/latest/triple-pattern-fragments/
.. [3] https://rdflib.readthedocs.org/
.. [4] https://github.com/pchampin/hydra-py

