# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import time
import random
import uuid
import leancloud
from leancloud import Query as LeanQuery
import threading
from datetime import datetime

from flask import Flask, request
from flask import render_template, send_file, make_response, redirect
from views.todos import todos_view
from score import calc_score, compress, transpose
DEBUG = True
static_dir = 'static/'
img_dir = 'static/img/'
img_upload_dir = 'static/img/upload/'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')


not_ajax = False
if len(sys.argv) > 1 and sys.argv[1] == 'not_ajax':
	not_ajax = True

use_local = False # always true
if len(sys.argv) > 2 and sys.argv[2] == 'use_local':
	use_local = True

my_port = 3100
if len(sys.argv) > 3:
	try:
		my_port = int(sys.argv[3])
	except Exception, e:
		my_port = 3100

LeanScore = leancloud.Object.extend('Score')
LeanLog = leancloud.Object.extend('Log')

@app.teardown_request
def teardown_request(exception):
	global LeanLog
	lean_log = LeanLog()
	lean_log.set('ip', request.remote_addr)
	lean_log.set('url', request.url)
	lean_log.set('phone', request.cookies.get('platform'))
	lean_log.set('exception', str(exception))
	lean_log.save()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/another')
def another():
	print request
	fn = random.choice(os.listdir(img_dir))
	chosen = img_dir + fn
	while os.path.isdir(chosen):
		fn = random.choice(os.listdir(img_dir))
		chosen = img_dir + fn
	return chosen

threads = {}
scores = {}

def calc_thread(dst_img, photo_uuid, user_url, lean_score, platform):
	global scores
	global use_local
	score_arr = [0, 0, 0]
	if use_local:
		if platform == 'i':
			user_img = img_upload_dir + photo_uuid + ".jpg.min.jpg"
		else:
			user_img = img_upload_dir + photo_uuid + ".jpg"
		print 'user_img thr:', user_img
		score_arr = calc_score(user_img, dst_img)
	else:
		print 'use lean'
		score_arr = calc_score(user_url, dst_img)
	lean_score.set('score', score_arr[0])
	lean_score.set('percent', score_arr[1])
	lean_score.set('review', score_arr[2])
	lean_score.increment('page_view', 1)
	lean_score.save()
	scores[photo_uuid] = str(score_arr)

@app.route('/result', methods=['POST'])
def result():
	#print request.files
	global use_local
	global threads
	print '0',time.ctime()
	platform = request.cookies.get('platform')
	photo = request.files['photo']
	photo_uuid = str(uuid.uuid4())
	dst_img = request.args.get('dst_img')
	content = photo.stream.read()
	print '1',time.ctime()
	buffer_content = transpose(buffer(content), platform)
	print '2',time.ctime()
	photo_file = leancloud.File(photo_uuid + ".jpg", buffer_content, 'image/jpeg')
	photo_file.save()
	# new_local_file_name = compress(local_file_name, platform)
	# print '2',time.ctime()
	# print 'new', new_local_file_name
	# new_local_file = open(new_local_file_name)
	# photo_file = leancloud.File(photo_uuid + '.jpg', new_local_file, 'image/jpeg')
	# new_local_file.close()
	# photo_file.save()
	print '3',time.ctime()
	print 'save leancloud'
	print 'after save'
	global LeanScore
	score = LeanScore()
	score.set("uuid", photo_uuid)
	score.set('dst_img', dst_img)
	score.set('user_url', photo_file.url)
	score.save()
	t = threading.Thread(target=calc_thread, args=(dst_img, photo_uuid, photo_file.url, score, platform))
	t.start()
	threads[photo_uuid] = t
	resp = make_response(redirect("/share?id="+score.id))
	print '4',time.ctime()
	return resp
	
@app.route('/share')
def share():
	global LeanScore
	print '5',time.ctime()
	leanId = request.args.get('id')
	query = LeanQuery(LeanScore)
	try:
		score = query.get(leanId)
	except Exception, e:
		return "Not Found"
	user_url = score.get('user_url')
	dst_img = score.get('dst_img')
	if score.get("page_view") > 0:
		score.increment('page_view', 1)
		score_arr = [score.get('score'), score.get('percent'), score.get('review')]
		score.save()
		resp = make_response(render_template("result.html", score=score_arr[0], percent=score_arr[1], review=score_arr[2], preview1=user_url, preview2=dst_img,btnInfo='我也要模仿'))
		#resp.set_cookie('url', photo_file.url)
		resp.set_cookie('ajax', '0')
		return resp
	# else:
	print '6',time.ctime()
	global not_ajax
	photo_uuid = score.get('uuid')
	if not_ajax:
		print 'not_ajax'
		if use_local:
			local_file_name = img_upload_dir + photo_uuid + ".jpg"
			score_arr = calc_score(local_file_name, dst_img)
		else:
			score_arr = calc_score(user_url, dst_img)
		#print 'ok', score_arr
		score.increment('page_view', 1)
		score.save()
		resp = make_response(render_template("result.html", score=score_arr[0], percent=score_arr[1], review=score_arr[2], preview1=user_url, preview2=dst_img, btnInfo='再再……再来一次！‘(*>﹏<*)′'))
		#resp.set_cookie('url', photo_file.url)
		resp.set_cookie('ajax', '0')
		return resp
	else:
		print '7',time.ctime()
		# platform = request.cookies.get('platform')
		# t = threading.Thread(target=calc_thread, args=(dst_img, photo_uuid, user_url, score, platform))
		# t.start()
		# threads[photo_uuid] = t
		#print '8',time.ctime()
		resp = make_response(render_template("result.html", score='?', percent='?', review='7', preview1=user_url, preview2=dst_img, btnInfo='再再……再来一次！‘(*>﹏<*)′'))
		resp.set_cookie('ajax', '1')
		resp.set_cookie("uuid", photo_uuid)
		print '9',time.ctime()
		return resp
	return 'ok'
@app.route('/calc')
def calc():
	global threads
	global scores
	photo_uuid = request.args.get('uuid')
	if not photo_uuid:
		return "Not Found"
	print '10',time.ctime()
	threads[photo_uuid].join()
	print '11',time.ctime()
	del threads[photo_uuid]
	score = scores[photo_uuid]
	del scores[photo_uuid]
	return score
	# global use_local
	# dst_img = request.args.get('dst_img')
	# print 'dst_img:', dst_img
	# if use_local:
	# 	photo_uuid = request.args.get('uuid')
	# 	user_img = img_upload_dir + photo_uuid + ".jpg"
	# 	print 'user_img:', user_img
	# 	score_arr = calc_score(user_img, dst_img)
	# else:
	# 	user_url = request.args.get('url')
	# 	print 'user_url:', user_url
	# 	score_arr = calc_score(user_url, dst_img)
	# return str(score_arr)


if __name__ == '__main__':
	APP_ID="wy1vhkf58knzywjpmny6r1pqbywmy3zxqo1qmj35mmaizd0z"
	APP_KEY="10hyto051fgrtxib3uo5yie10s4da1jx500qjyk3qek24d0p"
	MASTER_KEY="pye4tgaw8edmxlw7sct48xnb4r9h5lowdcufqokyug5cvy2q"
	leancloud.init(APP_ID, master_key=MASTER_KEY)
	port = int(os.environ.get("PORT", my_port))
	app.run(host='0.0.0.0', port=port)