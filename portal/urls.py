from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from django.contrib.sitemaps.views import sitemap

# from portal.views import FaqsView
# from portal.views import CareersView
from portal.views import AboutView, RecordCallEnquiryView
from portal.views import ContactView
from portal.views import ListVenueView
from portal.views import DetailView
from portal.views import HomeView, LocationsListView
from portal.views import LandlordView
from portal.views import HowitWorks
from portal.views import PolicyView
from portal.views import RegisterView
from portal.views import SearchView
from portal.views import SellForAFixedFee
# from portal.views import TermsView
from portal.views import WhatsIncluded
from portal.views import AgentsView
from portal.views import AgentsDetailView
from portal.views import PlansView
from portal.views import WhyUsView
from portal.views import CancellationPolicyView
from portal.views import RentForAFixedFeeView
from portal.views import FormSubmittedView

from portal.sitemaps import ListingSitemap, BlogSitemap

app_name = 'portal'

sitemaps = {
    'properties': ListingSitemap,
    'blogs': BlogSitemap,
}

urlpatterns = [
    path('', HomeView.as_view(), name="portal-home"),
    path('landlords/', LandlordView.as_view(), name="portal-landlords"),

    re_path(r"^s/$", SearchView.as_view(), name="portal-search"),
    re_path(r'^s/(?P<category>(serviced-offices|banquet-halls|coworking-spaces|meeting-rooms))/$',
        SearchView.as_view(),
        kwargs={
            'sef': True
        }, name='search-by-category'),
    re_path(r'^s/(?P<category>(serviced-offices|banquet-halls|coworking-spaces|meeting-rooms))/(?P<city>[a-z0-9\-]+)/$',
        SearchView.as_view(),
        kwargs={
            'sef': True
        }),
    re_path(r'^s/(?P<category>(serviced-offices|banquet-halls|coworking-spaces|meeting-rooms))/(?P<city>[a-z0-9\-]+)/'
        r'(?P<location>[a-z0-9\-]+)/$',
        SearchView.as_view(),
        kwargs={
            'sef': True
        }),
    re_path(r'^s/(?P<category>(serviced-offices|banquet-halls|coworking-spaces|meeting-rooms))/(?P<city>[a-z0-9\-]+)/'
        r'(?P<location>[a-z0-9\-]+)/(?P<sublocation>[a-z0-9\-]+)/$',
        SearchView.as_view(),
        kwargs={
            'sef': True
        }),

    re_path(r'^s/(?P<city>[a-z0-9\-]+)/$',
        SearchView.as_view(),
        kwargs={
            'sef': True
        }),
    re_path(r'^s/(?P<city>[a-z0-9\-]+)/(?P<location>[a-z0-9\-]+)/$',
        SearchView.as_view(),
        kwargs={
            'sef': True
        }),
    re_path(r'^s/(?P<city>[a-z0-9\-]+)/(?P<location>[a-z0-9\-]+)/'
        r'(?P<sublocation>[a-z0-9\-]+)/$',
        SearchView.as_view(),
        kwargs={
            'sef': True
        }),

    # re_path(r'(?P<venue_type>(business-center|hotels))/(?P<category>(serviced-offices|banquet-halls|coworking-spaces|meeting-rooms))/(?P<slug>[^/]+)-(?P<pk>\d+)/', DetailView.as_view(), name="portal-detail"),
    re_path(r'(?P<category>(serviced-offices|banquet-halls|coworking-spaces|meeting-rooms))/(?P<slug>[^/]+)-(?P<pk>\d+)/', DetailView.as_view(), name="portal-detail"),
    re_path(r'(?P<slug>[^/]+)-(?P<pk>\d+)/', DetailView.as_view(), name="portal-detail"),
    path('register/', RegisterView.as_view(), name="register"),

    re_path(r'agents/(?P<pk>\d+)/', AgentsDetailView.as_view(), name="agents-detail"),
    path('agents/', AgentsView.as_view(), name="agents"),

    # Sell Menu Urls
    path('sell/sell-for-a-fixed-fee/', SellForAFixedFee.as_view(), name="sell-for-a-fixed-fee"),
    path('sell/how-it-works/', HowitWorks.as_view(), name="sell-how-it-works"),
    path('sell/whats-included/', WhatsIncluded.as_view(), name="whats-included"),

    # Rent Menu Urls
    path('why-list-with-us/', WhyUsView.as_view(), name="why-us"),
    path('rent/rent-for-a-fixed-fee/', RentForAFixedFeeView.as_view(), name="rent-for-a-fixed-fee"),
    path('rent/how-it-works/', HowitWorks.as_view(), name="rent-how-it-works"),

    # Original
    path('about', AboutView.as_view(), name="about"),
    # path('terms-and-conditions', TermsView.as_view(), name="terms"),
    path('privacy-policy', PolicyView.as_view(), name="policy"),
    path('contact', ContactView.as_view(), name="contact"),
    path('cancellation-policy', CancellationPolicyView.as_view(), name="cancellation-policy"),
    path('list-your-space', ListVenueView.as_view(), name="list-space"),

    re_path(r'f/s/(?P<type>[^/]+)/', FormSubmittedView.as_view(), name="form-submitted"),

    path('record-call/<int:pk>/', csrf_exempt(RecordCallEnquiryView.as_view()), name='record-call'),
    path('locations/', LocationsListView.as_view(), name='locations-list'),
    path('plans/buy/', PlansView.as_view(), name='plans-buy'),

    # the sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
