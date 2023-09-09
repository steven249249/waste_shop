from django.db import models
from django.utils import timezone
from datetime import datetime, timezone, timedelta
# Create your models here.
import pytz


class Store(models.Model):
	class Food_Choice(models.TextChoices):
		bread = 'bread','麵包'
		bento = 'bento','便當'

	uid = models.CharField(max_length=255,null=True)
	name = models.CharField(max_length=255,null=True)
	address = models.CharField(max_length=255,null=True)
	tel = models.CharField(max_length=255,null=True)
	category = models.CharField(max_length=255,choices=Food_Choice.choices,default=Food_Choice.bread)
	def __str__(self):
		return self.name

	def json(self):	
		return {
			'name':self.name,
			'id':self.id
		}
class User(models.Model):
	uid = models.CharField(max_length=255,null=True)
	name = models.CharField(max_length=255,null=True)
	tel = models.CharField(max_length=255,null=True)
	point = models.PositiveIntegerField(default=0,null=True)
	subscribe = models.ManyToManyField(Store)

	def __str__(self):
		return self.name

class Gift(models.Model):
	price = models.PositiveIntegerField(default=0)
	number = models.PositiveIntegerField(default=0)
	name = models.CharField(max_length=255,null=True,default='')
	image = models.ImageField(upload_to='image/', blank=True, null=True)
	
	def __str__(self):
		return self.name

class Store_food(models.Model):
	image = models.ImageField(upload_to='image/', blank=True, null=True)
	store = models.ForeignKey(Store,on_delete=models.CASCADE,null=True)
	price = models.PositiveIntegerField(null=True)
	number = models.PositiveIntegerField(null=True)
	online = models.BooleanField(null=True,default=True)
	start_time = models.DateTimeField(auto_now_add=True)
	end_order_time = models.DateTimeField(null=True)
	end_get_time = models.DateTimeField(null=True)

	def __str__(self):
		return self.store.name+str(self.id)

	def json(self):
		return {
			'id':self.id,
			'image':self.image.url,
			'online':self.online,
			'price':self.price,
			'number': self.number,
			'store': self.store.name,
		}
class Order(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
	store = models.ForeignKey(Store,on_delete=models.CASCADE,null=True)
	store_food = models.ForeignKey(Store_food,on_delete=models.CASCADE,null=True)
	number = models.PositiveIntegerField(null=True)
	check = models.BooleanField(default = False,blank=True)
	order_time = models.DateTimeField(auto_now_add=True)
	description = models.CharField(max_length=255,null=True,default='',blank=True)
	user_now = models.BooleanField(default=True,blank=True)
	paid = models.BooleanField(default=False,null=True)
	user_get = models.BooleanField(default=False,null=True,blank=True)
	value = models.PositiveIntegerField(null=True,blank=True)
	certificate = models.CharField(default='',null=True,max_length=255,blank=True)
	def __str__(self):
		return '{}-{}-{}'.format(self.user,str(self.number),self.store)

	def json(self):
		# tw = pytz.timezone('Asia/Taipei')
		# time_ = self.time.astimezone(timezone(timedelta(hours=8)))
		time_ = self.order_time.strftime('%Y-%m-%d %H:%M:%S')
		
		return {
			'order_id':self.id,
			'address':self.store.address,
			'image':self.store_food.image.url,
			'user': self.user.name,
			'store': self.store.name,
			'store_id':self.store.uid,
			'store_food': self.store_food.id,
			'number':self.number,
			'check':self.check,
			'time':time_,
			'user_tel':self.user.tel,
			'store_tel':self.store.tel,
			'price':self.store_food.price,
			'description':self.description,
			'paid':self.paid,
			'certificate':self.certificate,
			'user_get':self.user_get
		}