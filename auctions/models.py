from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Listing(models.Model):
    title = models.CharField(max_length=64)
    image = models.URLField(default="", null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    start_bid = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default="", related_name="creator", null=False)
    status = models.CharField(max_length=10, default='open', choices=[
        ('open', 'Open'),
        ('closed', 'Closed'),
    ])

    def close_listing(self):
        self.status = 'closed'
        self.save()

    def __str__(self):
        return f"{self.id}: {self.title} {self.description}, {self.category}"
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist", null=False)
    listings = models.ManyToManyField(Listing, related_name="watchlists")


class Bid(models.Model):
    amount = models.IntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")

    class Meta:
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.amount}, {self.listing}, {self.user}"

    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=250, null=True, blank=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")