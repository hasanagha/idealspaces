from django.urls import re_path

from speedyblog.views import BlogCategoryView
from speedyblog.views import BlogDetailView
from speedyblog.views import BlogListView


app_name = "speedyblog"

urlpatterns = [
    re_path(
        r'^(?P<slug>[-_\w]+)/$',
        BlogDetailView.as_view(),
        name='blog_detail'
    ),
    re_path(r'^category/(?P<slug>[-_\w]+)/$', BlogCategoryView.as_view(), name='blog_category'),
    re_path(r'^$', BlogListView.as_view(), name='blog_index'),
]
