import datetime

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import ListingForm, BidForm, CommentForm
from .models import User, Listing, Watchlist, Bid, Comment


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        'listings': listings,
    })


def watchlist(request):
    curr = request.user
    if curr.is_authenticated:
        try:
            watchlist = Watchlist.objects.all()
        except Watchlist.DoesNotExist:
            watchlist = None

        if watchlist is not None:
            listings = []
            for element in watchlist:
                if element.user == curr:
                    listings.append(element.item)
            return render(request, "auctions/index.html", {
                'listings': listings,
                'watchlist': "Watchlist"
            })
    else:
        return HttpResponseRedirect(reverse("index"))


def remove(request, item):
    curr = request.user
    try:
        watchlist = Watchlist.objects.filter(user=curr)
    except Watchlist.DoesNotExist:
        watchlist = None
    itemObj = Listing.objects.get(listing_name=item)
    if watchlist.filter(item=itemObj).exists():
        watchlist.filter(item=itemObj).delete()

    return HttpResponseRedirect(reverse("details", args=[item]))


def add(request, item):

    curr = request.user

    try:
        watchlist = Watchlist.objects.filter(user=curr)
    except Watchlist.DoesNotExist:
        watchlist = None

    itemObj = Listing.objects.get(listing_name=item)

    if not watchlist.filter(item=itemObj).exists():
        watchitem = Watchlist(user=curr, item=itemObj)
        watchitem.save()

    return HttpResponseRedirect(reverse("details", args=[item]))


def details(request, item):
    listing = Listing.objects.get(listing_name=item)
    comments = Comment.objects.filter(item=listing)
    if request.user.is_authenticated and request.method == "POST":
        curr = request.user
        itemObj = Listing.objects.get(listing_name=item)
        form = BidForm(request.POST or None)
        commentForm = CommentForm(request.POST or None)

        if (form.is_valid()):
            bid = form.cleaned_data["bid_amount"]

            currBid = itemObj.current_bid

            if (not currBid and bid > itemObj.starting_bid) or (currBid and bid > currBid.value):
                bidObj = Bid(buyer=curr, value=bid)
                bidObj.save()
                itemObj.current_bid = bidObj
                itemObj.save()
                return render(request, "auctions/details.html", {
                    'listing': itemObj,
                    'form': BidForm,
                    'success': "Your bid has been sucessfully placed",
                    'comments': comments,
                    'form2': commentForm
                })

            return render(request, "auctions/details.html", {
                'listing': itemObj,
                'form': BidForm,
                'failure': "Your bid is too low",
                'comments': comments,
                'form2': commentForm
            })

        elif (commentForm.is_valid()):
            content = commentForm.cleaned_data["content"]
            if content != '':
                comment = Comment(user=curr, item=itemObj, content=content)
                comment.save()
    return render(request, "auctions/details.html", {
        'listing': listing,
        'form': BidForm,
        'comments': comments,
        'form2': CommentForm
    })


def create(request):
    template_name = 'auctions/create.html'
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if (form.is_valid()):
            title = form.cleaned_data["listing_name"]
            desc = form.cleaned_data["listing_desc"]
            bid = form.cleaned_data["starting_bid"]
            listing = Listing(listing_name=title, listing_desc=desc,
                              starting_bid=bid, creator=request.user, picture=request.FILES.get('picture', '/images/default.png'))
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, template_name, {
        'form': ListingForm,
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
    return HttpResponseRedirect(reverse("login"))


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
