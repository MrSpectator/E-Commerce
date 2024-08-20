from django.contrib import admin

from .models import *

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "start_bid", "date", "category", "creator")

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)