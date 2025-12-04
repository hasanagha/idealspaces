import re
import operator
import requests

from functools import reduce

from django.conf import settings

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.http import QueryDict
from django.urls import reverse
from django.utils.timezone import now as tz_now
from django.views import View
from django.views.generic import TemplateView, FormView
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import UserFavoriteListings
from portal.constants import AMENITIES, SORT_ORDER_PRICE_ASC, SORT_ORDER_PRICE_DESC, BANNED_WORDS
from portal.forms import ContactForm
from portal.forms import ListingEnquiryForm
from portal.forms import SearchForm
from portal.location_tree import LocationTree
from portal.models import Listing, Location, ListingStats, ContactUsEnquiry, SpamEnquiry
from portal.tasks import send_listing_email_on_successful_submission

from speedyblog.models import Post
from speedyblog.settings import POST_STATUS_PUBLISHED

from shapp.constants import LISTING_CATEGORIES, LISTING_FREQUENCIES
from shapp.constants import CATEGORY_SERVICED_OFFICES, CATEGORY_BANQUET_HALLS, CATEGORY_COWORKING_SPACES, CATEGORY_MEETING_ROOMS

from shapp.sms import SMSService
from shapp.email import EmailService
from shapp.utils import get_user_ip, clean_html

from better_profanity import profanity



class ComingSoonView(TemplateView):
    template_name = "portal/comingsoon.djhtml"


class FormSubmittedView(TemplateView):
    template_name = "portal/formsubmitted.djhtml"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['type'] = kwargs['type']

        return ctx


class HomeView(TemplateView):
    template_name = "portal/home.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)

        form = SearchForm()
        ctx['search_form'] = form

        listings = Listing.objects.get_published_listings()

        # ctx['featured_properties'] = listings.filter(is_featured=True)
        ctx['serviced_offices_count'] = listings.filter(category=CATEGORY_SERVICED_OFFICES).count()
        ctx['meeting_rooms_count'] = listings.filter(category=CATEGORY_MEETING_ROOMS).count()
        # ctx['coworking_spaces_count'] = listings.filter(category=CATEGORY_COWORKING_SPACES).count()
        # ctx['banquet_halls_count'] = listings.filter(category=CATEGORY_BANQUET_HALLS).count()

        ctx['blog_posts'] = Post.objects.filter(status=POST_STATUS_PUBLISHED).order_by('-created_on')[:3]

        return ctx


class LandlordView(TemplateView):
    template_name = "portal/landlords.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(LandlordView, self).get_context_data(**kwargs)

        form = SearchForm()
        ctx['search_form'] = form
        ctx['packages'] = settings.PACKAGES

        ctx['blog_posts'] = Post.objects.filter(status=POST_STATUS_PUBLISHED)[:3]

        return ctx


class SearchView(TemplateView):
    template_name = "portal/search.djhtml"

    def get_search_title_for_search_form(self, form):
        if not form.is_valid():
            return 'Spaces in United Arab Emirates'

        cd = form.cleaned_data
        if cd['location'] and len(cd['location']) == 1:
            location = cd['location'][0]
            if location.is_city:
                location_name = location.name
            elif location.is_location:
                location_name = '{}, {}'.format(location.name, location.parent.name)
            elif location.is_sublocation:
                location_name = '{}, {}, {}'.format(location.name, location.parent.name, location.parent.parent.name)
            else:
                location_name = 'United Arab Emirates'
        else:
            location_name = 'United Arab Emirates'

        if cd['category'] and cd['category'] in dict(LISTING_CATEGORIES):
            type_suffix = dict(LISTING_CATEGORIES)[cd['category']]
            # category_list = list()
            # for category in cd['category']:
            #     for cat in LISTING_CATEGORIES:
            #         if category in cat:
            #             category_list.append(cat[1])

            # type_suffix = ', '.join(category_list)
        else:
            type_suffix = 'Spaces'

        return '{} in {}'.format(type_suffix, location_name)

    def get_user_favorites(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return UserFavoriteListings.objects.filter(user=user).values_list('listing_id', flat=True)
        else:
            return None

    def get_page_title_and_meta_description(self, form, search_title=None):
        if not search_title:
            search_title = self.get_search_title_for_search_form(form)

        page_title = search_title
        meta_description = ''

        cd = form.cleaned_data

        if cd['category'] and cd['category'] in dict(LISTING_CATEGORIES):
            if cd['category'] == 'serviced-offices':
                page_title = 'Top 10 Business Centers & Serviced Offices in Dubai'
                meta_description = 'Browse Top 20 business centers, serviced offices and short term office available for rent in Dubai with Ideal Spaces. Compare photos, prices, reviews, enquire and book directly.'

            if cd['category'] == 'meeting-rooms':
                page_title = 'Top 10 Meeting Rooms & Conference Rooms in Dubai'
                meta_description = 'Browse Top 20 meeting rooms and conference rooms available for rent in Dubai with Ideal Spaces. Compare photos, prices, reviews, enquire and book directly.'

            if cd['category'] == 'coworking-spaces':
                page_title = 'Top 10 Coworking spaces in Dubai'
                meta_description = 'Browse Top 20 coworking spaces available for rent in Dubai with Ideal Spaces. Compare photos, prices, reviews, enquire and book directly.'

        return page_title, meta_description

    def get_context_data(self, **kwargs):
        ctx = super(SearchView, self).get_context_data(**kwargs)

        cleaned_query_params = QueryDict(mutable=True)
        for k, v in self.request.GET.lists():
            cleaned_values = list(filter(None, v))
            if len(v):
                if k in ['location', 'amenities']:
                    cleaned_query_params.setlist(k, cleaned_values)
                else:
                    if cleaned_values:
                        cleaned_query_params[k] = cleaned_values[0]

        if 'sef' in kwargs:
            if 'category' in kwargs:
                category = kwargs['category']

                for cat in LISTING_CATEGORIES:
                    if category in cat:
                        cleaned_query_params['category'] = category

            if 'sublocation' in kwargs:
                sublocation_slug = kwargs['sublocation']
                sublocation = Location.objects.get(is_sublocation=True, slug=sublocation_slug)
                cleaned_query_params.appendlist('location', sublocation.pk)

            if 'location' in kwargs:
                location_slug = kwargs['location']
                location = Location.objects.get(is_location=True, slug=location_slug)
                cleaned_query_params.appendlist('location', location.pk)

            if 'city' in kwargs:
                city_slug = kwargs['city']
                city = Location.objects.get(is_city=True, slug=city_slug)
                cleaned_query_params.appendlist('location', city.pk)

        # Build a location tree and use the leaf nodes as our search query
        search_location_tree = LocationTree()
        for location_id in cleaned_query_params.getlist('location'):
            location = Location.objects.get(pk=location_id)
            search_location_tree.add_location(location)
        location_ids_to_search_with = []
        for location_node in search_location_tree.tree.leaves():
            if location_node.identifier == 'root':
                continue
            location_ids_to_search_with.append(location_node.identifier)
        cleaned_query_params.setlist('location', location_ids_to_search_with)

        form = SearchForm(cleaned_query_params)
        ctx['search_form'] = form
        ctx['amenities'] = AMENITIES

        ctx['selected_location_name'] = cleaned_query_params.get('lt', None)
        ctx['selected_location_id'] = cleaned_query_params.get('location', None)

        qs = Listing.objects.get_published_listings()

        if form.is_valid():
            cd = form.cleaned_data
            ctx['category'] = cd.get('category')  # 'rent' if cd.get('property_type') == PROPERTY_TYPE_RENT else 'sale'

            if cd.get('location'):
                location_query_parts = []
                for location in cd['location']:
                    if location.is_city:
                        location_query_parts.append(Q(loc_city=location))
                    elif location.is_location:
                        location_query_parts.append(Q(loc_location=location))
                    elif location.is_sublocation:
                        location_query_parts.append(Q(loc_sub_location=location))

                if location_query_parts:
                    qs = qs.filter(reduce(operator.or_, location_query_parts))

            if cd.get('amenities'):
                amenities_query_parts = []
                for amenity in cd['amenities']:
                    amenities_query_parts.append(Q(amenities__contains=amenity))

                if amenities_query_parts:
                    qs = qs.filter(reduce(operator.or_, amenities_query_parts))

            if cd.get('category'):
                qs = qs.filter(category=cd['category'])

            if cd.get('venue'):
                qs = qs.filter(venue=cd['venue'])

            if cd.get('layout'):
                qs = qs.filter(layout=cd['layout'])

            if cd.get('people'):
                qs = qs.filter(capacity_min__lte=cd['people'])
                qs = qs.filter(capacity_max__gte=cd['people'])

            if cd.get('frequency') and cd.get('frequency') in dict(LISTING_FREQUENCIES):
                ctx['frequency'] = cd.get('frequency')

                if cd.get('frequency') == 'hourly':
                    qs = qs.filter(price_hourly__gte=1)
                if cd.get('frequency') == 'daily':
                    qs = qs.filter(price_daily__gte=1)
                if cd.get('frequency') == 'weekly':
                    qs = qs.filter(price_weekly__gte=1)
                if cd.get('frequency') == 'monthly':
                    qs = qs.filter(price_monthly__gte=1)
                if cd.get('frequency') == 'yearly':
                    qs = qs.filter(price_yearly__gte=1)

            # if cd.get('is_furnished'):
            #     qs = qs.filter(is_furnished=True)
            # if cd.get('is_fitted'):
            #     qs = qs.filter(is_fitted=True)

            # if cd.get('price_min'):
            #     qs = qs.filter(price__gte=cd['price_min'])
            # if cd.get('price_max'):
            #     qs = qs.filter(price__lte=cd['price_max'])

            # if cd.get('bedrooms_min'):
            #     qs = qs.filter(bedrooms__gte=cd['bedrooms_min'])
            # if cd.get('bedrooms_max'):
            #     qs = qs.filter(bedrooms__lte=cd['bedrooms_max'])

            # if cd.get('bedrooms') is not None and len(cd.get('bedrooms')):
            #     qs = qs.filter(bedrooms=cd['bedrooms'])

            # if cd.get('bathrooms_min') is not None:
            #     qs = qs.filter(bathrooms__gte=cd['bathrooms_min'])
            # if cd.get('bathrooms_max') is not None:
            #     qs = qs.filter(bathrooms__lte=cd['bathrooms_max'])

            # if cd.get('area_min'):
            #     qs = qs.filter(built_up_area__gte=cd['area_min'])
            # if cd.get('area_max'):
            #     qs = qs.filter(built_up_area__lte=cd['area_max'])

            # if cd.get('sort_order') is not None:
            #     if cd.get('sort_order') == SORT_ORDER_PRICE_ASC:
            #         qs = qs.order_by('-price')
            #     elif cd.get('sort_order') == SORT_ORDER_PRICE_DESC:
            #         qs = qs.order_by('price')
            #     else:
            qs = qs.order_by('-is_featured')

        paginator = Paginator(qs, 20)
        page_number = int(self.request.GET.get('page', 1))

        listings_page = paginator.get_page(page_number)
        ctx['listings'] = listings_page
        search_title = self.get_search_title_for_search_form(form)
        ctx['search_title'] = search_title

        ctx['page_title'], ctx['meta_description'] = self.get_page_title_and_meta_description(form, search_title)

        # Update impressions for all listings
        date = tz_now()
        for listing_id in listings_page.object_list.values_list('pk', flat=True):
            listing_stat, _ = ListingStats.objects.get_or_create(date=date, listing_id=listing_id)
            listing_stat.impressions = F('impressions') + 1
            listing_stat.save()

        location_tree = LocationTree()
        location_counts = qs.values('location_id').annotate(Count('location_id'))
        for location_count in location_counts:
            location = Location.objects.get(pk=location_count['location_id'])
            count = location_count['location_id__count']
            location_tree.add_location(location, count)

        location_facets = []

        ctx['filter_city_available'] = False
        ctx['filter_location_available'] = False
        ctx['filter_sublocation_available'] = False

        for location_id in location_tree.tree.expand_tree(mode=location_tree.tree.DEPTH):
            if location_id is 'root':
                continue

            node = location_tree.tree.get_node(location_id)
            location = node.data['location']

            facet_data = {
                'id': location.pk,
                'name': location.name,
                'slug': location.slug,
                'selected': search_location_tree.tree.get_node(location.pk) is not None,
                'count': node.data['count']
            }

            if location.is_city:
                facet_data['css_class'] = 'city'
                ctx['filter_city_available'] = True
            elif location.is_location:
                facet_data['css_class'] = 'location'
                ctx['filter_location_available'] = True
            else:
                facet_data['css_class'] = 'sublocation'
                ctx['filter_sublocation_available'] = True

            location_facets.append(facet_data)

        ctx['location_facets'] = location_facets
        ctx['user_favorites'] = self.get_user_favorites()
        ctx['qs'] = self.get_querystring()

        ctx['prev_page'] = False
        ctx['next_page'] = False
        ctx['current_page'] = page_number

        if page_number > 1:
            ctx['prev_page'] = page_number - 1

        if page_number < paginator.num_pages:
            ctx['next_page'] = page_number + 1

        return ctx

    def get_querystring(self):
        qs = []

        for key in self.request.GET:
            if key == 'page':
                continue

            val = self.request.GET.getlist(key)
            for v in val:
                qs.append('{}={}'.format(key, v))

        return '&'.join(qs)


class AgentsView(TemplateView):
    template_name = "portal/agents.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(AgentsView, self).get_context_data(**kwargs)

        ctx['agents'] = User.objects.filter(is_staff=True, is_active=True, userprofile__agent=True)

        return ctx


class AgentsDetailView(TemplateView):
    template_name = "portal/agents_detail.djhtml"

    def get_object(self):
        try:
            return User.objects.get(pk=self.kwargs['pk'], is_staff=True, is_active=True)
        except User.DoesNotExist:
            raise Http404()

    def get_context_data(self, **kwargs):
        ctx = super(AgentsDetailView, self).get_context_data(**kwargs)

        agent = self.get_object()

        ctx['agent'] = agent

        qs = Listing.objects.get_published_listings()
        qs = qs.filter(manager=agent)

        paginator = Paginator(qs, 10)
        page_number = self.request.GET.get('page', 1)

        ctx['listings'] = paginator.get_page(page_number)

        return ctx


class DetailView(TemplateView):
    template_name = "portal/detail.djhtml"

    def get_object(self):
        try:
            listing = Listing.objects.get(pk=self.kwargs['pk'])
        except Listing.DoesNotExist:
            raise Http404()
        else:
            return listing

    def get_context_data(self, **kwargs):
        ctx = super(DetailView, self).get_context_data(**kwargs)

        listing = self.get_object()
        date = tz_now()
        listing_stat, _ = ListingStats.objects.get_or_create(listing=listing, date=date)
        listing_stat.hits = F('hits') + 1
        listing_stat.save()

        ctx['listing'] = listing
        ctx['amenities'] = self.get_amenities(listing)

        ctx['meta_title'] = listing.meta_title or listing.title
        ctx['meta_description'] = listing.meta_description or listing.description

        qs = Listing.objects.get_published_listings()
        ctx['similar_listings'] = qs.filter(
            loc_location=listing.loc_location, category=listing.category
        ).exclude(id=listing.id)[:3]

        ctx['search_form'] = SearchForm()
        ctx['enquiry_form'] = ListingEnquiryForm()
        ctx['pricing_meta'] = self.get_pricing_meta()
        ctx['google_captcha_site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY

        ctx['is_favorite'] = False
        if self.request.user.is_authenticated:
            fav_listing = UserFavoriteListings.objects.filter(user=self.request.user, listing_id=listing.pk).count()
            ctx['is_favorite'] = True if fav_listing else False

        return ctx

    def get_pricing_meta(self):
        listing = self.get_object()
        price, freq, freq_display = listing.get_price_details()

        if listing.category == CATEGORY_MEETING_ROOMS and listing.price_daily:
            price = listing.price_daily
            freq_display = 'daily'

        if not price:
            price = 1

        in_dollars = price / 3.67

        return 'AED {} / $ {} {}'.format(
            "{:,.0f}".format(price),
            "{:,.0f}".format(in_dollars),
            freq_display)

    def get_amenities(self, listing):

        return [
            listing.amenities.choices.get(int(item))
            for item in listing.amenities
        ]

    def get(self, request, *args, **kwargs):
        listing = self.get_object()
        if listing.status == Listing.STATUS_DELETED:
            # Check if there are new versions of the listing we can show
            current_listing = listing
            while True:
                try:
                    current_listing = Listing.objects.get(previous_version=current_listing)
                except Listing.DoesNotExist:
                    break
                else:
                    if current_listing.status == Listing.STATUS_PUBLISHED:
                        return HttpResponseRedirect(reverse('portal:portal-detail', kwargs={
                            'slug': current_listing.slug,
                            'pk': current_listing.pk
                        }))

            return HttpResponse('This is not the listing you are looking for.', status=410)

        return super().get(request, *args, **kwargs)

    def post(self, request, **kwargs):
        form_data = request.POST.copy()
        listing = self.get_object()
        form_data['listing'] = listing.id
        form_data['message'] = clean_html(form_data['message'])

        form = ListingEnquiryForm(form_data)

        if form.is_valid():
            # captcha verification
            resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                'response': request.POST['g-recaptcha-response'],
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY
            })
            result_json = resp.json()

            if result_json['success']:
                if profanity.contains_profanity(form.cleaned_data['name']) or \
                   profanity.contains_profanity(form.cleaned_data['email']) or \
                   profanity.contains_profanity(form.cleaned_data['phone']) or \
                   profanity.contains_profanity(form.cleaned_data['message']) or \
                   len(set(form.cleaned_data['message'].split(' ')) & set(BANNED_WORDS)):

                    spam = SpamEnquiry(
                        name=form.cleaned_data['name'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                        message=form.cleaned_data['message'],
                        form='listing',
                        ip_address=get_user_ip(self.request)
                    )
                    spam.save()
                else:
                    form.save()

                    # if listing.company.send_email:
                    send_listing_email_on_successful_submission(form_data, listing)

                    # if listing.company.send_sms and listing.company.sms_mobile_number:
                    #     listing_url = "{}{}".format(settings.BASE_URL, listing.get_listing_url())
                    #     sms = SMSService()
                    #     sms_content = '{}, E:{}, P:{} is interested in '.format(
                    #         form_data['name'], form_data['email'], form_data['phone'], listing_url
                    #     )
                    #     sms.send_sms(
                    #         listing.company.sms_mobile_number,
                    #         sms_content
                    #     )

                response = {'success': True}
            else:
                response = {'success': False, 'errors': {'captcha': ['Please verify captcha.']}}
        else:
            response = {'success': False, 'errors': form.errors}

        date = tz_now()
        listing_stat, _ = ListingStats.objects.get_or_create(listing=listing, date=date)
        listing_stat.email_enquiries = F('email_enquiries') + 1
        listing_stat.save()

        return JsonResponse(response, safe=True)


class RegisterView(TemplateView):
    template_name = "portal/register.djhtml"


class CareersView(TemplateView):
    template_name = "portal/careers.djhtml"


class AboutView(TemplateView):
    template_name = "portal/about.djhtml"


class BaseContactView(FormView):
    form_class = ContactForm
    success_url = None
    form_type = None

    def has_email_or_link(self, message):
        regex_link = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        regex_email = r'[\w.+-]+@[\w-]+\.[\w.-]+'
        if len(re.findall(regex_link, message)) or len(re.findall(regex_email, message)):
            return True

        return False

    def send_emails(self, obj):
        email = EmailService()
        data = {
            'body': '',
            'type': self.form_type,
            'user_name': obj.name,
            'user_email': obj.email,
            'user_phone': obj.phone,
            'user_message': obj.message,
        }

        if self.form_type == ContactUsEnquiry.CONTACT_TYPE_LIST_VENUE:
            data['body'] = 'One of our staff member will get in touch with you to discuss about your space and how we can collect details in order to publish it on IdealSpaces.com'

        email.send_contact_emails(obj.email, obj.name, data)

    def form_valid(self, form, **kwargs):
        if profanity.contains_profanity(form.cleaned_data['name']) or \
           profanity.contains_profanity(form.cleaned_data['email']) or \
           profanity.contains_profanity(form.cleaned_data['phone']) or \
           profanity.contains_profanity(form.cleaned_data['message']) or \
           self.has_email_or_link(form.cleaned_data['message']):

            spam = SpamEnquiry(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                message=form.cleaned_data['message'],
                form='listvenue' if self.form_type == ContactUsEnquiry.CONTACT_TYPE_LIST_VENUE else 'contact',
                ip_address=get_user_ip(self.request)
            )
            spam.save()
        else:
            obj = form.save()

            obj.contact_type = self.form_type
            obj.save()

            self.send_emails(obj)

        return super().form_valid(form)


class ListVenueView(BaseContactView):
    template_name = "portal/list_venue_form.djhtml"
    success_url = "/f/s/list/"
    form_type = ContactUsEnquiry.CONTACT_TYPE_LIST_VENUE

    def get_context_data(self, **kwargs):
        ctx = super(ListVenueView, self).get_context_data(**kwargs)
        ctx['google_captcha_site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY

        return ctx


class ContactView(BaseContactView):
    template_name = "portal/contact.djhtml"
    success_url = "/f/s/contact/"
    form_type = ContactUsEnquiry.CONTACT_TYPE_CONTACT_FORM

    def get_context_data(self, **kwargs):
        ctx = super(ContactView, self).get_context_data(**kwargs)
        ctx['google_captcha_site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY

        return ctx


class TermsView(TemplateView):
    template_name = "portal/terms.djhtml"


class PolicyView(TemplateView):
    template_name = "portal/policy.djhtml"


class SellForAFixedFee(TemplateView):
    template_name = "portal/sell_for_a_fixed_fee.djhtml"


class HowitWorks(TemplateView):
    template_name = "portal/how_it_works.djhtml"


class CancellationPolicyView(TemplateView):
    template_name = "portal/cancellation_policy.djhtml"


class WhatsIncluded(TemplateView):
    template_name = "portal/whats_included.djhtml"


class FaqsView(TemplateView):
    template_name = "portal/faqs.djhtml"


class WhyUsView(TemplateView):
    template_name = "portal/whyus.djhtml"


class RentForAFixedFeeView(TemplateView):
    template_name = "portal/rent_for_a_fixed_fee.djhtml"


class PlansView(TemplateView):
    template_name = "account/plans.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(PlansView, self).get_context_data(**kwargs)

        ctx['packages'] = settings.PACKAGES

        return ctx


class LocationsListView(APIView):
    def get(self, request):
        locations = cache.get('locations')
        if not locations:
            locations = {}
            for location in Location.objects.all():
                location_info = {
                    'name': location.name,
                    'slug': location.slug,
                    'id': location.pk
                }
                if location.parent:
                    location_info['parent'] = location.parent.id

                locations[location.pk] = location_info

            cache.set('locations', locations)

        return Response(locations)


class RecordCallEnquiryView(View):
    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk)

        date = tz_now()
        listing_stat, _ = ListingStats.objects.get_or_create(listing=listing, date=date)
        listing_stat.call_enquiries = F('call_enquiries') + 1
        listing_stat.save()

        return HttpResponse()
