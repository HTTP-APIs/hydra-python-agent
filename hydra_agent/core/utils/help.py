"""Help function to help user with commands and their formats"""


def help():
    """ Help function to help user with commands and their formats"""
    print("Connecting to an API :- \n")
    print("connect\n")
    print("Querying Format\n")
    print("Get all endpoints :- show endpoints\n")
    print("Get all class_endpoints:- show classEndpoints\n")
    print("Get all collection_endpoints:- show collectionEndpoints\n")
    print("Get all members of collection_endpoint:-",
          "show <collection_endpoint> members\n")
    print("Get all properties of objects:-",
          "show objects<endpoint_type> properties\n")
    print("Get all properties of any member:-",
          "show object<id_of_member> properties\n")
    print("Get all classes properties:-show class<class_endpoint> properties\n")
    print("Get data with compare properties:-",
          "show <key> <value> and/or <key1> <value1>\n")
    print("Get data by using both opeartions(and,or)",
          "you should use brackets like:-",
          "show model xyz and (name Drone1 or name Drone2)",
          "or, show <key> <value> and (<key> <value> or <key> <value>)\n")