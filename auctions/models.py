from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORY_CHOICES = (
    ('Textbook', 'Textbook'),
    ('Videogame', 'Videogame'),
    ('Hardware', 'Hardware')
)


class User(AbstractUser):
    pass


class Auction_Listings(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(
        choices=CATEGORY_CHOICES, max_length=9, blank=True, null=True)
    picture = models.ImageField(blank=True, null=True)
    starting_bid = models.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Auction_Listings"

    def __str__(self):
        return self.title


class Comments(models.Model):
    comment = models.TextField(default=None, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(
        Auction_Listings, default=None, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Comments"


class Bids(models.Model):
    current_bid = models.DecimalField(
        max_digits=6, decimal_places=2, default=None, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(
        Auction_Listings, default=None, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Bids"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    auction = models.ForeignKey(
        Auction_Listings, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = [['user', 'auction']]