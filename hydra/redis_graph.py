import redis
from redisgraph import Graph,Node, Edge
from httplib2 import Http, HttpLib2ErrorWithResponse
from re import compile as regex
import urllib,json
"""
we have to give alias also with every node because node is like ({label}:{alias} {{{properties}}})
for no property of node we are using no_prop as dict and no know more about the id of node then try node.properties. 
"""
class _MemCache(dict):

    def __nonzero__(self):
        # even if empty, a _MemCache is True
        return True

    def set(self, key, value):
        self[key] = value

    def delete(self, key):
        if key in self:
            del self[key]

DEFAULT_HTTP_CLIENT = Http(_MemCache())
http = DEFAULT_HTTP_CLIENT


APIDOC_RE = regex(r'^<([^>]*)>; rel="http://www.w3.org/ns/hydra/core#apiDocumentation"$')
redis_con = redis.Redis(host='localhost', port=6379)
redis_graph = Graph("apidoc", redis_con)
no_prop = {"properties": "no property"}
null_node = Node(label="empty", properties=no_prop)
redis_graph.add_node(null_node)


"""
we can get APIdoc from url
url ="http://www.markus-lanthaler.com/hydra/event-api/"
url method is here

url ="http://www.markus-lanthaler.com/hydra/event-api/"
response = urllib.urlopen(url)
new_file = json.loads(response.read())

for now I am using url method
"""

def final_file(url):
    response = urllib.urlopen(url)
    new_file = json.loads(response.read())
    check_url(new_file,url)
    
def check_url(new_file,url):
    response,content = http.request(url,"GET")
    link = response.get('link')
    match = APIDOC_RE.match(link)
    api_doc = match.groups()[0]
    if api_doc != url:
        print url,"not match", api_doc
        new_url = api_doc
        return final_file(new_url)
    else:
        prop = {"vocabid1":url}
        print api_doc, "yes match",url
        print "now we have to create the graph for ",url
        node_url = Node(label="id1", properties={"id1":str(new_file["@id"])})
        redis_graph.add_node(node_url)
        get_type(new_file,node_url)
        return get_supp_class(node_url,"supportedclass",new_file["supportedClass"])
        
"""
Now we are putting the function for terminals or values
"""
def get_type(source_dict,source_node):
    predicate = "type"
    node = Node(label="id1_type", properties={"id1_type":str(source_dict["@type"])})
    redis_graph.add_node(node)
    edge = Edge(source_node,predicate,node)
    redis_graph.add_edge(edge)


    
"""
Now we are putting the functions for other dict or list type
"""
""" 
we have to access supported class 
"""
def get_supp_class(source_node,predicate,new_file):
    count =1
    for obj in new_file:
        idd = "id1_id" + str(count)
        count+=1
        node_supp_class_obj = Node(label = idd, properties ={idd:str(obj["@id"])})
        redis_graph.add_node(node_supp_class_obj)
        edge = Edge(source_node,predicate,node_supp_class_obj)
        redis_graph.add_edge(edge)
        
        get_supp_class_value(obj,node_supp_class_obj)
    print "Creating the graph"
    redis_graph.commit()
    print "yess done"

def get_supp_class_value(new_dict,source_node):
    for obj in new_dict:
        if obj !="@id":
            if type(new_dict[obj]) is not list and type(new_dict[obj]) is not dict:
                new_obj = ''.join(e for e in obj if e.isalnum())
                idd = source_node.label +"_"+ new_obj
                if new_dict[obj]:
                    s = (''.join(e for e in new_dict[obj] if e.isalnum())).lower()
                else: s=new_dict[obj]
                node = Node(label=idd, properties={str(idd):str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, new_obj, node)
                redis_graph.add_edge(edge)
                
            elif obj == "supportedOperation":
                if new_dict[obj]:
                    get_supp_oper(new_dict[obj],source_node)
                else:
                    edge = Edge(source_node, obj ,null_node)
                    redis_graph.add_edge(edge)
                    
            elif obj =="supportedProperty":
                if new_dict[obj]:
                    get_supp_prop(new_dict[obj],source_node)
                else:
                    edge = Edge(source_node,obj,null_node)
                    redis_graph.add_edge(edge)
                    
""" for supported operations"""                    
def get_supp_oper(new_file,source_node):
    predicate = "supportedoperation"
    count=1
    for obj in new_file:
        idd = source_node.label +"_id1"+ str(count)
        new_id = ''.join(e for e in obj["@id"] if e.isalnum())
        count+=1
        node_oper = Node(label=idd,properties ={idd:str(new_id)})
        redis_graph.add_node(node_oper)
        edge = Edge(source_node,predicate,node_oper)
        redis_graph.add_edge(edge)
        get_supp_oper_value(obj,node_oper)
        
def get_supp_oper_value(new_dict,source_node):
    for obj in new_dict:
        if obj != "@id":
            if type(new_dict[obj]) is not list and type(new_dict[obj]) is not dict:
                new_obj = ''.join(e for e in obj if e.isalnum())
                idd = source_node.label +"_"+ new_obj
                if new_dict[obj]:
                    s = (''.join(e for e in new_dict[obj] if e.isalnum())).lower()
                else: s=new_dict[obj]
                node = Node(label=idd, properties={str(idd):str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, new_obj, node)
                redis_graph.add_edge(edge)
                
            elif obj == "statusCodes":
                if new_dict[obj]:
                    get_status_code(new_dict[obj],source_node)
                else:
                    edge = Edge(source_node,obj,null_node)
                    redis_graph.add_edge(edge)

def get_status_code(new_file,source_node):
    predicate = "statuscodes"
    count = 1
    for obj in new_file:
        idd = source_node.label +"_id"+ str(count)
        count+=1
        new_id = str(obj["code"])
        node_status = Node(label =idd, properties={idd:new_id})
        redis_graph.add_node(node_status)
        edge = Edge(source_node,predicate,node_status)
        redis_graph.add_edge(edge)
        get_status_code_value(obj,node_status)
        
def get_status_code_value(new_dict,source_node):
    for obj in new_dict:
        if obj != "code":
            if type(new_dict[obj]) is not list and type(new_dict[obj]) is not dict:
                idd = source_node.label +"_"+ obj
                s=new_dict[obj]
                node = Node(label=idd, properties={str(idd):str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, obj, node)
                redis_graph.add_edge(edge)
               
""" for supported property"""
def get_supp_prop(new_file,source_node):
    predicate = "supportedproperty"
    count=1
    for obj in new_file:
        idd = source_node.label +"_id2"+ str(count)
        count+=1
        new_id = ''.join(e for e in obj["hydra:title"] if e.isalnum())
        node_prop = Node(label=idd, properties={str(idd):str(new_id)})
        redis_graph.add_node(node_prop)
        edge = Edge(source_node,predicate,node_prop)
        redis_graph.add_edge(edge)
        get_supp_prop_value(obj,node_prop)

def get_supp_prop_value(new_dict,source_node):
    for obj in new_dict:
        if obj != "hydra:title":
            if type(new_dict[obj]) is not list and type(new_dict[obj]) is not dict:
                new_obj = ''.join(e for e in obj if e.isalnum())
                idd = source_node.label +"_"+ new_obj
                if new_dict[obj] and type(new_dict[obj]) != type(True):
                    s = (''.join(e for e in new_dict[obj] if e.isalnum())).lower()
                else: s=new_dict[obj]
                node = Node(label=idd, properties={str(idd):str(s)})
                redis_graph.add_node(node)
                edge = Edge(source_node, new_obj, node)
                redis_graph.add_edge(edge)
            elif obj == "property" and type(new_dict[obj]) is dict:
                get_prop(new_dict[obj],source_node)
                
def get_prop(new_dict,source_node):
    predicate = "property"
    idd = source_node.label +"_"+ "property_id"
    s = (''.join(e for e in new_dict["@id"] if e.isalnum())).lower()
    node_prop_id = Node(label=idd,properties={str(idd):str(s)})
    redis_graph.add_node(node_prop_id)
    edge = Edge(source_node,predicate,node_prop_id)
    redis_graph.add_edge(edge)
    for obj in new_dict:
        if obj != "@id":
             if type(new_dict[obj]) is not list and type(new_dict[obj]) is not dict:
                new_obj = ''.join(e for e in obj if e.isalnum())
                idd = source_node.label +"_"+ new_obj
                if new_dict[obj] and type(new_dict[obj]) != type(True):
                    s = (''.join(e for e in new_dict[obj] if e.isalnum())).lower()
                else: s=new_dict[obj]
                node = Node(label=idd, properties={str(idd):str(s)})
                redis_graph.add_node(node)
                edge = Edge(node_prop_id,new_obj,node)
                redis_graph.add_edge(edge)
                
             elif obj == "supportedOperation":
                if new_dict[obj]:
                    get_supp_oper(new_dict[obj],node_prop_id)
                else:
                    edge = Edge(node_prop_id, obj ,null_node)
                    redis_graph.add_edge(edge)
                    

        

final_file("http://www.markus-lanthaler.com/hydra/event-api/")
