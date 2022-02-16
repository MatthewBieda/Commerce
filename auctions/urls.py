from django.urls import path

from . import views
from .views import Active_Listings, Create_Listing

urlpatterns = [
    path("", views.Active_Listings, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", Create_Listing.as_view(), name="newlisting"),
    path("<int:pk>", views.checklisting, name="checklisting"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<category>", views.category, name="category")
]
