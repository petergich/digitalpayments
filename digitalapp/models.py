from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class seller(models.Model):
    buss_name=models.CharField(max_length=254,primary_key=True)
    email=models.CharField(max_length=254,null=True)
    buss_shortcode=models.CharField(max_length=254,null=True)
    password=models.CharField(max_length=254)
    consumer_key=models.CharField(max_length=254,null=True)
    secret_key=models.CharField(max_length=254,unique=True)
    passkey=models.CharField(max_length=400,default="none")
    def __str__ (self):
        return self.buss_name
class customer(models.Model):
    username=models.CharField(max_length=254,unique=True)
    f_name=models.CharField(max_length=254)
    l_name=models.CharField(max_length=254)
    password=models.CharField(max_length=254)
    card_no=models.CharField(max_length=254,null=True)
    expiry=models.CharField(max_length=254,null=True)
    cvc=models.CharField(max_length=254,null=True)
    def __str__ (self):
        return self.name
class transaction(models.Model):
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    amount=models.IntegerField(default=0)
    time=models.DateTimeField(default=timezone.now)
    def __str__ (self):
        return self.seller.buss_name+str(self.amount)
# Create your models here.
