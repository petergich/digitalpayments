from django.db import models


class seller(models.Model):
    buss_name=models.CharField(max_length=254,primary_key=True)
    buss_shortcode=models.CharField(max_length=254)
    password=models.CharField(max_length=254)
    consumer_key=models.CharField(max_length=254,null=True)
    secret_key=models.CharField(max_length=254,unique=True)
    passkey=models.CharField(max_length=400,default="none")
    def __str__ (self):
        return self.buss_name
class customer(models.Model):
    name=models.CharField(max_length=254,primary_key=True)
    password=models.CharField(max_length=254)
    balance=models.IntegerField(default=0)
    def __str__ (self):
        return self.name
# Create your models here.
