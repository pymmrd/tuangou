from django import forms

class DealWishForm(forms.Form):
    wish_deal = forms.IntegerField(widget=forms.HiddenInput())
    
