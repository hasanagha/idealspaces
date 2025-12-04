from django.contrib import admin
from django.db import models as django_models
from pagedown.widgets import AdminPagedownWidget

from speedyblog.models import Category, Post, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_on')


class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {django_models.TextField: {'widget': AdminPagedownWidget}, }
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'created_on', 'posted_by', 'allow_comments')


class CommentAdmin(admin.ModelAdmin):
    formfield_overrides = {django_models.TextField: {'widget': AdminPagedownWidget}, }
    list_display = ('user_name', 'user_email', 'ip_address', 'created_on')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
