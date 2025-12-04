import datetime

from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver
from django.contrib.auth.models import User

from s3direct.fields import S3DirectField


class Company(models.Model):
    TYPES = (
        ('business center', 'Business Center'),
        ('hotel', 'Hotel'),
        ('outdoor', 'Outdoor'),
        ('stadium', 'Stadium'),
        ('restaurant', 'Restaurant'),
        ('conference centers', 'Conference Centers'),
        ('club and bars', 'Club and/or Bars'),
        ('art gallery', 'Art Galleries'),
        ('others', 'Others'),
    )

    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)

    inquiry_email = models.EmailField(blank=True)

    company_type = models.CharField(max_length=30, choices=TYPES, default='others')

    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)

    sms_mobile_number = models.CharField(max_length=20, blank=True)

    active = models.BooleanField(default=True)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class CompanyContract(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contracts')

    listings_allowed = models.SmallIntegerField(default=0)
    featured_allowed = models.SmallIntegerField(default=0)

    start_date = models.DateField(blank=True)
    expiry_date = models.DateField(blank=True)

    def __str__(self):
        return self.company.name

    @property
    def expired(self):
        return self.expiry_date < datetime.date.today()


class CompanyPayment(models.Model):
    MODES = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank transfer', 'Bank Transfer'),
        ('others', 'Others'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments')

    reference = models.CharField(max_length=50, blank=True)

    amount = models.SmallIntegerField(default=0)
    mode = models.CharField(max_length=20, choices=MODES, default='cash')

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company.name


class UserProfile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100, blank=True)

    about = models.TextField(blank=True)

    # logo = S3DirectField(dest="user_assets", blank=True)

    def get_default_image(self):
        return self.logo if self.logo else '/static/img/search_default.png'

    def __str__(self):
        return "{}:{}".format(self.user.pk, self.user)


class UserAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    title = models.CharField(max_length=50, blank=True)
    url = S3DirectField(dest="user_assets")

    def __str__(self):
        return "{}:{}".format(self.user.pk, self.user)


class UserFavoriteListings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey("portal.Listing", on_delete=models.CASCADE)

    date_added = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Favorite Listing'
        verbose_name_plural = 'User Favorite Listings'

    def __str__(self):
        return "{}:{}".format(self.user, self.listing.title)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
