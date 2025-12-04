from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from account.models import UserProfile
from portal.models import Listing
from portal.models import Location


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    last_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    phone = forms.CharField(max_length=15, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'type': 'number'}))

    class Meta:
        model = UserProfile
        exclude = ('user',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ()
        fields = ('first_name', 'last_name', 'email')


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, )
    last_name = forms.CharField(max_length=30, )
    phone = forms.CharField(max_length=14)
    captcha = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2',)
        error_messages = {
            'username': {
                'unique': 'A user with the same email address already exists',
            },
        }


class PasswordChange(forms.Form):
    old_password = forms.CharField(label='Old Password', max_length=50, required=True, widget=forms.PasswordInput)
    new_password = forms.CharField(label='New Password', max_length=50, required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm New Password', max_length=50, required=True, widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChange, self).__init__(*args, **kwargs)

    def clean(self):
        old_password = self.cleaned_data.get('old_password', None)
        new_password = self.cleaned_data.get('new_password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if not self.user.check_password(old_password):
            raise forms.ValidationError('Old password is incorrect')

        if new_password != confirm_password:
            raise forms.ValidationError('New password doesn\'t matched')


class AddListingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        property_types_counter = kwargs.pop('property_types_counter', None)
        # available_rental_slots = kwargs.pop('available_rental_slots', None)
        # available_sales_slots = kwargs.pop('available_sales_slots', None)

        super(AddListingForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs = {
                'class': 'form-control form-control-lg'
            }
        self.fields['amenities'].widget.attrs = {}
        # self.fields['is_furnished'].widget.attrs = {}
        # self.fields['is_fitted'].widget.attrs = {}
        # self.fields['built_up_area'].widget.attrs = {'class': 'form-control form-control-lg', 'min': 0}
        # self.fields['plot_area'].widget.attrs = {'class': 'form-control form-control-lg', 'min': 0}

        # if property_types_counter:
        #     property_type_choices = list()
        #     for k, v in property_types_counter.items():
        #         if v > 0:
        #             ptype = 'Sale' if k[1] == 'S' else 'Rent'
        #             choice = (k[0], ptype)
        #             property_type_choices.append(choice)

        #     # if property_type_choices:
        #     #     self.fields['property_type'].choices = property_type_choices
        #     #     self.fields['property_type'].error_messages['invalid_choice'] = 'Property type "Sale" is not allowed at the moment. Please contact us for details'
        # else:
        #     self.fields['property_type'].choices = (('', 'No slots available'),)
        #     self.fields['property_type'].widget.attrs.update({
        #         'disabled': True
        #     })

        self.fields['location'].queryset = Location.objects.filter(status=True)

    class Meta:
        model = Listing
        exclude = (
            'previous_version', 'approval_status', 'slot', 'user', 'manager',
            'created_on', 'updated_on', 'status', 'slug', 'rera_permit_number'
        )


class EditListingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditListingForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs = {
                'class': 'form-control form-control-lg'
            }
        self.fields['amenities'].widget.attrs = {}
        # self.fields['is_furnished'].widget.attrs = {}
        # self.fields['is_fitted'].widget.attrs = {}
        # self.fields['built_up_area'].widget.attrs = {'class': 'form-control form-control-lg', 'min': 0}
        # self.fields['plot_area'].widget.attrs = {'class': 'form-control form-control-lg', 'min': 0}

        # self.fields['status'].choices = (
        #     (Listing.STATUS_DRAFT, 'Draft'),
        #     (Listing.STATUS_UNPUBLISHED, 'Unpublished'),
        #     (Listing.STATUS_PUBLISHED, 'Published'),
        # )

    class Meta:
        model = Listing
        exclude = (
            'property_type', 'previous_version', 'approval_status', 'slot', 'user', 'created_on', 'updated_on',
            'slug', 'rera_permit_number'
        )
