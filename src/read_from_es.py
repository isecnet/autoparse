#!/usr/bin/env python3
"""
Read log records from Elasticsearch. Emits a stream to `stdout`.
"""

import json
import os
import sys
import uuid
from argparse import ArgumentParser

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

import settings


def run(constants):
    host = constants['host'] or os.getenv('ES_HOST')
    index = constants['index'] or os.getenv('ES_INDEX')
    user = constants['username'] or os.getenv('ES_USERNAME')
    password = constants['password'] or os.getenv('ES_PASSWORD')

    client = Elasticsearch([host], http_auth=(user, password))
    s = Search(using=client, index=index)

    max_lines = constants.get('max_lines', sys.maxsize)
    i = 0
    if constants['is_stream']:
        for hit in s:
            for result in hit.results:
                for line in result.body.splitlines():
                    if len(line) > 0:
                        print(json.dumps({
                            'id': str(uuid.uuid1()),
                            'source_collection': index,
                            'line': line,
                            'metadata': {}
                        }))
                        i += 1
                        if i == max_lines:
                            sys.exit(0)


if __name__ == '__main__':
    # read args
    parser = ArgumentParser(description='Run Elasticsearch Reader')
    parser.add_argument('--host', dest='host', type=str, help='elasticsearch host')
    parser.add_argument('--index', dest='index', type=str, help='elasticsearch index')
    parser.add_argument('--user', dest='username', type=str, help='elasticsearch user')
    parser.add_argument('--password', dest='password', type=str, help='elasticsearch password')
    parser.add_argument('--maxlines', dest='max_lines', type=int, default=-1,
                        help='maximum number of log lines to read')
    parser.add_argument('--stream', dest='is_stream', help='set streaming mode', action='store_true')
    parser.set_defaults(is_stream=False)
    args = parser.parse_args()

    run(vars(args))
