import redis
import json

"""Test for testing the data stored in collection endpoints"""

r = redis.StrictRedis()
reply = r.execute_command('GRAPH.QUERY',
                          'apidoc',"MATCH (p:collection) RETURN p")
obs = []
# reply is same as a table format and simplify it below in a familiar way.
# Redis returns a byte string and we have to convert it into json.
# members contain the collection of objects
# methods contains the operation can be done over the object.
# title contains the title or name of specific collection
for obj in reply:
    flag =0
    for obj1 in obj:
        if flag ==0:
            string = obj1.decode('utf-8')
            ob = map(str.strip, string.split(','))
            obs= list(ob)
            flag+=1
        else:
            string1 = obj1.decode('utf-8').replace("'", '"')
            newstr = '[' + string1 + ']'
            data = json.loads(newstr)
            print("\nid= ",data[2])
            for i in range(len(obs)): 
                print("\nobject: ",obs[i],":",data[i])
