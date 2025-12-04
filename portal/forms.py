import requests

from django import forms

from django.conf import settings
from shapp.utils import add_empty_choice

from portal.models import Location, ListingEnquiry, ContactUsEnquiry
from portal.constants import SORT_ORDER_OPTIONS

from shapp.constants import LISTING_CATEGORIES, LISTING_AMENITIES, LISTING_VENUES
from shapp.constants import LISTING_LAYOUTS, LISTING_FREQUENCIES, LISTING_NUMBER_OF_PEOPLE
# from portal.constants import LISTING_BEDROOMS_CHOICES, LISTING_BATHROOMS_CHOICES
# from portal.constants import RENT_PRICE_RANGES_LIST, AREA_RANGE_LIST


def get_locations_queryset():
    return Location.objects.filter(status=True)


class SearchForm(forms.Form):
    location = forms.ModelMultipleChoiceField(
        queryset=Location.objects.none(),
        required=False,
        widget=forms.widgets.SelectMultiple(attrs={
            'class': 'form-control form-control-lg temp-height-class',
            'placeholder': 'Search by location or building e.g, Dubai Marina or Burj Khalifa...'
        })
    )
    category = forms.ChoiceField(choices=add_empty_choice(LISTING_CATEGORIES, 'Type'), required=False,
                                 widget=forms.widgets.Select(
                                     attrs={
                                         'placeholder': 'Category',
                                         'class': 'form-control form-control-lg temp-height-class'
                                     })
                                 )

    amenities = forms.MultipleChoiceField(choices=LISTING_AMENITIES, required=False,
                                          widget=forms.widgets.SelectMultiple(
                                              attrs={
                                                  'placeholder': 'Amenities',
                                                  'class': 'form-control form-control-lg temp-height-class'
                                              })
                                          )

    venue = forms.ChoiceField(choices=add_empty_choice(LISTING_VENUES, 'Venue Type'), required=False,
                              widget=forms.widgets.Select(
                                  attrs={
                                      'placeholder': 'Venue Type',
                                      'class': 'form-control form-control-lg temp-height-class'
                                  })
                              )

    layout = forms.ChoiceField(choices=add_empty_choice(LISTING_LAYOUTS, 'Layout'), required=False,
                               widget=forms.widgets.Select(
                                   attrs={
                                       'placeholder': 'Layout',
                                       'class': 'form-control form-control-lg temp-height-class'
                                   })
                               )

    frequency = forms.ChoiceField(choices=add_empty_choice(LISTING_FREQUENCIES, 'Payment Type'), required=False,
                                  widget=forms.widgets.Select(
                                      attrs={
                                          'placeholder': 'Payment Type',
                                          'class': 'form-control form-control-lg temp-height-class'
                                      })
                                  )

    people = forms.ChoiceField(choices=add_empty_choice(LISTING_NUMBER_OF_PEOPLE, 'People'), required=False,
                               widget=forms.widgets.Select(
                                   attrs={
                                       'placeholder': 'People',
                                       'class': 'form-control form-control-lg temp-height-class'
                                   })
                               )

    sort_order = forms.ChoiceField(
        choices=SORT_ORDER_OPTIONS,
        required=False,
        widget=forms.widgets.Select(attrs={
            'class': 'form-control ui-select'
        })
    )

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        if self.data:
            self.fields['location'].queryset = get_locations_queryset()


class ListingEnquiryForm(forms.ModelForm):
    images = forms.CharField(required=False)
    phone = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'type': 'number'}))

    def __init__(self, *args, **kwargs):
        super(ListingEnquiryForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs = {
                'class': 'form-control'
            }

    class Meta:
        model = ListingEnquiry
        exclude = ('status', 'created_on', 'updated_on', )


class ListingBookViewingForm(forms.ModelForm):
    phone = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'type': 'number'}))

    def __init__(self, *args, **kwargs):
        super(ListingBookViewingForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs = {
                'class': 'form-control'
            }

    class Meta:
        model = ListingEnquiry
        exclude = ('message', 'status', 'created_on', 'updated_on', )


class ContactForm(forms.ModelForm):
    def clean(self):
        captcha = self.data.get('g-recaptcha-response', None)
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
            'response': captcha,
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY
        })
        result_json = resp.json()

        if not result_json['success']:
            raise forms.ValidationError('Please validate captcha.')

    class Meta:
        model = ContactUsEnquiry
        exclude = ('status', 'contact_type', 'created_on', 'updated_on')
