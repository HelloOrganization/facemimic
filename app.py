# coding: utf-8
import os
import random
import uuid
from leancloud import File as LeanFile

from datetime import datetime

from flask import Flask, request
from flask import render_template, send_file, make_response, redirect

from views.todos import todos_view
from score import calc_score

static_dir = 'static/'
img_dir = 'static/img/'
img_upload_dir = 'static/img/upload/'

app = Flask(__name__)
# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')


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
	photo = request.files['photo']
	photo_uuid = str(uuid.uuid4())
	print photo_uuid
	local_file_name = img_upload_dir + photo_uuid + ".jpg"
	photo.save(local_file_name)
	#photoFile = LeanFile('fileFromBuffer', buffer(photo))
	local_file = open(local_file_name)
	photo_file = LeanFile(photo_uuid, local_file)
	local_file.close()
	photo_file.save()
	resp = make_response(render_template("result.html"))
	resp.set_cookie("uuid", photo_uuid)
	return resp

@app.route('/calc')
def calc():
	photo_uuid = request.args.get('uuid')
	dst_img = request.args.get('dst_img')
	#mock_type = request.args.get('type')
	user_img = img_upload_dir + photo_uuid + ".jpg"
	print user_img, dst_img
	score = calc_score(user_img, dst_img)
	return str(score)

@app.route('/time')
def time():
    return str(datetime.now())
