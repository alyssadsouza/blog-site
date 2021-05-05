from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

class Listing(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=350)
    starting_bid = models.DecimalField(max_digits=10,decimal_places=2)
    current_price = models.DecimalField(max_digits=10,decimal_places=2, default=0.00)
    image = models.URLField(blank=True, default="https://icon-library.com/images/no-image-icon/no-image-icon-0.jpg")
    FASHION, TOYS, ELECTRONICS, HOME = "FSH","TOY","ETC","HOM"
    CATEGORIES = [(FASHION, "Fashion"),(TOYS, "Toys"),(ELECTRONICS, "Electronics"),(HOME, "Home")]
    category = models.CharField(max_length=3, blank=True, choices=CATEGORIES)
    winner = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Item #{self.id}: {self.title}"

class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing, blank=True, related_name="watchers")
    listings_added = models.ManyToManyField(Listing, blank=True, related_name="publisher")
    def __str__(self):
        return f"{self.username}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return f"{self.bidder.username}'s bid on \"{self.listing.title}\": ${self.amount}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=900)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.listing} published by {self.user}"