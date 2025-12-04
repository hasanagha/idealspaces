from django.contrib.sitemaps import Sitemap
from speedyblog.models import Post
from speedyblog.settings import POST_STATUS_PUBLISHED
from portal.models import Listing


class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.filter(status=POST_STATUS_PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_on


class ListingSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Listing.objects.filter(status=Listing.STATUS_PUBLISHED, approval_status=Listing.APPROVAL_STATUS_APPROVED)

    def lastmod(self, obj):
        return obj.updated_on
