from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Listing, Bid, Comment, User
from django.contrib import messages

def index(request):
    return render(request, "auctions/index.html", {
        "listings":Listing.objects.all()
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories":zip([i[0] for i in Listing.objects.first().CATEGORIES],[i[1] for i in Listing.objects.first().CATEGORIES])
    })

def category(request, category):
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {"listings":listings})

def comment(request, id):
    if request.method == 'POST':
        comment = Comment(
            listing=Listing.objects.get(pk=int(id)),
            user=request.user,
            comment=request.POST['comment']
            )
        comment.save()
        print("saved")

    return redirect("listing", list_id=int(id))

def listing(request, list_id):
    if request.method == 'POST':
        if request.POST['add'] == 'True':
            request.user.watchlist.add(Listing.objects.get(pk=int(request.POST['listing'])))
        else:
            request.user.watchlist.remove(Listing.objects.get(pk=int(request.POST['listing'])))

    listing = Listing.objects.get(pk=list_id)

    price = max(listing.current_price,listing.starting_bid)

    if len(listing.category) > 0:
        category = listing.get_category_display()
    else:
        category = 'No Category Listed'

    lister = request.user.username == listing.publisher.all().first().username and listing.active

    winner = False
    if not listing.active:
        winner = request.user.username == listing.winner
    
    return render(request, "auctions/listing.html", {
        "listing":listing,
        "price":price,
        "watchlist": request.user.watchlist.all(),
        "publisher":listing.publisher.all().first().username,
        "category": category,
        "bids":listing.bids.all(),
        "bidnum":len(listing.bids.all()),
        "lister":lister,
        "winner":winner,
        "comments":Comment.objects.filter(listing=listing)
    })

@login_required
def close(request, id):
    if request.method == 'GET':
        listing = Listing.objects.get(pk=int(id))
        listing.active = False
        listing.save()
        listing.winner = listing.bids.get(amount=listing.current_price).bidder.username
        listing.save()
    return HttpResponseRedirect(reverse("index"))

@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all()
    })

@login_required
def create_listing(request):
    if request.method == 'POST':
        title,description,starting_bid,category = request.POST['title'],request.POST['description'],float(request.POST['starting_bid']),request.POST['category']
        if len(request.POST['image']) == 0:
            image = "https://icon-library.com/images/no-image-icon/no-image-icon-0.jpg"
        else:
            image=request.POST['image']
        listing = Listing(title=title,description=description,starting_bid=starting_bid,category=category,image=image)
        listing.save()
        request.user.listings_added.add(listing)
        request.user.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, 'auctions/create-listing.html', {
        "categories":zip([i[0] for i in Listing.objects.first().CATEGORIES],[i[1] for i in Listing.objects.first().CATEGORIES])
    })

@login_required
def bid(request, id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=int(id))
        bid = float(request.POST['bid'])
        print(listing.current_price, listing.starting_bid)
        if listing.starting_bid > listing.current_price:
            if bid >= listing.starting_bid:
                listing.current_price = float(bid)
                listing.save()
                bid = Bid(bidder=request.user, listing=listing, amount=bid)
                bid.save()
            else:
                messages.add_message(request, messages.ERROR, 'Your bid must be at least as high as the starting bid')
        else:
            if bid > listing.current_price:
                listing.current_price = float(bid)
                listing.save()
                bid = Bid(bidder=request.user, listing=listing, amount=bid)
                bid.save()
            else:
                messages.add_message(request, messages.ERROR, 'Your bid must be greater than the current bid')
    return redirect("listing",list_id=int(id))


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

@login_required
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
