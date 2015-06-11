# coding: utf-8

import os

import leancloud
from wsgiref import simple_server

from app import app
from cloud import engine

test = True
if test:
	APP_ID="wy1vhkf58knzywjpmny6r1pqbywmy3zxqo1qmj35mmaizd0z"
	APP_KEY="10hyto051fgrtxib3uo5yie10s4da1jx500qjyk3qek24d0p"
	MASTER_KEY="pye4tgaw8edmxlw7sct48xnb4r9h5lowdcufqokyug5cvy2q"
	PORT=3100
else:
	APP_ID = os.environ['LC_APP_ID']
	MASTER_KEY = os.environ['LC_APP_MASTER_KEY']
	PORT = int(os.environ['LC_APP_PORT'])


leancloud.init(APP_ID, master_key=MASTER_KEY)

application = engine


if __name__ == '__main__':
    # 只在本地开发环境执行的代码
    app.debug = True
    server = simple_server.make_server('localhost', PORT, application)
    print "Running on http://localhost:%d"%PORT
    server.serve_forever()
