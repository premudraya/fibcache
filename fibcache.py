# -*- coding: utf-8 -*-

import os
import time
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from collections import OrderedDict

PORT = int(os.environ.get('FIB_PORT', 8000))


class Cache(object):
    def __init__(self, limit=50):
        self.cached_values = OrderedDict()
        self.limit = limit

    def _move_to_end(self, key):
        value = self.cached_values.pop(key)
        self.cached_values[key] = value

    def get_value(self, key):
        if key not in self.cached_values:
            return None

        # Взять значение из кеша по ключу key, и переместить его в конец.
        # Таким образом, последние запрошенные значения будут оставаться в конце кеша,
        # а не используемые будут удаляться из начала в функцией push_value().

        self._move_to_end(key)
        return self.cached_values[key]

    def push_value(self, key, value):
        # Добавить значение value в кеш по ключу key. Если в кеше не осталось места,
        # удалить из него значение, использованное ранее всего (хранится первым).

        if key not in self.cached_values \
                and len(self.cached_values) == self.limit:
            self.cached_values.popitem(last=False)
        self.cached_values[key] = value

fib_cache = Cache()


def fib(n):
    if n in (1, 2):
        return 1

    value = fib_cache.get_value(n)

    if not value:
        value = fib(n - 2) + fib(n - 1)
        fib_cache.push_value(n, value)
    return value


class FibonacciForm(BaseHTTPRequestHandler):

    get_template = (
        r"<html>"
        r"<head><title>Fib calculator</title></head>"
        r"<body>"
        r"  <form action='/' method='POST'>"
        r"    <p>Какое число Фибоначчи вы хотите получить?</p>"
        r"    <input type='number' min='1' max='100' value='1' name='n'>"
        r"    <input type='submit'>"
        r"  </form>"
        r"</body>")

    post_template = (
        r"<html>"
        r"<head><title>Fib calculator</title></head>"
        r"<body>"
        r"  <p>Ваш результат: %s</p>"
        r"</body>")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(self.get_template)

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

        length = int(self.headers.getheader('Content-Length'))
        post_data = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)

        value = fib(int(post_data['n'][0]))

        self.wfile.write(self.post_template % value)


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class(("", PORT), FibonacciForm)
    print time.asctime(), "Server Starts, port %d" % PORT
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops"
