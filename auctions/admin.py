from django.contrib import admin

# Register your models here.

from .models import Listing, Bid, Comment, User

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)