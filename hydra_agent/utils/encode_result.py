def encode_result(result):
    for record in result.result_set[0:]:
        for item in range(len(record)):
            record[item] = record[item].decode('utf-8')
    result.statistics = ""