from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, Listing, Comment, Bid
from django import forms

class createForm(forms.Form):
    title = forms.CharField(label='title', max_length=64)
    description = forms.CharField(label='description', max_length=300)
    imageUrl = forms.CharField(label='imageUrl', max_length=1000)
    price = forms.FloatField(label='price')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label='category', widget=forms.Select(attrs={'class': 'form-control col-md-1'}))

    def __init__(self, *args, **kwargs):
        super(createForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field, forms.ModelChoiceField ):
                field.widget.attrs['class'] = 'form-control col-md-6'

class commentForm(forms.Form):
    comment = forms.CharField(label='Add Comment', max_length= 300, widget=forms.TextInput(attrs={'class': 'form-control'}))

def index(request):
    

    if request.method == "POST":
        categoryFromForm = request.POST["category"]
        currentCategory = Category.objects.get(categoryName=categoryFromForm)
        categories = Category.objects.exclude(categoryName=currentCategory).all()
        listings = Listing.objects.filter(category=currentCategory, isActive=True)
        for listing in listings:
            listing.description = listing.description[:100]+'...'
        
        return render(request,"auctions/index.html",{
            "listings": listings,
            "categories": categories,
            "currentCategory":currentCategory,
        })
    else:
        allListings = Listing.objects.filter(isActive=True)
        categories = Category.objects.all()
        for listing in allListings:
            listing.description = listing.description[:100]+'...'

        return render(request, "auctions/index.html", {
            "listings": allListings,
            "categories": categories,
            "currentCategory": 'Select'
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
    
@login_required(login_url="login")
def createListing(request):
    if request.method == "POST":
        form = createForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            imageUrl = form.cleaned_data['imageUrl']
            price = form.cleaned_data['price']
            category = form.cleaned_data['category']
            currentUser = request.user  
            newListing = Listing(
                title=title,
                description=description,
                imageUrl=imageUrl,
                price=float(price),
                category=category,
                owner=currentUser,
            )
            newListing.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })       
    
    else:
        return render(request, "auctions/create.html",{
            "form": createForm()
        })
    
def view_listing(request, id):
    listingItem = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingItem.watchers.all()
    comments = listingItem.listingComments.all()
    isOwner = request.user.username == listingItem.owner.username
    max_value = max_bid(request.user, listingItem )
    if listingItem.currentBid == max_value and listingItem.isActive == False:
        return render(request, "auctions/listing.html",{
        "listingItem": listingItem,
        "isListingInWatchlist": isListingInWatchlist,
        "commentform": commentForm(),
        "comments": comments,
        "userBid": max_value,
        "isOwner": isOwner, 
        "message2": 'Congratulation you won the bid',
    })       
    else:
        return render(request, "auctions/listing.html",{
            "listingItem": listingItem,
            "isListingInWatchlist": isListingInWatchlist,
            "commentform": commentForm(),
            "comments": comments,
            "userBid": max_value,
            "isOwner": isOwner, 
            
        })

def max_bid(user, listingItem):
    if user.is_authenticated:
        userBids = user.Bidder.filter(auction=listingItem)
        max_value = None
        for bid in userBids:
            if max_value is None or bid.offer > max_value: max_value = bid.offer
        return max_value
    else:
        return None


@login_required(login_url="login")
def addwatchers(request, id):
    listingItem = Listing.objects.get(pk=id)
    currentUser = request.user
    listingItem.watchers.add(currentUser)
    return HttpResponseRedirect(reverse('listing', args=(id, )))

@login_required(login_url="login")
def removewatchers(request, id):
    listingItem = Listing.objects.get(pk=id)
    currentUser = request.user
    listingItem.watchers.remove(currentUser)
    return HttpResponseRedirect(reverse('listing', args=(id, )))

@login_required(login_url="login")
def watchlist(request):
    currentUser = request.user
    listings = currentUser.watched_listings.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required(login_url="login")
def addComment(request, id):
    commentform = commentForm(request.POST)

    if commentform.is_valid():
        comment = commentform.cleaned_data['comment']
        currentUser = request.user
        listingItem = Listing.objects.get(pk=id)
        newComment = Comment(author=currentUser, comment=comment, listing=listingItem)
        newComment.save()

        return HttpResponseRedirect(reverse('listing', args=(id, )))

@login_required(login_url="login")  
def addBid(request, id):
    listingItem = Listing.objects.get(pk=id)
    offer = float(request.POST['offer'])
    isListingInWatchlist = request.user in listingItem.watchers.all()
    comments = listingItem.listingComments.all()
    isOwner = request.user.username == listingItem.owner.username
    max_value = max_bid(request.user, listingItem )
    if is_valid(offer, listingItem):
        listingItem.currentBid = offer
        currentUser = request.user
        auction = listingItem
        newBid = Bid(
            auction=auction,
            user=currentUser,
            offer=offer,
        )
        newBid.save()
        listingItem.save()
        return render(request, "auctions/listing.html", {
            "message":"Your Bid has been Placed",
            "listingItem":listingItem,
            "isListingInWatchlist": isListingInWatchlist,
            "commentform": commentForm(),
            "comments": comments,
            "update": True,
            "userBid": max_value,
            "isOwner": isOwner,
        })
    else:
        return render(request, "auctions/listing.html", {
            "message": "Bid Amount Invalid",
            "listingItem":listingItem,
            "isListingInWatchlist": isListingInWatchlist,
            "commentform": commentForm(),
            "comments": comments,
            "update": False,
            "userBid": max_value,
            "isOwner": isOwner,
        })
        

def is_valid(offer, listingItem):
    if offer >= listingItem.price and (listingItem.currentBid is None or offer > listingItem.currentBid):
        return True
    else:
        return False
    
def closeAuction(request, id):
    listingItem = Listing.objects.get(pk=id)
    listingItem.isActive = False
    listingItem.save()
    isListingInWatchlist = request.user in listingItem.watchers.all()
    comments = listingItem.listingComments.all()
    isOwner = request.user.username == listingItem.owner.username
    max_value = max_bid(request.user, listingItem )
    return render(request, "auctions/listing.html", {
        "listingItem": listingItem,
        "isListingInWatchlist": isListingInWatchlist,
        "commentform": commentForm(),
        "comments": comments,
        "userBid": max_value,
        "isOwner": isOwner, 
        "message2": "Auction is Closed"
    })

def openAuction(request, id):
    listingItem = Listing.objects.get(pk=id)
    listingItem.isActive = True
    listingItem.save()
    isListingInWatchlist = request.user in listingItem.watchers.all()
    comments = listingItem.listingComments.all()
    isOwner = request.user.username == listingItem.owner.username
    max_value = max_bid(request.user, listingItem )
    return render(request, "auctions/listing.html", {
        "listingItem": listingItem,
        "isListingInWatchlist": isListingInWatchlist,
        "commentform": commentForm(),
        "comments": comments,
        "userBid": max_value,
        "isOwner": isOwner, 
        "message2": "Auction is Opened"
    })

