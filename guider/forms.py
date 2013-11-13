# -*- coding:utf-8 -*-
from django import forms
from django.conf import settings
from haystack.forms import SearchForm
from guider.models import DealReview
from django.http import Http404

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)

class DealReviewForm(forms.Form):
    deal_id = forms.IntegerField(widget=forms.HiddenInput())
    comment = forms.CharField(label='Comment', widget=forms.Textarea,
                                        max_length=COMMENT_MAX_LENGTH)

    def check_for_duplicate_comment(self, model, new):
        """
        Check that a submitted comment isn't a duplicate. This might be caused
        by someone posting a comment twice. If it is a dup, silently return the *previous* comment.
        """
        possible_duplicates = model._default_manager.filter(user = new.user)
        for old in possible_duplicates:
            if old.submit_date.date() == new.submit_date.date() and old.comment == new.comment:
                return old
        return new
