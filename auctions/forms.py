from django import forms
from .models import Auction_Listings, Comments, Bids


class PostForm(forms.ModelForm):

    class Meta:
        model = Auction_Listings
        exclude = ["user"]
        fields = ['title', 
                 'description',
                 'category',
                 'picture',
                 'starting_bid',
                 'user'
                ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control w-25'}),
            'description': forms.Textarea(attrs={'class': 'form-control w-25'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control w-25'}),
        }

class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        exclude = ['user', 'auction'] 
        fields = ['comment']

        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

class BidsForm(forms.ModelForm):

    class Meta:
        model = Bids
        exclude = ['user', 'auction'] 
        fields = ['current_bid']
        labels = {
        "current_bid": "Your bid"
        }


        widgets = {
            'current_bid': forms.NumberInput(attrs={'class': 'form-control'}),
        }