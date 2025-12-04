"""shapp URL Configuration"""
from django.urls import path
from django.urls import include
from django.contrib import admin


urlpatterns = [
    # path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    # path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS

    path('', include('portal.urls')),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('blog/', include('speedyblog.urls')),
    # Third party library
    path('s3direct/', include('s3direct.urls')),
    # path('admin/runas/', include('runas.urls')),
]
