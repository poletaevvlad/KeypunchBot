# -*- coding: utf-8 -*-

from random import random


def application(environ, start_response):
    data = 'Hello, World! {}\n'.format(random())
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([bytes(data, "utf-8")])
