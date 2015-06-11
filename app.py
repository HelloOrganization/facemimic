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

save_local = False
if len(sys.argv) > 1 and sys.argv[1] == 'save_local':
	save_local = True

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
	global save_local
	photo = request.files['photo']
	photo_uuid = str(uuid.uuid4())
	print photo_uuid
	content = photo.stream.read()
	#print len(content)
	photo_file = leancloud.File(photo_uuid, buffer(content))
	photo_file.save()
	print 'save leancloud'
	print save_local
	resp = make_response(render_template("result.html"))
	if save_local:
		resp.set_cookie('avos', '0')
		resp.set_cookie("uuid", photo_uuid)
		local_file_name = img_upload_dir + photo_uuid + ".jpg"
		dst = open(local_file_name, 'wb')
		dst.write(content)
		dst.close()
		print 'save_local', local_file_name
	else:
		resp.set_cookie('avos', '1')
		resp.set_cookie('url', photo_file.url)
	print 'after save'
	return resp

@app.route('/calc')
def calc():
	use_avos = request.args.get('avos')
	dst_img = request.args.get('dst_img')
	print 'dst_img:', dst_img
	if use_avos == '0':
		photo_uuid = request.args.get('uuid')
		user_img = img_upload_dir + photo_uuid + ".jpg"
		print 'user_img:', user_img
		score = calc_score(user_img, dst_img)
	else:
		user_url = request.args.get('url')
		print 'user_url:', user_url
		score = 100
	return str(score)

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