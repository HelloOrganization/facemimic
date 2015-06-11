# coding: utf-8
import os
import random
import uuid
import leancloud

from datetime import datetime

from flask import Flask, request
from flask import render_template, send_file, make_response, redirect
import sys
from views.todos import todos_view
from score import calc_score

static_dir = 'static/'
img_dir = 'static/img/'
img_upload_dir = 'static/img/upload/'

app = Flask(__name__)
# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')


not_ajax = False
if len(sys.argv) > 1 and sys.argv[1] == 'not_ajax':
	not_ajax = True

use_local = False
if len(sys.argv) > 2 and sys.argv[2] == 'use_local':
	use_local = True

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/another')
def another():
	fn = random.choice(os.listdir(img_dir))
	chosen = img_dir + fn
	while os.path.isdir(chosen):
		fn = random.choice(os.listdir(img_dir))
		chosen = img_dir + fn
	return chosen

@app.route('/result', methods=['POST'])
def result():
	#print request.files
	global use_local
	photo = request.files['photo']
	photo_uuid = str(uuid.uuid4())
	print photo_uuid
	content = photo.stream.read()
	#print len(content)
	photo_file = leancloud.File(photo_uuid, buffer(content))
	photo_file.save()
	print 'save leancloud'
	print use_local
	if use_local:
		local_file_name = img_upload_dir + photo_uuid + ".jpg"
		dst = open(local_file_name, 'wb')
		dst.write(content)
		dst.close()
		print 'use_local', local_file_name
	print 'after save'
	global not_ajax
	if not_ajax:
		dst_img = request.args.get('dst_img')
		if use_local:
			score_arr = calc_score(local_file_name, dst_img)
		else:
			score_arr = calc_score(photo_file.url, dst_img)
		resp = make_response(render_template("result.html", score=score_arr[0], percent=score_arr[1], review=score_arr[2]))
		resp.set_cookie('ajax', '0')
		return resp
	else:
		resp = make_response(render_template("result.html", score='?', percent='?', review='...'))
		resp.set_cookie('ajax', '1')
		resp.set_cookie('url', photo_file.url)
		resp.set_cookie("uuid", photo_uuid)
		return resp

@app.route('/calc')
def calc():
	global use_local
	dst_img = request.args.get('dst_img')
	print 'dst_img:', dst_img
	if use_local:
		photo_uuid = request.args.get('uuid')
		user_img = img_upload_dir + photo_uuid + ".jpg"
		print 'user_img:', user_img
		score_arr = calc_score(user_img, dst_img)
	else:
		user_url = request.args.get('url')
		print 'user_url:', user_url
		score_arr = calc_score(user_url, dst_img)
	return str(score_arr)

@app.route('/time')
def time():
    return str(datetime.now())

if __name__ == '__main__':
	APP_ID="wy1vhkf58knzywjpmny6r1pqbywmy3zxqo1qmj35mmaizd0z"
	APP_KEY="10hyto051fgrtxib3uo5yie10s4da1jx500qjyk3qek24d0p"
	MASTER_KEY="pye4tgaw8edmxlw7sct48xnb4r9h5lowdcufqokyug5cvy2q"
	leancloud.init(APP_ID, master_key=MASTER_KEY)
	port = int(os.environ.get("PORT", 3100))
	app.run(host='0.0.0.0', port=port)