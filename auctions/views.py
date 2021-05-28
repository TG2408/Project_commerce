from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import fields
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Watchlater

from django import forms
import urllib.request,os
from django.contrib.auth.decorators import login_required



def index(request):
    return render(request, "auctions/index.html",{
        "listing" : Listing.objects.all()
    })



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


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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


class newform(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'discription', 'price', 'category', 'imagelink', 'active']

# Create new listing
@login_required(login_url='http://127.0.0.1:8000/login')
def new_listing(request):
    current_user = request.user
    
    if request.method == "POST":
        form = newform(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            discription = form.cleaned_data['discription']
            price = form.cleaned_data['price']
            category = form.cleaned_data['category']
            imagelink = form.cleaned_data['imagelink']
            active = form.cleaned_data['active']
                        
            imagename = f"{title}.jpg"

            new_listing = Listing(title = title, discription = discription, price = price, category = category, imagename= imagename, imagelink = imagelink, active =active, masteruser = current_user.username,)
            new_listing.save()
            
            Bid(username = current_user.username, bid = price , bids_listing = new_listing ).save()

            if imagelink is not None:
                # Downloading image in static folder of auctions

                # Seting path for image download
                fullfilename = os.path.join("auctions/static/auctions", imagename)  
                 # Downloading image at above path
                urllib.request.urlretrieve(imagelink ,fullfilename)         
            
            return render(request, "auctions/index.html",{
                "listing" : Listing.objects.all()
            })
        else:
            return HttpResponse("Form not valid")

    else:
        return render(request, "auctions/new_listing.html", {
            "form" : newform()
        })

# Listing page defination
@login_required(login_url='/login')
def listing_page(request, name):
    if request.method == "POST":
        current_user = request.user # asking current user
        
        latest_comment = request.POST["latest_comment"]
        latest_bid = request.POST["latest_bid"]
        listing = Listing.objects.get(pk = name)
        
        Bid(username = current_user, bid = latest_bid, bids_listing = listing ).save()
        
        if latest_comment is not None:
            Comment(username = current_user,comment = latest_comment ,comment_listing = listing).save()

        listing_bid = listing.relate_bid.all().last()
        make_bid = listing_bid.bid + 1
    
        listing_watchlater = listing.relate_watchlater.filter(username = current_user)

        return render(request, "auctions/listing.html", {
            "listing" : listing ,
            "listing_comments" : listing.relate_comments.all()  ,
            "listing_bid" : listing_bid ,
            "make_bid" : make_bid ,
            "user_comments" : Comment.objects.all(),
            "listingwatchlater" : listing_watchlater
        }) 

    else :
        current_user = request.user
        listing = Listing.objects.get(pk = name)
        listing_bid = listing.relate_bid.all().last()
        make_bid = listing_bid.bid + 1

        listing_watchlater = listing.relate_watchlater.filter(username = current_user)

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
        
        listing_detail = request.POST["listing_detail"]
        
        temp = listing_detail.relate_watchlater.filter(username = current_user)
        if temp is not None:
            temp.delete()
        else:
            Watchlater(username = current_user, watchlater_listing = listing_detail)

    else:
        current_user = request.user
        watchlater_list = Watchlater.objects.filter(username = current_user)
        
        l = []
        for list in watchlater_list:
            l.append(list.watchlater_listing)

        return render(request, "auctions/index.html",{
            "listing" : l 
        })