from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError

from django.db.models import Max

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from django import forms

from .models import *

class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'image', 'description', 'start_bid', 'category')

    new_category = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False

    def clean(self):
        cleaned_data = super().clean()
        new_category = cleaned_data.get('new_category')
        if new_category:
            category, created = Category.objects.get_or_create(name=new_category)
            cleaned_data['category'] = category
        return cleaned_data

def index(request):
    list = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "list": list
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

@login_required
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.save()
            return HttpResponseRedirect(reverse("active"))
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })
    return render(request, "auctions/create_listing.html", {
        "form": NewListingForm(),
    })

@login_required
def close_listing(request, pk):
    list = Listing.objects.get(pk=pk)
    list.close_listing()
    return redirect('listing', pk)


def listing_view(request):
    list = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "list": list,
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing=listing)
    max_bid = listing.bids.aggregate(Max('amount'))['amount__max']
    current_bid = listing.bids.filter(amount=max_bid).first()
    if request.user.is_authenticated:
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    else:
        watchlist = None
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": watchlist,
        "max_bid": max_bid,
        "current_bid": current_bid,
        "comments": comments,
    })

@login_required
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    if listing not in watchlist.listings.all():
        watchlist.listings.add(listing)
    return redirect('listing', listing_id)

@login_required
def remove_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    if listing in watchlist.listings.all():
        watchlist.listings.remove(listing)
    return redirect('listing', listing_id)

@login_required
def bid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        amount = int(request.POST["bid"])

        if listing.creator == request.user:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error": "You cannot bid on your own listing"
            })
        
        # Check if the bid is higher than the start bid
        if amount <= listing.start_bid:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error": "Bid must be higher than the start bid"
            })
        
        # Check if there are previous bids
        if listing.bids.exists():
            previous_bid = listing.bids.order_by('-amount').first()
            # Check if the new bid is higher than the previous bid
            if amount <= previous_bid.amount:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "error": "Bid must be higher than the current bid"
                })
        
        new_bid = Bid(amount=amount, listing=listing, user=request.user)
        new_bid.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
@login_required
def comments(request, pk):
    if request.method == "POST":
        listing = Listing.objects.get(pk=pk)
        comment = request.POST["comment"]
        comments = Comment(comment=comment, listing=listing, user=request.user)
        comments.save()
        return HttpResponseRedirect(reverse("listing", args=(pk,)))

@login_required
def watchlist(request):
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    list = watchlist.listings.all()
    return render(request, "auctions/watchlist.html", {
        "list": list
    })

@login_required
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required
def category(request, category_name):
    category = Category.objects.get(name=category_name)
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category_name": category_name
    })