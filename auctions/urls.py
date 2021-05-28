from os import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing_page/<str:name>", views.listing_page, name = "listing_page"),
    path("closed_listing/<str:name>", views.closed_listing, name = "closed_listing"),
    path("categories", views.categories, name = "categories"),
    path("watchlater", views.watchlater, name = "watchlater"),
]
