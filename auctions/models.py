from typing import ByteString
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

categories= (
    ("Fashion","Fashion"),
    ("Toys","Toys"),
    ("Electronics","Electronics"),
    ("Books","Books"),
)

class Listing(models.Model):
    title = models.CharField(max_length=64 ,primary_key=True)
    discription = models.TextField()
    price = models.IntegerField(default=0)
    category = models.CharField(choices=categories, default="All", max_length=100, blank=True)
    imagename = models.CharField(max_length=200, blank = True)
    imagelink = models.URLField(max_length=250, blank=True)
    active = models.BooleanField(default=False)
    masteruser = models.CharField(max_length=100, blank=True) 


class Bid(models.Model):
    username = models.CharField(max_length=100, blank=True)
    bid = models.IntegerField(default=0)
    bids_listing = models.ForeignKey(Listing,on_delete=models.CASCADE, related_name="relate_bid")
    
    
class Comment(models.Model):
    username = models.CharField(max_length=100, blank=True)
    comment = models.CharField(max_length=200 ,default=None , blank=True)
    comment_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="relate_comments")


