from django.contrib import admin
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.db import models as django_models
from pagedown.widgets import AdminPagedownWidget

from portal.models import ContactUsEnquiry
from portal.models import Listing
from portal.models import ListingAsset, ListingPricing
from portal.models import ListingEnquiry
from portal.models import Location, SpamEnquiry

from account.custom_admin_filter import ManagerFilter, ManagerForListingEnquiriesFilter


class LocationModelAdmin(admin.ModelAdmin):
    list_display = ["name", "is_city", "is_location", "is_sublocation", "status"]
    list_filter = ["status", "is_city", "is_location", "is_sublocation"]
    search_fields = ["name"]


class SpamAdminModel(admin.ModelAdmin):
    list_display = ["name", "email", "email", "phone", "form", "ip_address", "message"]
    list_filter = ["form"]
    search_fields = ["name", "email", "email", "phone", "form", "ip_address"]


class ListingAssetModelAdmin(admin.TabularInline):
    model = ListingAsset


class ListingPricingModelAdmin(admin.TabularInline):
    model = ListingPricing


class ListingEnquiryModelAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "listing_tag", "listing_manager", "status", "created_on"]
    list_filter = [ManagerForListingEnquiriesFilter, "listing", "status"]
    search_fields = ["name", "email", "phone"]

    def get_queryset(self, request):
        qs = super(ListingEnquiryModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(listing__manager=request.user)

    def listing_tag(self, obj):
        return mark_safe('<a href="/admin/portal/listing/{}/change/" target="_blank">{}</a>'.format(
            obj.listing.id,
            obj.listing
        ))

    listing_tag.short_description = 'Listing'

    def listing_manager(self, obj):
        return obj.listing.manager.get_full_name() if obj.listing.manager else '-'

    listing_manager.short_description = 'Manager'


class ContactUsEnquiryModelAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "contact_type", "phone", "status", "created_on"]
    list_filter = ["status", "contact_type"]
    search_fields = ["name", "email", "phone"]


class ListingModelAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "location", "venue", "category", "reference_tag", "listing_manager",
                    "status", "created_on", "live_link"]
    list_filter = [ManagerFilter, "company", "status", "location", "category"]
    search_fields = ["title", "venue", "category", "company__name"]
    readonly_fields = ['get_difference_from_previous_version', 'view_on_live']
    formfield_overrides = {django_models.TextField: {'widget': AdminPagedownWidget}, }

    inlines = [
        ListingAssetModelAdmin, ListingPricingModelAdmin
    ]

    def get_queryset(self, request):
        qs = super(ListingModelAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs

        return qs.filter(manager=request.user)

    def reference_tag(self, obj):
        return obj.get_reference_code()

    reference_tag.short_description = 'Reference Code'

    def live_link(self, obj):
        if obj.pk:
            return mark_safe('<a href="{}" target="_blank">Click to view</a>'.format(
                obj.get_listing_url()
            ))

        return None

    live_link.short_description = 'Live'

    def listing_manager(self, obj):
        return obj.manager.get_full_name() if obj.manager else '-'

    listing_manager.short_description = 'Manager'

    def get_difference_from_previous_version(self, obj):
        previous_version = obj.previous_version
        different_fields = []

        for field in ['location', 'property_type', 'category', 'title', 'description', 'reference_code',
                      'rera_permit_number', 'is_furnished', 'is_fitted', 'price', 'bedrooms', 'bathrooms',
                      'built_up_area', 'plot_area', 'amenities']:
            if getattr(obj, field) != getattr(previous_version, field):
                different_fields.append(field)

        if obj.assets.all().values_list('pk', flat=True) != previous_version.assets.all().values_list('pk', flat=True):
            different_fields.append('images')

        return ', '.join(different_fields)

    get_difference_from_previous_version.verbose_name = 'Difference from previous version'

    def view_on_live(self, obj):
        if obj.pk:
            return mark_safe('<a href="{}" target="_blank" class="historylink">Click to view on portal</a>'.format(
                obj.get_listing_url()
            ))

        return '-'

    view_on_live.verbose_name = 'Difference from previous version'

    class Media:
        css = {
            'all': (static('css/custom-admin.css'),),
        }

        js = (static('libs/tinymce/jquery.tinymce.min.js'), static('js/admin.js'),)


admin.site.register(Location, LocationModelAdmin)
admin.site.register(SpamEnquiry, SpamAdminModel)
admin.site.register(Listing, ListingModelAdmin)
admin.site.register(ListingEnquiry, ListingEnquiryModelAdmin)
admin.site.register(ContactUsEnquiry, ContactUsEnquiryModelAdmin)

admin.site.site_header = "SuperAdmin - Ideal Spaces"
