from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import fields
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import urllib.request,os
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Watchlater


# Index page definations
def index(request):
    return render(request, "auctions/index.html",{
        "listing" : Listing.objects.all()
    })


# Login page definations
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


# User Logout Definations
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# User registration definations
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# Defining django form(dynamic) directly using Listing Model
class newform(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'discription', 'price', 'category', 'imagelink', 'active']


# Create new listing
@login_required(login_url='http://127.0.0.1:8000/login')  # Making Login necessary for using this defination
def new_listing(request):
    current_user = request.user                           # requesting for current loginned user 
    
    if request.method == "POST":
        form = newform(request.POST)                      # Requesting for form data
        if form.is_valid():
            title = form.cleaned_data['title']
            discription = form.cleaned_data['discription']
            price = form.cleaned_data['price']
            category = form.cleaned_data['category']
            imagelink = form.cleaned_data['imagelink']
            active = form.cleaned_data['active']
                        
            imagename = f"{title}.jpg"

            # making object or storing data in Listing model
            new_listing = Listing(title = title, discription = discription, price = price, current_bid = price, category = category, imagename= imagename, imagelink = imagelink, active =active, masteruser = current_user.username)
            new_listing.save()
            
            # making object or storing data in Bid model
            Bid(username = current_user.username, bid = price , bids_listing = new_listing ).save()

            if imagelink is not None:                                                    # Downloading image in static folder of auctions
                fullfilename = os.path.join("auctions/static/auctions", imagename)       # Seting path for image download  
                urllib.request.urlretrieve(imagelink ,fullfilename)                      # Downloading image at above path
            
            return render(request, "auctions/index.html",{
                "listing" : Listing.objects.all()
            })
        else:
            return HttpResponse("Form not valid")

    else:
        return render(request, "auctions/new_listing.html", {
            "form" : newform()                                        # sending newform to create_listing.html
        })

# Listing page defination
@login_required(login_url='/login')
def listing_page(request, name):
    if request.method == "POST":
        current_user = request.user
        
        latest_comment = request.POST["latest_comment"]
        latest_bid = request.POST["latest_bid"]
        listing = Listing.objects.get(pk = name)
        listing.current_bid = latest_bid
        listing.save()
        
        Bid(username = current_user.username, bid = latest_bid, bids_listing = listing ).save()
        
        if latest_comment != "":
            Comment(username = current_user.username,comment = latest_comment ,comment_listing = listing).save()

        listing_bid = listing.relate_bid.all().last()
        make_bid = listing_bid.bid + 1
    
        listing_watchlater = listing.relate_watchlater.filter(username = current_user.username)

        return render(request, "auctions/listing.html", {
            "listing" : listing ,
            "listing_comments" : listing.relate_comments.all()  ,
            "listing_bid" : listing_bid ,
            "make_bid" : make_bid ,
            "user_comments" : Comment.objects.all(),
            "listingwatchlater" : listing_watchlater
        }) 

    else :
        a= "isha"
        b= "isha"
        current_user = request.user
        listing = Listing.objects.get(pk = name)
        listing_bid = listing.relate_bid.all().last()
        make_bid = listing_bid.bid + 1

        listing_watchlater = listing.relate_watchlater.filter(username = current_user.username)

        if listing.active == False:
            if current_user.username == listing_bid.username:
                return render(request, "auctions/listing.html", {
                    "listing" : listing,
                    "listing_bid" : listing_bid       
                })
            else:
                return HttpResponse(f"%{listing_bid.username}% or %{current_user.username}% won this")
                
        else:
            return render(request, "auctions/listing.html", {
                "listing" : listing ,
                "listing_comments" : listing.relate_comments.all()  ,
                "listing_bid" : listing_bid ,
                "make_bid" : make_bid ,
                "user_comments" : Comment.objects.all(),
                "listingwatchlater" : listing_watchlater
            })


#Close Listing
def closed_listing(request, name):
    close_listing = Listing.objects.get(pk = name)
    close_listing.active = False
    close_listing.save()
    return render(request, "auctions/index.html", {
        "listing" : Listing.objects.all()
    })
    

# Listing based on categories
@login_required(login_url='/login')
def categories(request):
    if request.method == "POST":
        category = request.POST["category"]
        return render(request, "auctions/index.html",{
        "listing" : Listing.objects.filter(category = category)
        })
    else : 
        return render(request, "auctions/categories.html")


# Watchlater of each user
@login_required(login_url='/login')
def watchlater(request):
    if request.method == "POST":
        current_user = request.user
        
        listing_title = request.POST["listing_title"]
        
        listing_detail = Listing.objects.get(title = listing_title)

        temp = listing_detail.relate_watchlater.filter(username = current_user.username).first()

        if temp is not None:
            temp.delete()
            listing_bid = listing_detail.relate_bid.all().last()
            make_bid = listing_bid.bid + 1
            listing_watchlater = listing_detail.relate_watchlater.filter(username = current_user.username)
            return render(request, "auctions/listing.html", {
                "listing" : listing_detail ,
                "listing_comments" : listing_detail.relate_comments.all()  ,
                "listing_bid" : listing_bid ,
                "make_bid" : make_bid ,
                "listingwatchlater" : listing_watchlater,
                "user_comments" : Comment.objects.all(),                
            })
        else:
            Watchlater(username = current_user.username, watchlater_listing = listing_detail).save()
            listing_bid = listing_detail.relate_bid.all().last()
            make_bid = listing_bid.bid + 1
            listing_watchlater = listing_detail.relate_watchlater.filter(username = current_user.username)
            return render(request, "auctions/listing.html", {
                "listing" : listing_detail ,
                "listing_comments" : listing_detail.relate_comments.all()  ,
                "listing_bid" : listing_bid ,
                "make_bid" : make_bid ,
                "listingwatchlater" : listing_watchlater,
                "user_comments" : Comment.objects.all(),                
            })
       
    else:
        current_user = request.user
        watchlater_list = Watchlater.objects.filter(username = current_user.username)
        
        l = []
        for list in watchlater_list:
            l.append(list.watchlater_listing)

        return render(request, "auctions/index.html",{
            "listing" : l 
        })