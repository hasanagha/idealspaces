import datetime

from django.contrib import admin
from django.utils.safestring import mark_safe

from account.models import UserProfile, UserAsset, Company, CompanyContract, CompanyPayment
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class UserFavoriteListingsModelAdmin(admin.ModelAdmin):
    list_display = ["user", "date_added"]


class CompanyModelAdmin(admin.ModelAdmin):
    list_display = ["name", "company_type", "send_email", "send_sms", "active", "created_on"]
    list_filter = ["active", "company_type"]
    search_fields = ["name", "address"]


class CompanyContractModelAdmin(admin.ModelAdmin):
    list_display = ["company", "listings_allowed", "featured_allowed", "start_date", "expiry_date", "expired"]
    list_filter = ["company"]
    search_fields = ["company__name"]

    def expired(self, obj):
        if obj.expiry_date > datetime.date.today():
            html = '<img src="/static/admin/img/icon-yes.svg" alt="Yes">'
        else:
            html = '<img src="/static/admin/img/icon-no.svg" alt="No">'

        return mark_safe(html)

    expired.short_description = 'Contract Expired'


class CompanyPaymentModelAdmin(admin.ModelAdmin):
    list_display = ["company", "amount", "reference", "mode", "created_on"]
    list_filter = ["company", "mode"]
    search_fields = ["company__name", "reference", "mode"]


class UserProfileInline(admin.StackedInline):
    inlines = [UserAsset]
    model = UserProfile
    max_num = 1
    can_delete = False


class UserAssetsInline(admin.TabularInline):
    model = UserAsset


class AccountsUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "is_staff", "date_joined"]
    inlines = [UserProfileInline, UserAssetsInline]


# unregister old user admin
admin.site.unregister(User)
# # register new user admin that includes a UserProfile
admin.site.register(User, AccountsUserAdmin)
admin.site.register(Company, CompanyModelAdmin)
admin.site.register(CompanyContract, CompanyContractModelAdmin)
admin.site.register(CompanyPayment, CompanyPaymentModelAdmin)

# admin.site.register(UserProfile, UserProfileModelAdmin)
