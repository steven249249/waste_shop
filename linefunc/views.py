
from django.shortcuts import render,redirect
# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from linebot import LineBotApi, WebhookParser,WebhookHandler
import linebot
from flask import Flask, request,json
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
		MessageEvent,
		TextSendMessage,
		TemplateSendMessage,
		ButtonsTemplate,
		MessageTemplateAction,
		PostbackEvent,
		PostbackTemplateAction,
		AccountLinkEvent
)
from linebot.models import *
from . import models
from urllib.parse import parse_qsl
import time
from liffpy import (
		LineFrontendFramework as LIFF,
		ErrorResponse
)
from django.urls import reverse
from django.contrib import messages 
import json
import requests
import threading
from secrets import *
import base64
import re
import datetime
import string
import random
liff_api = LIFF(settings.LINE_CHANNEL_ACCESS_TOKEN)
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
headers = {'Authorization':"Bearer "+settings.LINE_CHANNEL_ACCESS_TOKEN,'Content-Type':'application/json'}
login_user = None
@csrf_exempt
#負責接受從line傳過來的請求
def callback(request):
	global webhook,webhook_url
	if request.method == 'POST':
		signature = request.META['HTTP_X_LINE_SIGNATURE']
		body = request.body.decode('utf-8')

		try:
			events = parser.parse(body, signature)
		except InvalidSignatureError:
			return HttpResponseForbidden()
		except LineBotApiError:
			return HttpResponseBadRequest()
		webhook = line_bot_api.get_webhook_endpoint()
		webhook_url = webhook.endpoint
		for event in events:
			try:
				uid=event.source.user_id
				profile = line_bot_api.get_profile(uid)
				name=profile.display_name
				if models.User.objects.filter(uid = uid):
					pass
				else:
					models.User.objects.create(uid=uid,name=name)

				if isinstance(event, MessageEvent):#如果是訊息事件
					#先取得傳訊息的資訊
					mtext=event.message.text
					#輸入文字資訊來選擇功能			
					if mtext =='我有剩食':
						print(type(event.reply_token))
						message = TextSendMessage('https://liff.line.me/1657551781-Nw414Paj')							
						line_bot_api.reply_message(event.reply_token,message)
					elif mtext == '尋找剩食':
						search_food(event)
					elif mtext =='確認訂單':
						message = TextSendMessage('https://liff.line.me/1657551781-Z1PxP0d6')             
						line_bot_api.reply_message(event.reply_token,message)
					elif mtext =='顧客確認':
						message = TextSendMessage('https://liff.line.me/1657551781-OZyWyPk5')             
						line_bot_api.reply_message(event.reply_token,message)

				elif isinstance(event, PostbackEvent):
					backdata = dict(parse_qsl(event.postback.data))
					if backdata.get('action') == 'find':
						select_food_button(event)
					elif backdata.get('action') == 'all_food':
						search_food(event,'all_food')
					elif backdata.get('action') == 'bread':
						search_food(event,'bread')
					elif backdata.get('action') == 'bento':
						search_food(event,'bento')
					# if backdata.get('action') == 'login':
					# 	login(event)
					# elif backdata.get('action') == 'link':
					# 	account_link(event,backdata)
					

				elif isinstance(event, AccountLinkEvent):

					message=TextSendMessage(text='綁定成功')
					line_bot_api.reply_message(event.reply_token,message)
					

			except linebot.exceptions.LineBotApiError as e:
				print(e.status_code)
				print(e.request_id)
				print(e.error.message)
				print(e.error.details)

		return HttpResponse()
	else:
		return HttpResponseBadRequest()

class Store_Food_Thread(threading.Thread):

	def __init__(self,store_food_id,time_):
		threading.Thread.__init__(self)
		if models.Store_food.objects.filter(id=store_food_id):
			self.store_food = models.Store_food.objects.filter(id=store_food_id)[0]
		else:
			self.store_food = None
		self.time_ = time_
	def run(self):
		if self.store_food:
			pass_time = 0
			while True:
				if pass_time>=self.time_:
					self.store_food.online  = False
					self.store_food.save()
					print('thread_end')
					break
				print(pass_time)
				pass_time +=5
				time.sleep(5)
		else:
			print('store_food not find')


def convert_html_time(time_):
	time_ = time_.split(':')
	time_ = datetime.time(int(time_[0]), int(time_[1]), 0)
	date_ = datetime.datetime.now().date()
	time_ = datetime.datetime.combine(date_,time_)

	return time_
@csrf_exempt
def store_give(request):
	print(request.POST)

	if request.is_ajax():
		print(request.is_ajax())
		uid = request.POST.get('uid')
		price = request.POST.get('price')
		number = request.POST.get('number')
		end_order_time =request.POST.get('end_order_time')
		end_order_time = convert_html_time(end_order_time)
		print(end_order_time)
		end_get_time = request.POST.get('end_get_time')
		end_get_time = convert_html_time(end_get_time)
		print(end_get_time)
		print(type(end_get_time))
		try:
			image = request.FILES.getlist('imgFiles_add')[0]
			img_flag = True
		except:
			messages.add_message(request,messages.WARNING,"必須附圖片")
			img_flag = False

		if img_flag == True:
			print(uid)
			print(image)
			if models.Store.objects.filter(uid=uid):
				if models.Store_food.objects.filter(store=models.Store.objects.filter(uid=uid)[0]).filter(online=True):
					messages.add_message(request,messages.WARNING,"你已經有一份剩食委託")
				else:
					if int(number) <= 1000  and int(number)>0:
						if int(price) <= 1000 and int(price)>0:
							time_now_plus_ten = datetime.datetime.now()+datetime.timedelta(minutes=10)
							print(time_now_plus_ten)
							if  time_now_plus_ten < end_order_time: 
								if end_get_time >=end_order_time:			
									store = models.Store.objects.filter(uid=uid)[0]
									store_food = models.Store_food.objects.create(store=store,price=price,number=number,image=image,end_get_time=end_get_time,end_order_time=end_order_time)
									duration = store_food.end_order_time - store_food.start_time
									pass_s = duration.days*86400 + duration.seconds
									Store_Food_Thread(store_food.id,pass_s).start()
									messages.add_message(request,messages.SUCCESS,"創立剩食委託成功")
								else:
									messages.add_message(request,messages.WARNING,"最後取得餐點時間需比最後下訂時間晚或相同,時間只能在同一天")
							else:
								messages.add_message(request,messages.WARNING,"最後下訂時間需比現在時間晚10分鐘")
						else:
							messages.add_message(request,messages.WARNING,"輸入的價格請介於1~1000之間")
					else:
						messages.add_message(request,messages.WARNING,"輸入的數量請介於1~1000之間")
			else:
				messages.add_message(request,messages.WARNING,"你必須是商家才可以執行此操作")

	return render(request,'store_give.html',locals())
@csrf_exempt
def store_check_order(request):
	print(request.POST)
	if request.is_ajax():
			data = json.loads(request.POST.get('data'))
			uid = data[0]['uid']
			response_data = {}
			if models.Store.objects.filter(uid=uid):
				store = models.Store.objects.filter(uid=uid)[0]
				if models.Store_food.objects.filter(store=store):
					store_food= models.Store_food.objects.filter(store=store)
					if models.Order.objects.filter(store=store):
						response = {}
						response['now'] = []
						response['store_food']=[]
						if models.Store_food.objects.filter(store=store).filter(online=True):
							store_food_now = models.Store_food.objects.filter(store=store).filter(online=True)[0]
							orders = models.Order.objects.filter(store_food=store_food_now)
							data = [i.json() for i in orders]
							response['now'] = data
							response['store_food'] = store_food_now.json()

						orders_all = models.Order.objects.filter(store=store)
						data_all = [i.json() for i in orders_all]
						response['all'] = data_all
						response ['message']='成功'
						# print(response)
						# print(json.dumps(response)) #str
						return HttpResponse(json.dumps(response), content_type="application/json")
					else:
						response_data['message']= '尚未有訂單'
						return JsonResponse(response_data)
				else:
						response_data['message']= '沒有發布過剩食委託'
						return JsonResponse(response_data)
			else:
				response_data['message']= '你必須是商家才可以執行此操作'
				return JsonResponse(response_data)




	return render(request,'store_check_order.html',locals())
@csrf_exempt
def detail_order(request):
	print(request.GET)
	print('-----------------------')
	if 'order_id' in request.GET:
			order_id = request.GET['order_id']
			if models.Order.objects.filter(id = order_id):
				order = models.Order.objects.filter(id = order_id)[0]
			else:
				return HttpResponse('該訂單不存在')
	if request.is_ajax():
		data = json.loads(request.POST.get('data'))
		store_id = data[0]['store_id']
		order_id= data[0]['order_id']
		type_ =data[0]['type']
	
		if models.Store.objects.filter(uid=store_id):         
			store = models.Store.objects.filter(uid=store_id)[0]
			if models.Order.objects.filter(id=order_id):
				order  = models.Order.objects.filter(id=order_id)[0]
				if order.store == store:
					response = order.json()
					response['message'] = '店家正確'
					if type_ == 'to_check':
						check = data[0]['check']
						if order.paid == False:
							if check =='checked':
								if order.store_food.number-order.number>=0:
									order.check = True
									order.save()
									store_food = models.Store_food.objects.filter(id=order.store_food.id)
									store_food.update(number=store_food[0].number-order.number)

									webhook = line_bot_api.get_webhook_endpoint()
									webhook_url = webhook.endpoint
									pic_url = webhook_url+'/media/image/official_image/01.png'
									url_ ='https://liff.line.me/1657551781-GpqEqJPY?order_id={}'.format(order.id)
									print(url_)
									text = CarouselColumn(
										thumbnail_image_url=pic_url,
										title='你的訂單已被確認,訂單編號:{}'.format(order.id),
										text='前往查看訂單',
										# text="aaaa",
										actions=[
											URITemplateAction(
													label='查看訂單',
													uri='https://liff.line.me/1657551781-OZyWyPk5'
												)
											]
										)
									message = TemplateSendMessage(
											alt_text='你的訂單已被確認',
											template=CarouselTemplate(
											columns=[text]
										)
									)
									line_bot_api.push_message(order.user.uid,message)



									response['message'] = '成功確認訂單'
								else:
									response['message'] = '超出所提供份數'
							else:
								order.check = False
								order.save()
								store_food = models.Store_food.objects.filter(id=order.store_food.id)
								store_food.update(number=store_food[0].number+order.number)
								response['message'] = '成功取消確認訂單'
						else:
							response['message'] = '顧客已付款,不能更改確認訂單狀況'

					elif type_ == 'user_get':
						if order.paid == True:
							if order.user_get == False:
								response['message'] = '顧客成功取餐'
								order.user_get =True
								order.user_now = False
								order.save()
								uid = order.user.uid
								webhook = line_bot_api.get_webhook_endpoint()
								webhook_url = webhook.endpoint
								pic_url = webhook_url+'/media/image/official_image/01.png'
								url_ ='https://liff.line.me/1657551781-DOprpXyb?order_id={}'.format(order.id)
								print(url_)
								text = CarouselColumn(
									thumbnail_image_url=pic_url,
									title=store.name,
									text='評分以及訂閱店家',
									# text="aaaa",
									actions=[
										URITemplateAction(
												label='評分以及訂閱店家',
												uri='https://liff.line.me/1657551781-DOprpXyb?order_id={}'.format(order.id)
											)
										]
									)
								message = TemplateSendMessage(
										alt_text='評分以及訂閱店家',
										template=CarouselTemplate(
										columns=[text]
									)
								)
								line_bot_api.push_message(uid,message)
							else:
								response['message'] = '顧客已經取餐過了'
						else:
							response['message'] = '顧客尚未付款,不能更改取餐狀態'
					# print(response)
					return JsonResponse(response)

				else:
					return JsonResponse({'message':'店家不正確'})
			else:
				return JsonResponse({'message':'訂單不存在'})
		else:
			return JsonResponse({'message':'店家不存在'})

		return render(request,'detail_order.html',locals())

	return render(request,'detail_order.html',locals())
@csrf_exempt
def change_description(request):
	print(request.GET)
	print('-----------------------')
	if 'order_id' in request.GET:
			order_id = request.GET['order_id']
			if models.Order.objects.filter(id=order_id):
				order = models.Order.objects.filter(id=order_id)[0]
			else:
				return HttpResponse('該訂單不存在')

	if request.is_ajax():
		print(request.POST)
		data = json.loads(request.POST.get('data'))	
		type_ = data[0]['type']
		order_id = data[0]['order_id']
		if type_ =='change':
			description = data[0]['description']
			order = models.Order.objects.filter(id=order_id)[0]
			order.description = description
			order.save()
			return JsonResponse({'message':'修改備註成功'})
		else:
			uid_store = data[0]['uid_store']
			if models.Store.objects.filter(uid=uid_store):         
				store = models.Store.objects.filter(uid=uid_store)[0]
				order = models.Order.objects.filter(id=order_id)[0]
				if order.store == store:
					response = {}
					response['description'] = order.description
					response['message'] = '成功'
					return JsonResponse(response)
				else:
					return JsonResponse({'message':'店家不正確'})
			else:
				return JsonResponse({'message':'你必須是商家才可以執行此操作'})   
	return render(request,'change_description.html',locals())

@csrf_exempt
def user_get_store_food(request):
	print(request.GET)
	print('-----------------------')
	if 'store_id' in request.GET:
		uid_store = request.GET['store_id']

		if models.Store.objects.filter(uid=uid_store):
			store = models.Store.objects.filter(uid=uid_store)[0]
			if models.Store_food.objects.filter(store=store).filter(online=True):
				store_food = models.Store_food.objects.filter(store=store).filter(online=True)[0]
				print(store_food)
			else:
				return HttpResponse('該剩食不存在')
		else:
			return HttpResponse('該店家不存在')

	if request.is_ajax():
		data = json.loads(request.POST.get('data'))
		uid = data[0]['uid']
		number = data[0]['number']
		uid_store = data[0]['uid_store']
		# if uid != uid_store:
		if models.Store.objects.filter(uid=uid_store):         
			store = models.Store.objects.filter(uid=uid_store)[0]
			if uid != '':
				if models.Store_food.objects.filter(store=store).filter(online=True):           
					if models.User.objects.filter(uid=uid):
						user = models.User.objects.filter(uid=uid)[0]
						store_food = models.Store_food.objects.filter(store=store).filter(online=True)[0]
						print(store_food)
						if int(number) <=  store_food.number:
							if models.Order.objects.filter(user=user).filter(user_now=True):
								messages.add_message(request,messages.SUCCESS,"一人只能有一份訂單")
							else:        
								order = models.Order.objects.create(user=user,store=store,store_food=store_food,number=number)
								messages.add_message(request,messages.SUCCESS,"下訂成功")

								webhook = line_bot_api.get_webhook_endpoint()
								webhook_url = webhook.endpoint
								pic_url = webhook_url+'/media/image/official_image/01.png'
								url_ ='https://liff.line.me/1657551781-GpqEqJPY?order_id={}'.format(order.id)
								print(url_)
								text = CarouselColumn(
									thumbnail_image_url=pic_url,
									title='新的顧客訂單,訂單編號:{}'.format(order.id),
									text='前往查看顧客訂單',
									# text="aaaa",
									actions=[
										URITemplateAction(
												label='查看顧客訂單',
												uri='https://liff.line.me/1657551781-GpqEqJPY?order_id={}'.format(order.id)
											)
										]
									)
								message = TemplateSendMessage(
										alt_text='新的顧客訂單',
										template=CarouselTemplate(
										columns=[text]
									)
								)
								line_bot_api.push_message(store.uid,message)
						else:
							messages.add_message(request,messages.WARNING,"不能超過指定數量")
					else:
						messages.add_message(request,messages.WARNING,"找不到使用者")
				else:
					return HttpResponse('該剩食訂單不存在')
			else:
				messages.add_message(request,messages.WARNING,"請確認是從line端登入")
		else:
			return HttpResponse('該店家不存在')
		# else:
		# 	messages.add_message(request,messages.WARNING,"你不能訂購自己店家的剩食委託")
			


	return render(request,'user_get_store_food.html',locals())
@csrf_exempt
def user_check_order(request):
	print(request.POST)
	if request.is_ajax():
		data = json.loads(request.POST.get('data'))
		uid = data[0]['uid']
		response_data = {}
		if models.User.objects.filter(uid=uid):
			user = models.User.objects.filter(uid=uid)[0]
			if models.Order.objects.filter(user=user):
					response = {}
					
					if models.Order.objects.filter(user=user).filter(user_now=True):
						order_now = models.Order.objects.filter(user=user).filter(user_now=True)[0]
						data = order_now.json()
						response['now'] = data

					orders_all = models.Order.objects.filter(user=user)
					data_all = [i.json() for i in orders_all]
					response['all'] = data_all
					response ['message']='成功'
					# print(response)
					# print(json.dumps(response)) #str
					return HttpResponse(json.dumps(response), content_type="application/json")
			else:
				response_data['message']= '沒有下訂的紀錄'
				return JsonResponse(response_data)

		else:
			response_data['message']= '用戶不存在'
			return JsonResponse(response_data)

	return render(request,'user_check_order.html',locals())
@csrf_exempt
def user_pay(request):

	if request.is_ajax():
		print(request.POST)
		data = json.loads(request.POST.get('data'))	
		uid = data[0]['uid']
		type_ = data[0]['type']
		if type_ =='get_uid':
			if models.User.objects.filter(uid=uid):
				user = models.User.objects.filter(uid=uid)[0]
				if models.Order.objects.filter(user=user).filter(user_now=True):
					if models.Order.objects.filter(user=user).filter(user_now=True).filter(check=True):
						order = models.Order.objects.filter(user=user).filter(user_now=True).filter(check=True)[0]
						return JsonResponse({'message':'成功','uid':uid,'price':order.store_food.price})
					else:
						return JsonResponse({'message':'此訂單尚未被確認,不能付款','uid':uid})
				else:
					return JsonResponse({'message':'該使用者現在沒有訂單','uid':uid})
			else:
				return JsonResponse({'message':'無此使用者'})
		elif type_=='pay':
			if models.User.objects.filter(uid=uid):
				user = models.User.objects.filter(uid=uid)[0]
				if models.Order.objects.filter(user=user).filter(user_now=True):
					order = models.Order.objects.filter(user=user).filter(user_now=True)[0]
					if order.paid == False:
						order.paid = True
						length_of_string = 8
						certificate = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string))
						order.certificate = certificate
						order.save()
						return JsonResponse({'message':'付款成功','uid':uid})
					else:
						return JsonResponse({'message':'已經付過款'})
					
				else:
					return JsonResponse({'message':'該使用者現在沒有訂單','uid':uid})
			else:
				return JsonResponse({'message':'無此使用者'})
		elif type_ == 'subscribe':
			pass
		elif type_ == 'score':
			pass

	return render(request,'user_pay.html',locals())
@csrf_exempt
def rating(request):

	print(request.GET)
	print('-----------------------')
	if 'order_id' in request.GET:
		order_id = request.GET['order_id']
		print(order_id)
		if models.Order.objects.filter(id=order_id).filter(paid=True).filter(user_get=True):
			order = models.Order.objects.filter(id=order_id)[0]
		else:
			return HttpResponse('該訂單不存在,無法評論')


	if request.is_ajax():
		print(request.POST)
		data = json.loads(request.POST.get('data'))	
		uid = data[0]['uid']
		type_ = data[0]['type']
		order_id = data[0]['order_id']
		if type_ =='get_uid':
			if models.User.objects.filter(uid=uid):
				user = models.User.objects.filter(uid=uid)[0]
				if models.Order.objects.filter(id=order_id):
					order_user = models.Order.objects.filter(id=order_id)[0].user
					if order_user == user:
						if models.Order.objects.filter(id=order_id).filter(paid=True).filter(user_get=True):
							order = models.Order.objects.filter(id=order_id).filter(paid=True).filter(user_get=True)[0]
							if user.subscribe.filter(id=order.store.id):
								return JsonResponse({'message':'成功','uid':uid,'name':order.store.name,'subscribe':'yes'})
							else:
								return JsonResponse({'message':'成功','uid':uid,'name':order.store.name,'subscribe':'no'})
						else:
							return JsonResponse({'message':'需付款且成功取貨才可以評分','uid':uid,'order_id':order.id})
					else:
						return JsonResponse({'message':'需是該名顧客才可以評分才可以評分','uid':uid,'order_id':order.id})
			else:
				return JsonResponse({'message':'無此使用者'})
		elif type_=='rating':
			score = data[0]['score']
			if models.User.objects.filter(uid=uid):
				user = models.User.objects.filter(uid=uid)[0]
				if models.Order.objects.filter(id=order_id).filter(paid=True).filter(user_get=True):
					order = models.Order.objects.filter(id=order_id).filter(paid=True).filter(user_get=True)[0]
					if order.user == user:
						order.value = int(score)
						print(order.value)
						order.save()
						return JsonResponse({'message':'成功評分','uid':uid,'order_id':order.id})
					else:
						return JsonResponse({'message':'只有該訂單的使用者才能評分','uid':uid,'order_id':order.id})
				else:
					return JsonResponse({'message':'需付款且成功取貨才可以評分','uid':uid,'order_id':order.id})
			else:
				return JsonResponse({'message':'無此使用者','order_id':order.id})
		elif type_ == 'subscribe':
			subscribe_status = data[0]['subscribe_status']
			if models.User.objects.filter(uid=uid):
				user = models.User.objects.filter(uid=uid)[0]
				if models.Order.objects.filter(id=order_id).filter(paid=True).filter(user_get=True):
					order = models.Order.objects.filter(id=order_id).filter(paid=True).filter(user_get=True)[0]
					if order.user == user:
						store = order.store
						if subscribe_status =='no':
							user.subscribe.add(store)
							user.save()
							print('user_subscirbe:',end='')
							print(user.subscribe.all())
							return JsonResponse({'message':'成功訂閱'})
						else:
							user.subscribe.remove(store)
							user.save()
							print('user_subscirbe:',end='')
							print(user.subscribe.all())
							return JsonResponse({'message':'成功取消訂閱'})
					else:
						return JsonResponse({'message':'只有該訂單的使用者才能訂閱','uid':uid,'order_id':order.id})
				else:
					return JsonResponse({'message':'需付款且成功取貨才可以訂閱','uid':uid,'order_id':order.id})
			else:
				return JsonResponse({'message':'無此使用者','order_id':order.id})
		

	return render(request,'rating.html',locals())
@csrf_exempt
def subscribe_check(request):
	if request.is_ajax():
		print(request.POST)
		data = json.loads(request.POST.get('data'))	
		uid = data[0]['uid']
		type_ = data[0]['type']
		if type_ =='get_uid':
			if models.User.objects.filter(uid=uid):
				user = models.User.objects.filter(uid=uid)[0]
				subscribe_store = user.subscribe.all()
				data_all = [i.json() for i in subscribe_store]
				print(subscribe_store)
				return JsonResponse({'message':'成功','subscribe_store':data_all})
			else:
				return JsonResponse({'message':'無此使用者'})
		elif type_=='alter_subscribe':
			stores_id = data[0]['stores_id']
			if models.User.objects.filter(uid=uid):
				user = models.User.objects.filter(uid=uid)[0]
				user.subscribe.clear()
				for store_id in stores_id:
					subscribe_store = models.Store.objects.get(id=store_id)
					user.subscribe.add(subscribe_store)
				print(user.subscribe.all())
				return JsonResponse({'message':'成功'})
			else:
				return JsonResponse({'message':'無此使用者'})

	return render(request,'subscribe_check.html',locals())

def test(request):
	return render(request,'test.html',locals())

def select_food_button(event):
	webhook = line_bot_api.get_webhook_endpoint()
	webhook_url = webhook.endpoint
	pic_url = webhook_url+'/media/image/official_image/01.png'
	print(pic_url)
	store_food =models.Store_food.objects.filter(online=True)
	store_food = [food for food in store_food if food.number>0]
	stores  = []
	categories = set()
	categories_action = []
	categories_action.append(
			PostbackTemplateAction(  #執行Postback功能,觸發Postback事件
					label='所有剩食',  #按鈕文字
					#text='@購買披薩',  #顯示文字訊息
					data='action=all_food'  #Postback資料
				)
		)
	for i in range(len(store_food)):
		stores.append(store_food[i].store)
		categories.add(stores[i].category)
	
	categories = list(categories)
	for i in range(len(categories)):
		if categories[i] == 'bread':
			label_ = '麵包'
		elif categories[i] == 'bento':
			label_ = '便當'
		categories_action.append(
			PostbackTemplateAction(  #執行Postback功能,觸發Postback事件
					label=label_,  #按鈕文字
					#text='@購買披薩',  #顯示文字訊息
					data='action={}'.format(categories[i])  #Postback資料
				)
			)
	message = TemplateSendMessage(
		alt_text='選擇食物種類',
		template=ButtonsTemplate(
		thumbnail_image_url=pic_url,  #顯示的圖片
		title='食物種類',  #主標題
		text='選擇食物種類：',  #副標題
			actions=categories_action
		)
	)
	line_bot_api.reply_message(event.reply_token, message)

def search_food(event,category):
	# try:
	food_list = []
	
	store_food =models.Store_food.objects.filter(online=True)
	store_food = [food for food in store_food if food.number>0]
	if store_food:			
		if category == 'all_food':
			store_food_category = store_food
		else:
			store_food_category = []
			for i in range(len(store_food)):
				if store_food[i].store.category == category:
					store_food_category.append(store_food[i])

		webhook = line_bot_api.get_webhook_endpoint()
		webhook_url = webhook.endpoint
		for i in range(len(store_food_category)):
			pic_url = webhook_url+store_food_category[i].image.url
			orders= models.Order.objects.filter(store_food = store_food_category[i])
			print(orders)
			if orders:
				order_value_list = []
				for order in orders:
					if order.value!=None:
						order_value_list.append(order.value)
				if len(order_value_list)>0:
					order_avg_value = sum(order_value_list)/len(order_value_list)
					order_avg_value = str(round(order_avg_value,1))
				else:
					order_avg_value = '尚未有評分'
			else:
				order_avg_value = '尚未有評分'
			food_list.append(
						{
							"type": "bubble",
							"hero": {
								"type": "image",
								"size": "full",
								"aspectRatio": "20:13",
								"aspectMode": "cover",
								"url": pic_url
							},
							"body": {
								"type": "box",
								"layout": "vertical",
								"spacing": "sm",
								"contents": [
									{
										"type": "text",
										"text": store_food_category[i].store.name,
										"wrap": True,
										"weight": "bold",
										"size": "xl"
									},
									{
										"type": "box",
										"layout": "baseline",
										"contents": [
											{
												"type": "text",
												"text": "$",
												"wrap": True,
												"weight": "bold",
												"size": "xl",
												"flex": 0,
												"contents": []
											},
											{
												"type": "text",
												"text": str(store_food_category[i].price),
												"wrap": True,
												"weight": "bold",
												"size": "xl",
												"flex": 0
											}
										]
									},
									{
										"type": "text",
										"text": "份數:"+str(store_food_category[i].number)
									},
									{
										"type": "text",
										"text": "地址:"+store_food_category[i].store.address
									},
									{
										"type": "text",
										"text": "店家評分:"+order_avg_value
									},
									{
										"type": "text",
										"text": "電話:"+store_food_category[i].store.tel
									}
								]
							},
							"footer": {
								"type": "box",
								"layout": "vertical",
								"spacing": "sm",
								"contents": [
									{
										"type": "button",
										"style": "primary",
										"action": {
											"type": "uri",
											"label": "立即下訂",
											"uri": "https://liff.line.me/1657551781-mq1D1gLa?store_id={}".format(store_food_category[i].store.uid)
										}
									}
								]
							}
						}
		
					)
		flex_message = {
					"type": "carousel",
					"contents": food_list   
					}
		message = FlexSendMessage(alt_text='附近剩食店家',contents=flex_message)
		line_bot_api.reply_message(event.reply_token,message)

	else:
		message = TextSendMessage(text='現在沒有剩食')
		line_bot_api.reply_message(event.reply_token,message)
	# except:
	# 	line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

# def switch_store(backdata):
# 	headers = {'Authorization':'Bearer ZCXsmz2iYE0Sysbtdp+I+epGG3B7IZv4pjMzL0J85kGD0hUkDfEsirD0xyOYq8dRw62Qnf0Go5ZtbHVylSuTdRl39IzXGRitXezmD4EZ9c2+ejb0EDU4q+o/l3tDzeVaFWNjSdmlT/qRonep/JBCQgdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}
# 	req = requests.request('GET', 'https://api.line.me/v2/bot/richmenu/alias/list',
#                 headers=headers,data=json.dumps(body).encode('utf-8'))
# 	#json.load(req.text).aliases[0].richMenuId
# 	richMenuId = json.loads(req.text)['aliases'][0]['richMenuId']
# 	req = requests.request('POST','https://api.line.me/v2/bot/user/{}/richmenu/{}',headers=headers).format()
# 	print(req.text)

# def switch_user(backdata):
