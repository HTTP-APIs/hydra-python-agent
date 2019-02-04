from redisgraph.query_result import QueryResult
"""
Used to decorate data returned from redis memory
"""


def encode_result(result: QueryResult):
    for record in result.result_set[0:]:
        for item in range(len(record)):
            record[item] = record[item].decode('utf-8')
    result.statistics = ""
