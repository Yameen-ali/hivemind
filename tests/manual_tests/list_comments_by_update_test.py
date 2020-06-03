#!/usr/bin/python3
from .test_base import run_test

if __name__ == '__main__':
    reference_hive_node_url = 'https://api.hive.blog'
    test_hive_node_url = 'http://127.0.0.1:8080'

    payload = {
        "jsonrpc":"2.0",
        "method":"database_api.list_comments",
        "params" : {
            "start" : ['steemit', '1970-01-01T00:00:00', '', ''],
            "limit" : 10,
            "order" : 'by_update'
        },
        "id":1
    }

    run_test(reference_hive_node_url, test_hive_node_url, payload, ['author', 'permlink', 'parent_author', 'parent_permlink', 'updated_at'])
