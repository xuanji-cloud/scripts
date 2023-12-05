import os
import sys
from functools import update_wrapper

import click
import requests

API_BASE = "https://m.xj.edisec.net/v1"


def unwrap_response(resp):
    if resp.status_code != 200:
        print("[-] [%d]%s" % (resp.status_code, resp.text))
        exit()
    res = resp.json()
    if res['code'] != 0:
        print("[-] [%d]%s" % (res['code'], res['message']))
        exit()
    return res['data']


def require_login(f):
    @click.option('-u', '--username', help='Username', required=True)
    @click.option('-p', '--password', help='Password', required=True)
    @click.pass_context
    def func(ctx, *args, username, password, **kwargs):
        resp = requests.post(API_BASE + "/signin", json={
            "account": username,
            "password": password
        })
        data = unwrap_response(resp)
        ctx.ensure_object(dict)
        ctx.obj['TOKEN'] = data['token']
        ctx.obj['API_HEADERS'] = {
            "Authorization": "Bearer %s" % ctx.obj['TOKEN']
        }
        return ctx.invoke(f, ctx, *args, **kwargs)

    return update_wrapper(func, f)


class upload_in_chunks(object):
    def __init__(self, filename, chunk_size=1 << 13):
        self.filename = filename
        self.chunk_size = chunk_size
        self.totalsize = os.path.getsize(filename)
        self.read_sofar = 0

    def __iter__(self):
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.chunk_size)
                if not data:
                    sys.stderr.write("\n")
                    break
                self.read_sofar += len(data)
                percent = self.read_sofar * 1e2 / self.totalsize
                sys.stderr.write("\r{percent:3.0f}%".format(percent=percent))
                yield data

    def __len__(self):
        return self.totalsize
