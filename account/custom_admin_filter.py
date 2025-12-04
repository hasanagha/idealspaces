from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User


class UserFilter(SimpleListFilter):
    title = 'user'
    parameter_name = 'user__id'

    def lookups(self, request, model_admin):
        return [(u.id, u.username) for u in User.objects.filter(is_staff=False, is_superuser=False)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id__exact=self.value())


class ManagerFilter(SimpleListFilter):
    title = 'manager'
    parameter_name = 'manager__id'

    def lookups(self, request, model_admin):
        return [(u.id, u.username) for u in User.objects.filter(is_staff=True)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(manager__id__exact=self.value())


class ManagerForListingEnquiriesFilter(SimpleListFilter):
    title = 'manager'
    parameter_name = 'manager__id'

    def lookups(self, request, model_admin):
        return [(u.id, u.username) for u in User.objects.filter(is_staff=True)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(listing__manager_id=self.value())


class SuperUserFilter(SimpleListFilter):
    title = 'superuser'
    parameter_name = 'user__id'

    def lookups(self, request, model_admin):
        return [(u.id, u.username) for u in User.objects.filter(is_superuser=True)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id__exact=self.value())
