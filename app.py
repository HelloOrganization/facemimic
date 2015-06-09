# coding: utf-8
import os
import random
from leancloud import File as LeanFile

from datetime import datetime

from flask import Flask, request
from flask import render_template, send_file, make_response, redirect

from views.todos import todos_view

static_dir = 'static/'
img_dir = 'static/img/baoman/'

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
	return chosen + '?type=baoman'

@app.route('/show', methods=['POST'])
def show():
	print request.files
	photo = request.files['photo']

	photo.save(img_dir + 'photo.jpg')
	return render_template("show.html")

@app.route('/time')
def time():
    return str(datetime.now())
