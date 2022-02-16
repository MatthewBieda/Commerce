from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.db.models import Max
from django.core.paginator import Paginator
from django.contrib import messages

import auctions

from .forms import BidsForm, CommentsForm, PostForm
from .models import Auction_Listings, Bids, Comments, User, Watchlist


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

# Display all listings


def Active_Listings(request):

    # Obtain the current maximum bid for each auction from the database
    auction_objects = Auction_Listings.objects.all()
    current_max_bid = []
    for auction in auction_objects:
        current_max_bid.append(
            ((auction.bids_set.filter().aggregate(Max('current_bid')))))

    # Convert from a list of dictionaries into a list
    top_bids = [d['current_bid__max'] for d in current_max_bid]

    # Use Python's zip function to map each auction to it's maximum bid
    x = (zip(auction_objects, top_bids))
    data = (tuple(x))

    page_num = request.GET.get('page')
    data_paginator = Paginator(data, 8)
    page = data_paginator.get_page(page_num)

    # Pass this data into Django's context
    context = {
        'page': page
    }

    return render(request, "index.html", context)


class Create_Listing(CreateView):
    model = Auction_Listings
    form_class = PostForm
    template_name = 'newlisting.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def checklisting(request, pk):

    user = request.user

    # Get this auction object using the primary key
    auction_listing = Auction_Listings.objects.get(id=pk)

    # Obtain the current maximum bid for the auction from the database
    current_max_bid = auction_listing.bids_set.filter().aggregate(
        Max('current_bid'))["current_bid__max"]

    if current_max_bid == None:
        current_max_bid = auction_listing.starting_bid

    # Get all current comments for this auction
    comment = Comments.objects.filter(auction_id=pk)

    # Process forms
    if request.method == 'POST':
        if 'save_comment' in request.POST:
            commentsform = CommentsForm(request.POST)
            if commentsform.is_valid():
                commentdraftform = commentsform.save(commit=False)
                print(commentdraftform.comment)
                if len(commentdraftform.comment) == 0:
                    messages.error(
                        request, "Please don't enter blank comments!")
                    return HttpResponseRedirect(request.path_info)
                commentdraftform.user = request.user
                commentdraftform.auction = auction_listing
                commentdraftform.save()
                return HttpResponseRedirect(request.path_info)
        if 'save_bid' in request.POST:
            bidsform = BidsForm(request.POST)
            if bidsform.is_valid():
                biddraftform = bidsform.save(commit=False)
                if biddraftform.current_bid is None:
                    messages.error(request, "Please enter a bid.")
                    return HttpResponseRedirect(request.path_info)
                if biddraftform.current_bid < current_max_bid:
                    messages.error(request, "Your bid was too low.")
                    return HttpResponseRedirect(request.path_info)
                biddraftform.user = request.user
                biddraftform.auction = auction_listing
                biddraftform.save()
                return HttpResponseRedirect(request.path_info)

    if request.method == 'GET':
        commentsform = CommentsForm()
        bidsform = BidsForm()

    # Handling close listing event
    if(request.GET.get('closelisting')):
        auction_listing.is_active = False
        auction_listing.save()
        return HttpResponseRedirect(reverse('index'))

    # Handling add to watchlist event with duplicate checking
    if(request.GET.get('addwatchlist')):
        try:
            foo = Watchlist()
            foo.user = request.user
            foo.auction = auction_listing
            foo.save()
            return HttpResponseRedirect(reverse('watchlist'))
        except:
            print("no bueno")
            messages.error(request, "Item is already in your watchlist!")

    context = {
        "auction_data": auction_listing,
        "current_max_bid": current_max_bid,
        "comments": comment,
        "commentsform": commentsform,
        "bidsform": bidsform,
        "user": user,
    }

    if auction_listing.is_active == False:
        winner = auction_listing.bids_set.get(current_bid=current_max_bid)
        auction_winner = winner.user
        context.update({"auction_winner": auction_winner})

    return render(request, "checklisting.html", context)


def watchlist(request):

    user = request.user

    # Get user's watchlist items
    watchlist = Watchlist.objects.filter(user=user)

    context = {
        "watchlist": watchlist
    }

    # Handling remove from watchlist event
    if request.GET.get('ModelRef'):
        watchlistpk = request.GET.get('ModelRef')
        record = Watchlist.objects.get(id=watchlistpk)
        record.delete()

    return render(request, "watchlist.html", context)


def categories(request):
    return render(request, "categories.html")


def category(request, category):

    # Filter for categories
    if category == "Uncategorized":
        sublistings = Auction_Listings.objects.filter(category=None)
    else:
        sublistings = Auction_Listings.objects.filter(category=category)

    current_max_bid = []
    for auction in sublistings:
        current_max_bid.append(
            ((auction.bids_set.filter().aggregate(Max('current_bid')))))

    # Convert from a list of dictionaries into a list
    top_bids = [d['current_bid__max'] for d in current_max_bid]

    # Use Python's zip function to map each auction to it's maximum bid
    x = (zip(sublistings, top_bids))
    data = (tuple(x))

    print(data)

    page_num = request.GET.get('page')
    data_paginator = Paginator(data, 8)
    page = data_paginator.get_page(page_num)

    context = {
        "page": page,
        "category": category
    }

    print(context)

    return render(request, "category.html", context)
