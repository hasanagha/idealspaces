from django.conf import settings
from django.urls import reverse

from django.db import models

from s3direct.fields import S3DirectField

from .settings import COMMENT_STATUS_PENDING, COMMENT_STATUS_APPROVED, COMMENT_STATUS_DELETED
from .settings import POST_STATUS_PUBLISHED, POST_STATUS_UNPUBLISHED, POST_STATUS_DRAFT


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_meta_title(self):
        return self.meta_title or self.name

    def get_meta_description(self):
        return self.meta_description

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }

        return reverse('speedyblog:blog_category', kwargs=kwargs)

    def get_posts_count(self):
        return Post.objects.filter(category=self, status=POST_STATUS_PUBLISHED).count()


class Post(models.Model):
    STATUSES = (
        (POST_STATUS_PUBLISHED, 'Published'),
        (POST_STATUS_UNPUBLISHED, 'Unpublished'),
        (POST_STATUS_DRAFT, 'Draft'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField()

    status = models.CharField(max_length=1, choices=STATUSES, default=POST_STATUS_PUBLISHED, db_index=True)

    image = S3DirectField(dest="user_assets", blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    allow_comments = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.title

    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_description or self.description

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }

        return reverse('speedyblog:blog_detail', kwargs=kwargs)

    def get_comments_count(self):
        return Comment.objects.filter(post=self, status=COMMENT_STATUS_APPROVED).count()


class Comment(models.Model):
    STATUSES = (
        (COMMENT_STATUS_PENDING, 'Pending'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_DELETED, 'Deleted')
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()

    created_on = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(default='0.0.0.0')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=50, default='anonymous')
    user_email = models.EmailField(blank=True)

    status = models.CharField(max_length=1, choices=STATUSES, default=COMMENT_STATUS_PENDING, db_index=True)

    def __str__(self):
        return self.comment

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ['created_on']
