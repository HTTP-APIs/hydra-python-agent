In the redisgraph_demo1, storing the API structure in the graph using Redisgraph.py.
 
For now, it is rough graph and I have to added some more functions and properties and build the fine graph of API structure.
And it is like a demo if this implementation is fine then I will move forward with this implementation.

here is the edges which show how the graph is connected:
`
(apidocumentation)-[:has_title]->(title)
(apidocumentation)-[:has_description]->(description)
(apidocumentation)-[:has_supportedclasses]->(supportedClasses)
(apidocumentation)-[:has_entrypoint]->(entrypoint)
(supportedClasses)-[:has_displayname]->(display_name)
(display_name)-[:has_description]->(description)
(display_name)-[:has_supportedoperations]->(supportedoperation)
(supportedoperation)-[:has_title]->(operation_title)
(operation_title)-[:has_method]->(operation_method)
(operation_title)-[:has_expectclass]->(operation_expects)
(operation_title)-[:has_returns]->(operation_returns)
(operation_title)-[:has_status]->(posiblestatus)
(posiblestatus)-[:has_status]->(status_code)
(display_name)-[:has_supportedproperty]->(supportedproperty)
(supportedproperty)-[:has_title]->(property_title)
(property_title)-[:has_property]->(property)
(property)-[:has_links]->(property_link)
(property_title)-[:has_requires]->(requires)
(property_title)-[:is_readonly]->(readonly)
(property_title)-[:is_writeonly]->(writeonly)
`


So, with this implementation we will get a graph structure in Redis memory, where we can store the data and can retrieve the data with the help of endpoints (I'll define the functions for put the data into the graph and and for the retrive the data from it).
 
How this graph is useful:

With the help of this implementaion we have a connected graph which can contain all the data like every property in the graph. So, we can get easily any property using graph.

And this graph can be access like this:
 we'll have many endpoints like apidocumentation, supportedclasses, supportedoperation, supportedproperty and ....
 if we get the first endpoint apidocumentation the we will go on apidocumentation node show its properties like this:
        apidocumentaion {
                            title : "hydra:title"
                            description : "hydra:description"
                            entrypoint : "hydra:entrypoint"
                            supportedclasses : "hydra:supportedclasses"
                        }
  and if now client have query for supportedclasses of the same apidocumentaion_id(above) then we will move forward in graph go to the node supportedclasses and will show all titles of it like:
        supportedclasses {
                             title1: "class_title1"
                             title2: "class_title2"
                             .
                             .
                             .
                         }
     and then client can query for any of class with the help of title of it.
     
And similary we can query for the other endpoints and can access whole the graph easily.

 

