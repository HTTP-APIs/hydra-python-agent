import redis
import hydra_graph as graph
from hydrus.hydraspec import doc_maker
import hydrus
from collections_endpoint import CollectionEndpoints
import urllib.request
import json

def final_file(url):
    """ Open the given url and read and load the Json data."""
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf-8'))

def split_data(count,objects):
    for obj in objects:
        string = obj.decode('utf-8')
        map_string = map(str.strip,string.split(','))
        property_list = list(map_string)
        check = property_list.pop()
        property_list.append(check.replace("\x00",""))
        print (property_list)

def endpoints_query(query):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    if query == "endpoint":
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc', "MATCH (p:classes) RETURN p") + \
                r.execute_command('GRAPH.QUERY',
                                  'apidoc', "MATCH (p:collection) RETURN p")
        count = 0

    if query == "classEndpoint":
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc','MATCH (p:classes)' 'RETURN p')
        count = 0

    if query == "collectionEndpoint":
#        reply = r.execute_command('GRAPH.QUERY','apidoc','RETURN ',query,'')
        reply  = r.execute_command('GRAPH.QUERY',
                                   'apidoc','MATCH (p:collection) RETURN p')
        count = 2

    for objects in reply:
        count+=1
        if count==1:
            print("\nclasses endpoint\n")
        if count==3:
            print("\ncollection endpoint\n")
        if count%2!=0:
            split_data(count,objects)
#    print (reply)

def operation_and_property_query(query):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    endpoint, query = query.split(" ")
#    print(endpoint)
    if "objects" in endpoint:
        endpoint = endpoint.replace("Collection","")
        id_ = endpoint
        print(id_,endpoint)
        endpoint = endpoint.replace("objects","")
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc','MATCH ( p:{} ) WHERE (p.type = "{}") RETURN p.{}'.format(id_,endpoint,query))
        print("objects")
        count = 0
    elif "object" in endpoint:
        index = endpoint.find("Collection")
        id_ = endpoint[5:index]
#        print (id_)
        endpoint = endpoint.replace("object","")
#        endpoint = "/api/" + endpoint
        print("object")
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc','MATCH ( p:{}) WHERE (p.parent_id = "{}") RETURN p.{}'.format(id_,endpoint,query))
        count = 0
    elif "Collection" in endpoint:
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc','MATCH ( p:collection ) WHERE (p.type="{}") RETURN p.{}'.format(endpoint,query))
        count = 2
        print("collection_endpoint")
    else:
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc','MATCH ( p:classes ) WHERE (p.type="{}") RETURN p.{}'.format(endpoint,query))
        count = 0
        print("class_endpoint")
    for objects in reply:
        count+=1
        if count%2!=0:
            split_data(count,objects)


def collection_endpoint_members(endpoint):
    collect = CollectionEndpoints(graph.redis_graph,graph.class_endpoints)
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    endpoint = endpoint.replace(" members","")
#    collect.load_from_server(endpoint,api_doc,url)
    query = "objects"+endpoint[:-10]
#    print(query)
    reply = r.execute_command('GRAPH.QUERY',
                              'apidoc','MATCH (p:{}) WHERE (p.type = "{}") RETURN p.id'.format(query,endpoint[:-10]))
#    print(reply)
    if len(reply[0])==1:
        collect.load_from_server(endpoint,api_doc,url)
        reply = r.execute_command('GRAPH.QUERY',
                                  'apidoc','MATCH (p:{}) WHERE (p.type = "{}") RETURN p.id'.format(query,endpoint[:-10]))
    count=2
    print("members")
    for objects in reply:
        count+=1
        if count%2!=0:
            split_data(count,objects)


#def compare_property(query):
#    endpoint_type, query1 = query.split(" ",1)
##    query = list(map(str.strip, query.split(' ')))
#    r = redis.StrictRedis(host='localhost', port=6379, db=0)
#    query = endpoint_type
#    endpoint_type = "objects" + endpoint_type
#    print(endpoint_type,query1)
#    reply = r.execute_command('GRAPH.QUERY',
#                              'apidoc','MATCH ( p:{} ) WHERE (p.type= "{}") RETURN p.property_value'.format(endpoint_type,query))
#    count = 0
#    for objects in reply:
#        count+=1
#        if count%2!=0:
#            for obj in objects:
#                string = obj.decode('utf-8')
#                print (string)
#                map_string = map(str.strip,string.split(','))
#                property_list = list(map_string)
#                check = property_list.pop()
#                property_list.append(check.replace("\x00",""))
#                for query1 in dict(property_list[0]):
#                    print(query1)
#                print (property_list[0])
#    print(reply)


def main():
    initialize= 0
    while(1):
        if initialize ==0:
            print("just initialize")
            global url
            url =input("url>>>")
            apidoc = final_file(url + "/vocab")
            global api_doc
            api_doc = doc_maker.create_doc(apidoc)
            graph.main(url,api_doc)
            initialize+=1
        elif initialize >0:
#            print("for query write your query in queryformat")
            print("for exit enter EXIT or write query in queryformat")
            query = input("query>>>")
            if query == "EXIT":
                break
            else:
                query = query.replace("show ","")
                if query=="endpoint" or query == "collectionEndpoint" or query == "classEndpoint":
                    endpoints_query(query)
                elif "members" in query:
                    collection_endpoint_members(query)
                elif "properties" in query or "operations" in query or "property_value" in query or "type" in query or "id" in query:
                    operation_and_property_query(query)
#                else:
#                    compare_property(query)


if __name__ =="__main__":
    print ("querying format")
    print ("for endpoint:- show endpoint")
    print ("for class_endpoint:- show classEndpoint")
    print ("for collection_endpoint:- show collectionEndpoint")
    print ("for members of collection_endpoint:-show <collection_endpoint> members")
    print ("for properties of any member:- show object<id_of_member> properties ")
    print ("for properties of objects:- show objects<endpoint> properties")
    print ("for collection or class properties:- show <collection_endpoint or class_endpoint> properties")
    main()
#    query = input()
#    query = query.replace("show ","")
#    operation_and_property_query(query)
##    endpoints_query(query)
#    class_endpoint_query("http://35.224.198.158:8080/api","classEndpoint")
