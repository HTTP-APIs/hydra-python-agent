# python-hydra-agent

This branch has been created only to be used as a reference when refactoring python-hydra-agent in the future.

### Changes Made

- Improved the package structure
- Improved the algorithm being used to connect various edges between the nodes
- Added type-annotations
- Better printing format of the data
- Added try-except block wherever necessary
- Some methods have been converted to static methods to improve performance and purity

### Explanation

- Package Structure -- `python-hydra-agent` has been organised into 3 layers. utils(primary code), core(secondary code) and hydra_agent(bookkeeping code). utils contains all the primary modules such as `class_objects` , `collection_endpoint` etc. core contains all the modules related to query types.
  hydra_agent contains all the modules which act as an interface for the user.![(/home/shravan/Desktop/Screenshot_20190205_035727.png)

- The time complexity(average case) for the algorithm being used to connect edges between various class nodes has been decreased from O(n<sup>2</sup>k<sup>2</sup>) to O(k<sup>2</sup>) (where k represents the number of classEndpoints having other endpoints as properties and n represents the number of nodes in graph). The previous algorithm used to traverse over all the nodes in the graph to find the ones to connect. This process is heavy and takes time. It has been replaced by the use of dictionary which has an average case complexity of O(1) and a worst case complexity of O(n). Even if the worst case scenario is considered, the number of keys in dictionary are going to be less than the number of nodes in graph(because it contains `collectionEndpoints` as well) and the time complexity will be O(k<sup>4</sup>)

- New printing format

  ```bash
  >>>show endpoints
  Class Endpoints -- 
  
  +----------------------------+--------+-----------------------+-----------------+
  |        p.properties        | p.type |          p.id         |   p.operations  |
  +----------------------------+--------+-----------------------+-----------------+
  | ['TopLeft', 'BottomRight'] |  Area  | vocab:EntryPoint/Area | ['POST', 'GET'] |
  +----------------------------+--------+-----------------------+-----------------+
  
  Collection Endpoints -- 
  
  +----------------------+---------------------------------------+----------------+-----------+
  |        p.type        |                  p.id                 |  p.operations  | p.members |
  +----------------------+---------------------------------------+----------------+-----------+
  |  LogEntryCollection  |  vocab:EntryPoint/LogEntryCollection  | ['GET', 'PUT'] |    NULL   |
  |   DroneCollection    |    vocab:EntryPoint/DroneCollection   | ['GET', 'PUT'] |    NULL   |
  | DatastreamCollection | vocab:EntryPoint/DatastreamCollection | ['GET', 'PUT'] |    NULL   |
  |  MessageCollection   |   vocab:EntryPoint/MessageCollection  | ['GET', 'PUT'] |    NULL   |
  |  CommandCollection   |   vocab:EntryPoint/CommandCollection  | ['GET', 'PUT'] |    NULL   |
  |   StateCollection    |    vocab:EntryPoint/StateCollection   | ['GET', 'PUT'] |     []    |
  +----------------------+---------------------------------------+----------------+-----------+
  
  ```

  

- Methods such as `RedisProxy().get_connection()`don't need instantiation of the class. Hence they've been made static and used as `RedisProxy.get_connection()`



### Usage

Fire up `redisgraph` server(assuming you have docker installed)

```bash
docker run -p 6379:6379 --rm redislabs/redisgraph
```

One a new terminal window type the following--

```bash
git clone https://github.com/ShravanDoda/python-hydra-agent.git
cd python-hydra-agent
git checkout refactor_async
```

Install virtual environment and install the dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install redis
pip install redisgraph
pip install git+https://github.com/ShravanDoda/hydra-python-core@develop#egg=hydra-python-core
```

Run `python-hydra-agent`

```bash
cd hydra_agent
python querying_mechanism.py
```

Using `python-hydra-agent`

```python
>>>connect
Please input the address of the API you want to connect to -> http://localhost:8080/serverapi
```



### Missing

- No new functionality has been added
- No test suite
- Docker image hasn't been created
- Uses hydra_python_core as a dependency which hasn't been merged yet

