from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.shortcuts import reverse
import string
import random


class Support(models.Model):
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    message = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    company = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    postalcode = models.CharField(max_length=30, null=True)
    bio = models.TextField(max_length=500, null=True)
    def __str__(self):
        return f'{self.user.username}'
              
class Commodity(models.Model):
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(null=True)
    img = models.ImageField(upload_to='pics', blank=True)
    icon = models.ImageField(upload_to='pics',blank=True)
    commodity_type = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=700, null=True)
    wholesaleprice = models.CharField(max_length=200, null=True)
    farmprice = models.CharField(max_length=200, null=True)
    marketprice = models.CharField(max_length=200, null=True)
    date = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("commodity_info", kwargs={
            'slug':self.slug
        })

class Farmer(models.Model):
    no = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    commodity = models.CharField(max_length=200, null=True)
    commoditytype = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)


    def __str__(self):
        return self.name


class Farmer(models.Model):
    no = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    commodity = models.CharField(max_length=200, null=True)
    commoditytype = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)


    def __str__(self):
        return self.name


   





 

















    