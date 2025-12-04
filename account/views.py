import json
import datetime
import requests
import short_url

from collections import Counter

from django import forms
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now as tz_now
from django.views.generic import TemplateView, FormView, View, UpdateView

from account.forms import ProfileForm, PasswordChange, SignUpForm, AddListingForm, EditListingForm
from account.mixins import LoginRequiredMixin
from account.models import UserFavoriteListings
from account.models import UserProfile
from portal.constants import AMENITIES
from portal.models import Listing, ListingAsset, ListingEnquiry
from portal.tasks import send_activation_email_on_successful_signup
from shapp.aws import AWS
from shapp.helpers import get_client_ip

from account.models import CompanyContract


class RegisterView(FormView):
    template_name = "account/register.djhtml"
    form_class = SignUpForm

    def get_context_data(self, **kwargs):
        ctx = super(RegisterView, self).get_context_data(**kwargs)

        return ctx

    def form_valid(self, form):
        if not self.verify_captcha(self.request):
            form.add_error('captcha', 'Invalid captcha')

            return super(RegisterView, self).form_invalid(form)

        user = form.save(commit=False)
        user.is_active = False
        user.email = user.username  # As we want users to use their email addresses as their usernames.

        user.save()

        user.userprofile.phone = form.cleaned_data['phone']
        user.userprofile.save()

        send_activation_email_on_successful_signup(user)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account:user-register-success')

    def verify_captcha(self, request):
        payload = {
            'response': request.POST['g-recaptcha-response'],
            'remoteip': get_client_ip(request),
            'secret': settings.CAPTCHA_SECRET_KEY
        }

        response = requests.post('https://www.google.com/recaptcha/api/siteverify', payload)

        if response.status_code == 200:
            response = response.json()
        else:
            return False

        return response['success']


class ActivateView(TemplateView):
    template_name = "portal/activate_account.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(ActivateView, self).get_context_data(**kwargs)

        user_id = short_url.decode_url(kwargs['token'])
        try:
            user = User.objects.get(pk=user_id, is_active=False)
            user.is_active = True
            user.userprofile.email_confirmed = True
            user.userprofile.save()
            user.save()

            expiry_date = datetime.date.today() + datetime.timedelta(days=365)
            for _ in range(3):
                ListingSlot.objects.create(user=user, listing_type=PROPERTY_TYPE_RENT,
                                           status=ListingSlot.STATUS_ACTIVE, expiry_date=expiry_date)

            ctx['valid'] = True
        except User.DoesNotExist:
            ctx['valid'] = False

        return ctx


class RegisterSuccessView(TemplateView):
    template_name = "account/register_success.djhtml"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "account/dashboard.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        return ctx


class InquiriesView(LoginRequiredMixin, TemplateView):
    template_name = "account/inquiries.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        company = user.userprofile.company

        ctx['inquiries'] = ListingEnquiry.objects.filter(listing__company=company).order_by('-id')

        return ctx


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "account/stats.djhtml"


class ContractsView(LoginRequiredMixin, TemplateView):
    template_name = "account/contracts.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        company = user.userprofile.company

        ctx['published_spaces'] = 0
        ctx['unpublished_spaces'] = 0
        ctx['contracts'] = CompanyContract.objects.filter(company=company).order_by('-id')

        return ctx


class PlansView(LoginRequiredMixin, TemplateView):
    template_name = "account/plans.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(PlansView, self).get_context_data(**kwargs)

        ctx['packages'] = settings.PACKAGES

        return ctx


class ListingSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "account/listing_success.djhtml"


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "account/profile.djhtml"
    form_class = ProfileForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if not self.request.POST:
            profile = self.get_user_profile()

            ctx['form'] = ProfileForm(
                initial={
                    'first_name': profile.user.first_name,
                    'last_name': profile.user.last_name,
                    'phone': profile.phone
                }
            )

        return ctx

    def form_valid(self, form):
        profile = self.get_user_profile()

        data = form.cleaned_data

        profile.user.first_name = data['first_name']
        profile.user.last_name = data['last_name']
        profile.phone = data['phone']

        profile.save()
        profile.user.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account:user-profile') + '?success=1'

    def get_user_profile(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)

        return profile


class ProfilePasswordChangeView(LoginRequiredMixin, FormView):
    template_name = "account/change_password.djhtml"
    form_class = PasswordChange

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()

        form_kwargs['user'] = self.request.user

        return form_kwargs

    def form_valid(self, form):
        data = form.cleaned_data

        self.request.user.set_password(data['new_password'])
        update_session_auth_hash(self.request, self.request.user)
        self.request.user.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account:user-change-password') + '?success=1'


class UserListingsView(LoginRequiredMixin, TemplateView):
    template_name = "account/company_spaces.djhtml"

    def get_context_data(self, **kwargs):
        user = self.request.user
        ctx = super(UserListingsView, self).get_context_data(**kwargs)

        listings = Listing.objects.filter(company=user.userprofile.company).exclude(status='X')

        ctx['listings'] = listings

        return ctx


class UserFavoritesView(LoginRequiredMixin, TemplateView):
    template_name = "account/user_favorites.djhtml"

    def get_context_data(self, **kwargs):
        user = self.request.user
        ctx = super(UserFavoritesView, self).get_context_data(**kwargs)

        ctx['listings'] = UserFavoriteListings.objects.filter(user=user).exclude(listing__status='X')

        return ctx


class AddListingView(LoginRequiredMixin, FormView):
    template_name = "account/user_listing_form.djhtml"
    form_class = AddListingForm

    def get_form_kwargs(self):
        kwargs = super(AddListingView, self).get_form_kwargs()

        property_types_counter = Counter()

        kwargs['property_types_counter'] = property_types_counter

        return kwargs

    def form_valid(self, form):
        new_listing = form.save(commit=False)
        new_listing.user = self.request.user
        new_listing.slug = slugify(new_listing.title)
        new_listing.status = Listing.STATUS_PUBLISHED

        new_listing.save()

        self.upload_images(new_listing, self.request.POST['fileuploader-list-files'])
        self.upload_floorplans(new_listing, self.request.POST['fileuploader-list-floorplans'])

        return HttpResponseRedirect('{}?title={}'.format(
            reverse('account:listing-success'), new_listing.title)
        )

    def get_context_data(self, **kwargs):
        ctx = super(AddListingView, self).get_context_data(**kwargs)

        ctx['amenities'] = AMENITIES[:5]

        return ctx

    def upload_images(self, listing, images):
        if images:
            for item in images.split(','):
                image = ListingAsset(
                    listing=listing,
                    asset_type=ListingAsset.ASSET_TYPE_IMAGE,
                    url=item
                )
                image.save()

    def upload_floorplans(self, listing, images):
        if images:
            for item in images.split(','):
                image = ListingAsset(
                    listing=listing,
                    asset_type=ListingAsset.ASSET_TYPE_FLOORPLANS,
                    url=item
                )
                image.save()


class EditListingView(LoginRequiredMixin, UpdateView):
    template_name = 'account/user_listing_form.djhtml'
    form_class = EditListingForm
    model = Listing
    queryset = Listing.objects.exclude(status=Listing.STATUS_DELETED)

    def get_context_data(self, **kwargs):
        ctx = super(EditListingView, self).get_context_data(**kwargs)

        ctx['amenities'] = AMENITIES[:5]
        ctx['listing'] = self.object

        ctx['listing_images'] = self.prepare_assets(
            self.object.assets.filter(asset_type=ListingAsset.ASSET_TYPE_IMAGE))
        # ctx['listing_floorplans'] = self.prepare_assets(
            # self.object.assets.filter(asset_type=ListingAsset.ASSET_TYPE_FLOORPLANS))

        return ctx

    def prepare_assets(self, assets):
        return json.dumps([{
            'name': item.url.split('/')[-1:][0],
            'type': 'image/jpg',
            'size': 0,
            'file': item.url,
            'data': {
                'url': item.url
            }
        } for item in assets])

    def get_object(self, queryset=None):
        listing = super(EditListingView, self).get_object(queryset)
        if listing.company != self.request.user.userprofile.company:
            raise Listing.DoesNotExist

        return listing

    def form_valid(self, form):
        old_listing = self.get_object()
        # If the user doesn't need pre-approval for listings, or the current version of the listing is not approved yet,
        # we don't need to create a new version. New versions are only needed when editing an approved listing
        if (not self.request.user.userprofile.needs_approval or
                old_listing.approval_status == Listing.APPROVAL_STATUS_REVIEW):
            new_listing = form.save(commit=False)
            new_listing.previous_version = old_listing
            new_listing.save()

            return HttpResponseRedirect('{}?title={}'.format(
                reverse('account:listing-success'), new_listing.title)
            )

        new_listing = form.save(commit=False)
        new_listing.pk = None
        new_listing.previous_version = old_listing

        new_listing.save()

        self.upload_images(new_listing, self.request.POST['fileuploader-list-files'])
        self.upload_floorplans(new_listing, self.request.POST['fileuploader-list-floorplans'])

        return HttpResponseRedirect('{}?title={}'.format(
            reverse('account:listing-success'), new_listing.title)
        )

    def upload_images(self, listing, images):
        if images:
            for item in images.split(','):
                image = ListingAsset(
                    listing=listing,
                    asset_type=ListingAsset.ASSET_TYPE_IMAGE,
                    url=item
                )
                image.save()

    def upload_floorplans(self, listing, images):
        if images:
            for item in images.split(','):
                image = ListingAsset(
                    listing=listing,
                    asset_type=ListingAsset.ASSET_TYPE_FLOORPLANS,
                    url=item
                )
                image.save()


class UnpublishListingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk)
        if listing.user != request.user:  # or listing.manager != request.user:
            response = {'success': False, 'msg': 'You do not own this listing'}
        else:
            listing.status = Listing.STATUS_UNPUBLISHED
            listing.save()

            response = {'success': True}

        return JsonResponse(response)


class PublishListingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk)
        if listing.user != request.user:  # or listing.manager != request.user:
            response = {'success': False, 'msg': 'You do not own this listing'}
        else:
            listing.status = Listing.STATUS_PUBLISHED
            listing.save()

            response = {'success': True}

        return JsonResponse(response)


class DeleteListingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk)
        if listing.user != request.user:  # or listing.manager != request.user:
            response = {'success': False, 'msg': 'You do not own this listing'}
        else:
            listing.status = Listing.STATUS_DELETED
            listing.slot = None
            listing.save()

            response = {'success': True}

        return JsonResponse(response)


class DocumentUploadView(View):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('files[]', request.FILES.get('floorplans[]', None))
        file_url = AWS.upload_file(file)

        if file_url:
            response = {
                'url': file_url
            }
            status = 200
        else:
            response = {'url': None}
            status = 400

        return JsonResponse(response, status=status)


class UserFavoriteListingUpdateView(View):
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'msg': 'signin'})

        listing_id = request.POST.get('listing_id', None)

        if listing_id:
            try:
                listing = Listing.objects.get(id=listing_id, status='P')
            except Listing.DoesNotExist:
                response = {'status': 'error', 'msg': 'No listing found'}

            try:
                favorite = UserFavoriteListings.objects.get(listing=listing, user=self.request.user)
                favorite.delete()
                response = {'status': 'success', 'msg': 'removed'}
            except UserFavoriteListings.DoesNotExist:
                record = UserFavoriteListings(
                    listing=listing,
                    user=self.request.user
                )
                record.save()
                response = {'status': 'success', 'msg': 'added'}

        return JsonResponse(response)
