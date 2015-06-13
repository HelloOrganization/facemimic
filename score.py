#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# $File: score.py

import requests
import json
import math
import random
import time
import pickle
from PIL import Image
from cStringIO import StringIO
import commands


bench_file = open('static/txt/bench.pkl', 'rb')
bench_list = pickle.load(bench_file)
error_code = 0
error_desp = ""
# try:
#      bench_str = bench_file.read()
# finally:
#      bench_file.close()

def expression_sightcorp_url(pic):
	json_resp = requests.post( 'http://api.sightcorp.com/api/detect/',
              data   = { 'app_key'   : '4abab32a3d064bdb85810374b6c01d5f',
                         'client_id' : 'a54ed59cac2f4d169d1e6f6f555003df',
						 'attribute' : 'expressions',
						 'max_persons': 1,		
						 'url': pic } 
			   )
	print json_resp.text
	return json_resp.text

def expression_sightcorp_file(content_StringIO):
	json_resp = requests.post( 'http://api.sightcorp.com/api/detect/',
              data   = { 'app_key'   : '4abab32a3d064bdb85810374b6c01d5f',
                         'client_id' : 'a54ed59cac2f4d169d1e6f6f555003df',
						 'attribute' : 'expressions',
						 'max_persons': 1 },
              files  = { 'img'       : ( 'filename', content_StringIO ) }
			   )
	print json_resp.text
	return json_resp.text

	
def expression_score_sightcorp(tag, content_StringIO):
	#print pic
	json_resp = expression_sightcorp_file(content_StringIO)
	res = json.loads( json_resp )
	#print_result("sightcorp", json_resp)
	if len(res)==2:
		global error_code, error_desp
		error_code = res["error_code"]
		error_desp = str(res["description"])
		return 0

	if len(res['persons'])==0:
		global error_code, error_desp
		error_code = 1500
		error_desp = "no face detected, height: "+str(res['img_height'])+" width: "+str(res['img_width'])
		return 0
		
	expressions = res['persons'][0]['expressions']
	sum = 0.0
	for tags in expressions:
		sum += float(expressions[tags]['value'])
	if tag == 1:		
		return float(100) * float((expressions['happiness']['value']+expressions['surprise']['value']) / sum)
	elif tag == 2:
		return float(100) * float((expressions['anger']['value']+expressions['disgust']['value']) / sum)
	elif tag == 3:
		return float(100) * float((expressions['sadness']['value']+expressions['fear']['value']+expressions['disgust']['value']) / sum)
	elif tag == 4:
		return float(100) * float((expressions['surprise']['value']+expressions['fear']['value']) / sum)
	else:
		return 0

def get_dis(exp1, exp2):
	sum1 = 0.0
	for tags in exp1:
		sum1 += exp1[tags]['value']**2
	sum1 = math.sqrt(sum1)
	#print 'sum1',sum1
	sum2 = 0.0
	for tags in exp2:
		sum2 += exp2[tags]['value']**2
	sum2 = math.sqrt(sum2)
	#print 'sum2',sum2
	dis = 0.0
	for tags in exp2:
		#print 10*exp1[tags]['value']/sum1, 10*exp2[tags]['value']/sum2
		dis += (40*exp1[tags]['value']/sum1-40*exp2[tags]['value']/sum2)**2
	dis = math.sqrt(dis)
	return dis
	
def expression_similarity_sightcorp(benchmark_index, content_StringIO):	
	global bench_list
	#print "len",len(bench_list)
	json_resp1 = bench_list[benchmark_index-1]
	res1 = json.loads( json_resp1 )
	json_resp2 = expression_sightcorp_file(content_StringIO)
	res2 = json.loads( json_resp2 )
	
	global error_code, error_desp
	if len(res2)==2:
		print 'sorry, error occured'
		return 0

	if len(res2['persons'])==0:
		print 'no face detected'
		return 0
	
	expressions1 = res1['persons'][0]['expressions']
	expressions2 = res2['persons'][0]['expressions']
	
	#dis += (1-expressions2[tags]['value'])**2	
	dis = get_dis(expressions1, expressions2)
	return 100-int(dis)

#score1 = metric_similarity(PIC1, PIC2)
#print score1
def get_per(score):
	return int(100*math.sqrt(float(score)/100))

def get_review(score):
	if score >= 95 and score <= 100: 
		return 0
		return "你对面部动作、眼神、情绪的把握已经臻于化境！天哪，我还以为你是这些表情的原型，而不是它们的模仿！"
	elif score >= 85 and score <= 94:
		return 1
		return "非……非常好，就是这种感觉！令人潸然泪下的感人模仿！请务必分享到朋友圈让大家看看……"
	elif score >= 75 and score <= 84:
		return 2
		return "出人意料的良好表现！这次模仿令我印象深刻，我会记住你的。"
	elif score >= 60 and score <= 74:
		return 3
		return "哎唷不错~我觉得已经很像了！不过如果你觉得你的技艺不止于此的话，那么请继续前进吧！"
	elif score >=40 and score <= 59:
		return 4
		return "想象一下图中的人物是怀着何等心情做出这样的表情的，他又遇到了什么样的夸张事情，然后再假象自己置身其中，体会同样的情绪，最后大胆地表现出来！你一定可以的！再来一次吧~"
	elif score >=1 and score <= 39:
		return 5
		return "呀！模仿还需继续努力哦~再来一次吧！或者分享到朋友圈让他人评点！节操什么的就不要太在意啦。"
	else:
		return 6
		return "咦？0分？不要惊慌，可能是我们没有在照片中检测到人脸，也可能是拍摄姿势不对，记住要拿起手机竖着拍摄哦！不如再来一次！"

def transpose(buffer_content, platform):
	print buffer_content[0:10]
	if platform != 'i':
		return buffer_content
	im = Image.open(StringIO(buffer_content))
	new_im = im.transpose(Image.ROTATE_270)
	fake_file = StringIO()
	new_im.save(fake_file, 'jpeg')
	fake_file.seek(0)
	return fake_file


def compress(user_pic, platform):
	if platform == 'a':
		return user_pic
	status, new_user_pic = commands.getstatusoutput("java -classpath . RotatePic "+ user_pic)
	# user_img = Image.open(user_pic)
	# new_img = user_img.transpose(Image.ROTATE_270) 
	# new_user_pic = user_pic + ".min.jpg"
	# new_img.save(new_user_pic)
	# ori_w,ori_h = user_img.size
	# if max(ori_h,ori_w) >= 1000:
	# 	ratio = 1000.0/max(ori_h,ori_w)
	# 	new_img = user_img.resize((int(ori_w*ratio), int(ori_h*ratio)))
	# 	new_img.rotate(90)
	# 	new_user_pic = user_pic + ".min.jpg"
	# 	new_img.save(new_user_pic)
	return new_user_pic
	#return user_pic

def calc_score(user_content_StringIO, dst_pic):
	#print user_pic, dst_pic
	res = dst_pic.split('/')
	dst_name = res[-1]
	if dst_name[0] == 'e':
		tag = dst_name[2]
		score = expression_score_sightcorp(int(tag), user_content_StringIO)
	else:
		benchmark_index = (dst_name.split('.'))[0]
		#print benchmark_index
		score = expression_similarity_sightcorp(int(benchmark_index), user_content_StringIO)
	global error_code, error_desp
	return [int(score), get_per(score), get_review(score), error_code, error_desp]
#print expression_emovu(0, PIC1)

# print expression_similarity_sightcorp(1, "static/img/benchmark/1.jpg")
# bench = []
# path = "static/img/benchmark/"
# for i in range(1, 24):
# 	bench.append(expression_sightcorp(path+str(i)+'.jpg'))
# 	time.sleep(1)

# pickle.dump(bench,bench_file)
# bench_file.close()
