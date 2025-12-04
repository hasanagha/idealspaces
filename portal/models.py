from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField
from s3direct.fields import S3DirectField

from django.contrib.humanize.templatetags.humanize import naturalday

from account.models import Company

from shapp.constants import LISTING_CATEGORIES, LISTING_LAYOUTS, LISTING_VENUES, LISTING_AMENITIES
from shapp.constants import LISTING_FREQUENCIES_PREFIX, LISTING_FREQUENCIES, CATEGORY_MEETING_ROOMS


class Location(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, db_index=True)

    is_city = models.BooleanField(default=False)
    is_location = models.BooleanField(default=False)
    is_sublocation = models.BooleanField(default=False)

    latitude = models.FloatField(max_length=15, null=True)
    longitude = models.FloatField(max_length=15, null=True)

    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ListingManager(models.Manager):
    def get_published_listings(self):
        return self.filter(status='published', company__active=True)


class Listing(models.Model):
    STATUS_PUBLISHED = 'published'
    # STATUS_DRAFT = 'draft'
    STATUS_UNPUBLISHED = 'unpublished'
    STATUS_DELETED = 'deleted'
    STATUSES = (
        # (STATUS_DRAFT, 'Draft'),
        (STATUS_DELETED, 'Deleted'),
        (STATUS_UNPUBLISHED, 'Unpublished'),
        (STATUS_PUBLISHED, 'Published')
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    objects = ListingManager()

    status = models.CharField(max_length=50, choices=STATUSES, db_index=True)

    manager = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, null=True, blank=True)

    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    loc_city = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL, related_name='+', editable=False)
    loc_location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL, related_name='+', editable=False)
    loc_sub_location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL, related_name='+',
                                         editable=False)

    venue = models.CharField(max_length=50, choices=LISTING_VENUES)
    category = models.CharField(max_length=50, choices=LISTING_CATEGORIES)
    layout = MultiSelectField(choices=LISTING_LAYOUTS, blank=True)

    title = models.CharField(max_length=500)

    meta_title = models.CharField(max_length=500, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    address = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=600)
    description = models.TextField(blank=True)
    reference_code = models.CharField(max_length=100, blank=True)
    parking = models.CharField(max_length=100, blank=True)
    deposit = models.CharField(max_length=100, blank=True)
    minimum_terms = models.CharField(max_length=100, blank=True)

    is_featured = models.BooleanField(default=False)

    area = models.FloatField(null=True)

    price_hourly = models.PositiveIntegerField(default=0)
    price_daily = models.PositiveIntegerField(default=0)
    price_weekly = models.PositiveIntegerField(default=0)
    price_monthly = models.PositiveIntegerField(default=0)
    price_yearly = models.PositiveIntegerField(default=0)

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    capacity_min = models.PositiveIntegerField()
    capacity_max = models.PositiveIntegerField()

    amenities = MultiSelectField(max_length=100, choices=LISTING_AMENITIES, blank=True)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "space"
        verbose_name_plural = "spaces"

    def __str__(self):
        return self.title

    def get_reference_code(self):
        return "{}/00{}".format(
            self.category,
            self.pk
        )

    def get_price_display(self):
        price, frequency, frequency_display = self.get_price_details()

        return '{} <span class="price-frequency-display">{}</span>'.format("{:,}".format(price), frequency)

    def get_price_details(self):
        price = 0
        frequency = 'per month'
        frequency_display = 'monthly'

        if self.price_monthly:
            price = self.price_monthly

        if self.price_hourly:
            price = self.price_hourly
            frequency = 'per hour'
            frequency_display = 'hourly'

        if self.price_daily:
            price = self.price_daily
            frequency = 'per day'
            frequency_display = 'daily'

        if self.price_weekly:
            price = self.price_weekly
            frequency = 'per week'
            frequency_display = 'weekly'

        if self.price_yearly:
            price = self.price_yearly
            frequency = 'per year'
            frequency_display = 'yearly'

        if self.category == CATEGORY_MEETING_ROOMS and self.price_hourly:
            price = self.price_hourly
            frequency = 'per hour'
            frequency_display = 'hourly'

        return price, frequency, frequency_display

    def get_images(self):
        return self.assets.filter(asset_type=ListingAsset.ASSET_TYPE_IMAGE).order_by('order')

    def get_default_image(self):
        images = self.get_images()

        return images.first().url if images else '/static/img/search_default.png'

    def get_videos(self):
        return self.assets.filter(asset_type=ListingAsset.ASSET_TYPE_VIDEO)

    def get_floorplans(self):
        return self.assets.filter(asset_type=ListingAsset.ASSET_TYPE_FLOORPLANS).order_by('id')

    def get_listing_url(self):
        slug = self.slug.lower()
        kwargs = {
            'pk': self.pk,
            'slug': slug,
            'category': self.category,
        }

        return reverse('portal:portal-detail', kwargs=kwargs)

    def get_absolute_url(self):
        return self.get_listing_url()

    def get_latitude(self):
        if self.latitude:
            return self.latitude

        if self.location.latitude:
            return self.location.latitude
        else:
            return self.location.parent.latitude

    def get_longitude(self):
        if self.longitude:
            return self.longitude

        if self.location.longitude:
            return self.location.longitude
        else:
            return self.location.parent.longitude

    def get_location(self):
        if self.location.is_sublocation:
            return "{}, {}, {}".format(
                self.location,
                self.location.parent,
                self.location.parent.parent
            )
        elif self.location.is_location:
            return "{}, {}".format(
                self.location,
                self.location.parent
            )

        return self.location

    def get_amenities(self):

        return [
            self.amenities.choices.get(int(item))
            for item in self.amenities
        ]

    def save(self, *args, **kwargs):
        self.loc_city = None
        self.loc_location = None
        self.loc_sub_location = None

        if self.location.is_city:
            self.loc_city = self.location
        elif self.location.is_location:
            self.loc_city = self.location.parent
            self.loc_location = self.location
        elif self.location.is_sublocation:
            self.loc_city = self.location.parent.parent
            self.loc_location = self.location.parent
            self.loc_sub_location = self.location

        # # Handle the logic for promoting a listing to approved and removing the old version here
        # if self.previous_version is not None and self.pk:
        #     old_self = Listing.objects.get(pk=self.pk)
        #     if (
        #         self.approval_status == Listing.APPROVAL_STATUS_APPROVED and
        #         old_self.approval_status != Listing.APPROVAL_STATUS_APPROVED
        #     ):
        #         self.previous_version.status = Listing.STATUS_DELETED
        #         self.previous_version.slot = None
        #         self.previous_version.save()

        super(Listing, self).save(*args, **kwargs)

    # def has_new_version_in_review(self):
        # return Listing.objects.filter(previous_version=self, approval_status=Listing.APPROVAL_STATUS_REVIEW)


class ListingAsset(models.Model):
    ASSET_TYPE_IMAGE = 'image'
    # ASSET_TYPE_VIDEO = 'video'
    # ASSET_TYPE_FLOORPLANS = 'floorplan'

    ASSET_TYPES = (
        (ASSET_TYPE_IMAGE, 'Image'),
        # ('F', 'Floor Plans'),
        # ('V', 'Video'),
    )

    asset_type = models.CharField(max_length=50, choices=ASSET_TYPES)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='assets')
    url = S3DirectField(dest="listing_assets")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "space asset"
        verbose_name_plural = "space assets"

    def __str__(self):
        return self.asset_type


class ListingPricing(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='pricing')
    frequency_prefix = models.CharField(max_length=50, choices=LISTING_FREQUENCIES_PREFIX, blank=True)
    frequency = models.CharField(max_length=50, choices=LISTING_FREQUENCIES)
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.frequency

    class Meta:
        verbose_name = "space pricing"
        verbose_name_plural = "spaces pricings"


class ListingEnquiry(models.Model):
    ENQUIRY_STATUS_NEW = 'new'
    ENQUIRY_STATUS_CLOSED = 'closed'
    ENQUIRY_STATUS_WORKING = 'working'
    ENQUIRY_STATUS_SPAM = 'spam'

    STATUSES = (
        (ENQUIRY_STATUS_NEW, 'New'),
        (ENQUIRY_STATUS_CLOSED, 'Closed'),
        (ENQUIRY_STATUS_WORKING, 'Working'),
        (ENQUIRY_STATUS_SPAM, 'Spam'),
    )

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)

    status = models.CharField(max_length=50, choices=STATUSES, default=ENQUIRY_STATUS_NEW)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return "{}[{}]".format(self.name, self.email)

    class Meta:
        verbose_name = 'Space Inquiry'
        verbose_name_plural = 'Space Inquiries'

    def created_on_days_ago(self):
        return naturalday(self.created_on).title()


class ContactUsEnquiry(models.Model):
    CONTACT_STATUS_NEW = 'new'
    CONTACT_STATUS_PROCESSED = 'closed'
    CONTACT_STATUS_SPAM = 'spam'
    CONTACT_STATUS_WORKING = 'working'

    STATUSES = (
        (CONTACT_STATUS_NEW, 'New'),
        (CONTACT_STATUS_PROCESSED, 'Closed'),
        (CONTACT_STATUS_WORKING, 'Working'),
        (CONTACT_STATUS_SPAM, 'Spam'),
    )

    CONTACT_TYPE_LIST_VENUE = 'listvenueform'
    CONTACT_TYPE_CONTACT_FORM = 'contactform'

    CONTACT_TYPES = (
        (CONTACT_TYPE_LIST_VENUE, 'List Venue Form'),
        (CONTACT_TYPE_CONTACT_FORM, 'Contact Us Form')
    )

    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=50, blank=True)
    message = models.TextField(blank=True)

    contact_type = models.CharField(max_length=50, choices=CONTACT_TYPES, default=CONTACT_TYPE_CONTACT_FORM)

    status = models.CharField(max_length=50, choices=STATUSES, default=CONTACT_STATUS_NEW)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Form Inquiry'
        verbose_name_plural = 'Contact Form Inquiries'

    def __str__(self):
        return "{}[{}]".format(self.name, self.email)


class SpamEnquiry(models.Model):
    FORMS = (
        ('listing', 'Listing'),
        ('contact', 'Contact'),
        ('listvenue', 'List Venue'),
    )

    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, blank=True)
    message = models.TextField(blank=True)

    form = models.CharField(max_length=10, choices=FORMS, default='listing')

    ip_address = models.CharField(max_length=20, blank=True)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.email)

    class Meta:
        verbose_name = 'Spam'
        verbose_name_plural = 'Spams'


class ListingStats(models.Model):
    date = models.DateField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    impressions = models.PositiveIntegerField(default=0)
    hits = models.PositiveIntegerField(default=0)

    email_enquiries = models.PositiveIntegerField(default=0)
    call_enquiries = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('date', 'listing')
