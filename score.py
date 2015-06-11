#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# $File: score.py

import requests
#import unirest
import json
import math
import random
	
def expression_sightcorp(pic):
	json_resp = requests.post( 'http://api.sightcorp.com/api/detect/',
              data   = { 'app_key'   : '4abab32a3d064bdb85810374b6c01d5f',
                         'client_id' : 'a54ed59cac2f4d169d1e6f6f555003df',
						 'attribute' : 'expressions',
						 'max_persons': 1		},
              files  = { 'img'       : ( 'filename', open( pic, 'rb' ) ) }, 
			   )
	#print "sightcorp : ", json_resp.text
	return json_resp.text
	
def expression_score_sightcorp(tag, pic):
	#print pic
	json_resp = expression_sightcorp(pic)
	res = json.loads( json_resp )
	#print_result("sightcorp", json_resp)
	if len(res['persons'])==0:
		print 'no face detected'
		return 0
		
	expressions = res['persons'][0]['expressions']
	sum = 0.0
	for tags in expressions:
		sum += float(expressions[tags]['value'])
	if tag == 0:		
		return float(100) * float((expressions['happiness']['value']+expressions['surprise']['value']) / sum)
	elif tag == 1:
		return float(100) * float((expressions['anger']['value']+expressions['disgust']['value']) / sum)
	elif tag == 2:
		return float(100) * float((expressions['sadness']['value']+expressions['fear']['value']+expressions['disgust']['value']) / sum)
	elif tag == 3:
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
	
def expression_similarity_sightcorp(pic1, pic2):	
	#print pic1
	#print pic2
	json_resp1 = expression_sightcorp(pic1)
	res1 = json.loads( json_resp1 )
	json_resp2 = expression_sightcorp(pic2)
	res2 = json.loads( json_resp2 )
	print res1
	print res2
	
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
def calc_score(user_pic, dst_pic):
	res = dst_pic.split('/')
	dst_name = res[-1]
	if dst_name[0] == 'e':
		tag = dst_name[2]
		score = expression_sightcorp(int(tag), user_pic)
	else:
		benchmark_pic = res[0]+'/'+res[1]+'/benchmark/'+res[2]
		score = expression_similarity_sightcorp(benchmark_pic, user_pic)
	return score
#print expression_emovu(0, PIC1)