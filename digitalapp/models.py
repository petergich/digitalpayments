from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class seller(models.Model):
    buss_name=models.CharField(max_length=254,primary_key=True)
    phone_number=models.CharField(max_length=254,null=True)
    registration_number=models.CharField(max_length=254,null=True)
    email=models.CharField(max_length=254,null=True)
    buss_shortcode=models.CharField(max_length=254,null=True)
    password=models.CharField(max_length=254)
    consumer_key=models.CharField(max_length=254,null=True)
    secret_key=models.CharField(max_length=254,null=True)
    passkey=models.CharField(max_length=400,null=True)
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
        return self.username
class transactionsRecord(models.Model):
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    amount=models.IntegerField(default=0)
    time=models.DateTimeField(default=timezone.now)
class registration_request(models.Model):
    seller=models.ForeignKey(seller,on_delete=models.CASCADE)
    date=models.DateField(default=timezone.now)
    status=models.BooleanField(default=False)
    def __str__ (self):
        return self.seller
# Create your models here.
