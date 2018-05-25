import redis
from redisgraph import Graph, Node, Edge

redis_con = redis.Redis(host='localhost', port=6379)
redis_graph = Graph("apidoc", redis_con)

"""
defining function for fetch API structure and store it in graph
"""
# assumption that in "obj" we have the API structure which is fetch or
# parse from the hydrus/apidoc for id_=id


def apidocumentation():

    # create node
    apidoc_node = Node(
        label="node",
        alias="apidocumentation",
        properties={
            "prop": "apidocumentation_id"})
    redis_graph.add_node(apidoc_node)

    title = 'obj_title'
    # put method for title
    # get method for title
    node = Node(label="node", alias="title", properties={"prop": str(title)})
    redis_graph.add_node(node)
    create_graph(apidoc_node, node, "has_title")

    description = 'obj_description'
    # put method for description
    # get method for description
    node1 = Node(
        label="node",
        alias="description",
        properties={
            "prop": str(description)})
    redis_graph.add_node(node1)
    create_graph(apidoc_node, node1, "has_description")

    supportedclasses = 'obj_supportedClasses'
    # put function for add whole classes in it
    # get method for return the property of it.
    # class supported_class: which would have both the functions
    prop ="It will contain the displayname for evry class in supportedclasses"
    supportedclass_node = Node(
        label="node",
        alias="supportedClasses",
        properties={
            "prop": prop})
    redis_graph.add_node(supportedclass_node)
    create_graph(apidoc_node, supportedclass_node, "has_supportedclasses")

    entrypoint = 'obj_entrypoint'
    # put method for entrypoint
    # get method for entrypoint
    node2 = Node(
        label="node",
        alias="entrypoint",
        properties={
            "prop": str(entrypoint)})
    redis_graph.add_node(node2)
    create_graph(apidoc_node, node2, "has_entrypoint")

    supported_classes(supportedclass_node)


def supported_classes(supportedclass_node):
    # we use here iterable method because supportedClasses have a list of
    # objects itself

    display_name = 'iterable(obj_supportedClasses_displayname_or_title)'
    # put method for add display name.
    # similary we use get method.
    node = Node(
        label="node",
        alias="display_name",
        properties={
            "prop": str(display_name)})
    redis_graph.add_node(node)
    create_graph(supportedclass_node, node, "has_displayname")

    description = 'iterable(obj_supportedClasses_description)'
    # put method for add description
    # get method for return description
    node1 = Node(
        label="node",
        alias="description",
        properties={
            "prop": str(description)})
    redis_graph.add_node(node1)
    create_graph(node, node1, "has_description")

    supportedoperation = 'iterable(obj_supportedclasses_supportedOperation)'
    # put method for add the supported operation
    # get method to return the supported operation
    prop = "it contains the title of all objects of supportes operations"
    supportedoper_node = Node(
        label="node",
        alias="supportedoperation",
        properties={
            "prop": prop})
    redis_graph.add_node(supportedoper_node)
    create_graph(node, supportedoper_node, "has_supportedoperations")

    supported_operations(supportedoper_node)

    supportedproperty = 'iterable(obj_supportedclasses_supportedProperties)'
    # put method for add the supported propety
    # get method to return the supported property
    prop = "it contains the title of every object of the supported property"
    supportedprop_node = Node(
        label="node",
        alias="supportedproperty",
        properties={
            "prop": prop})
    redis_graph.add_node(supportedprop_node)
    create_graph(node, supportedprop_node, "has_supportedproperty")

    supported_property(supportedprop_node)


def supported_operations(supportedoper_node):

    title = 'obj_supportedclasses_supportedOperation_method'
    # put and get methods for opeartions title
    node = Node(
        label="node",
        alias="operation_title",
        properties={
            "prop": str(title)})
    redis_graph.add_node(node)
    create_graph(supportedoper_node, node, "has_title")

    method = 'obj_supportedclasses_supportedOperation_method'
    # put and get methods for method
    node1 = Node(
        label="node",
        alias="operation_method",
        properties={
            "prop": str(method)})
    redis_graph.add_node(node1)
    create_graph(node, node1, "has_method")

    expect_class = 'obj_supportedclasses_supportedOperation_expects'
    # put and get methods for expects
    node2 = Node(
        label="node",
        alias="operation_expects",
        properties={
            "prop": str(expect_class)})
    redis_graph.add_node(node2)
    create_graph(node, node2, "has_expectclass")

    returned_class = 'obj_supportedclasses_supportedOperation_returns'
    # put and get method for returns
    node3 = Node(
        label="node",
        alias="operation_returns",
        properties={
            "prop": str(returned_class)})
    redis_graph.add_node(node3)
    create_graph(node, node3, "has_returns")

    possible_status = 'obj_supportedclasses_supportedOperation_possibleStatus'
    status_node = Node(
        label="node",
        alias="posiblestatus",
        properties={
            "prop": possible_status})
    redis_graph.add_node(status_node)
    create_graph(node, status_node, "has_status")
    # put and get method for possible status in class possible_status:

    possibleStatus(status_node)


def supported_property(supportedprop_node):

    title = 'obj_supportedclasses_supportedProperty_title'
    # put and get method for supp_prop title
    node = Node(
        label="node",
        alias="property_title",
        properties={
            "prop": title})
    redis_graph.add_node(node)
    create_graph(supportedprop_node, node, "has_title")

    properties = 'obj_supportedclasses_supportedProperty_property'
    # put and get method for properties class Property
    property_links = "all links of property"
    property_node = Node(
        label="node",
        alias="property",
        properties={
            "prop": property_links})
    redis_graph.add_node(property_node)
    create_graph(node, property_node, "has_property")

    Property(property_node)

    required = 'obj_supportedclasses_supportedProperty_requires'
    # put and get method for reuires
    node2 = Node(label="node", alias="requires", properties={"prop": required})
    redis_graph.add_node(node2)
    create_graph(node, node2, "has_requires")

    readonly = 'obj_supportedclasses_supportedProperty_readonly'
    # put and get method for readonly
    node3 = Node(
        label="node",
        alias="readonly",
        properties={
            "prop": str(readonly)})
    redis_graph.add_node(node3)
    create_graph(node, node3, "is_readonly")

    writeonly = 'obj_supportedclasses_supportedProperty_writeonly'
    # put and get method for writeonly
    node3 = Node(
        label="node",
        alias="writeonly",
        properties={
            "prop": str(writeonly)})
    redis_graph.add_node(node3)
    create_graph(node, node3, "is_writeonly")


def possibleStatus(status_node):

    status_code="obj_supportedclasses_supportedOperation_possiblestatus_statusCode"
    # put and get method
    node = Node(
        label="node",
        alias="status_code",
        properties={
            "prop": str(status_code)})
    redis_graph.add_node(node)
    create_graph(status_node, node, "has_status")


def Property(property_node):

    link = 'obj_supportedclasses_supportedProperty_property_Links'
    # put and get method for links
    node = Node(label="node", alias="property_link", properties={"prop": link})
    redis_graph.add_node(node)
    create_graph(property_node, node, "has_links")

    supportedoperation = 'obj_supportedclasses_supportedProperty_property_supportedoperation'
    node1 = Node(
        label="node",
        alias="supportedoperation",
        properties={
            "prop": supportedoperation})
    redis_graph.add_node(node1)
    create_graph(node, node1, "has_supportedoperation")


def create_graph(source_node, dest_node, predicate):
    edge = Edge(source_node, predicate, dest_node)
    redis_graph.add_edge(edge)


apidocumentation()


for i in redis_graph.edges:
    print i
print "\n\n\n\n"
for i in redis_graph.nodes:
    print i
