from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=50)

    def __str__(self):
        return self.categoryName

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=300)
    imageUrl = models.CharField(max_length=1000, blank=True, null=True)
    price = models.FloatField()
    currentBid = models.FloatField(blank=True, null=True)
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchers = models.ManyToManyField(User, blank=True, null=True, related_name='watched_listings')

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComments" )
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComments" )
    comment = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.author} comment on {self.listing}"
    
class Bid(models.Model):
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='auction')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Bidder')
    offer =  models.FloatField()