from django.contrib import admin

from .models import User, Bids, Comments, Auction_Listings, AbstractUser

#register models here
admin.site.register(User)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Auction_Listings)
