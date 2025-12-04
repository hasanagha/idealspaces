import requests

from django.http import Http404
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic.dates import DateDetailView
from django.views.generic import TemplateView, DetailView

from speedyblog.forms import CommentForm
from speedyblog.models import Comment, Post, Category

from shapp.helpers import get_client_ip

from speedyblog.settings import COMMENT_STATUS_APPROVED, POST_STATUS_PUBLISHED


class BlogListView(TemplateView):
    template_name = 'speedyblog/post_list_page.html'

    def get_context_data(self, **kwargs):
        ctx = super(BlogListView, self).get_context_data(**kwargs)

        ctx['posts'] = Post.objects.filter(status=POST_STATUS_PUBLISHED).select_related().order_by('-created_on')
        ctx['categories'] = Category.objects.all().order_by('name')

        return ctx


class BlogCategoryView(TemplateView):
    template_name = 'speedyblog/post_list_page.html'

    def get_context_data(self, **kwargs):
        slug = kwargs['slug']
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExists:
            raise Http404()

        ctx = super(BlogCategoryView, self).get_context_data(**kwargs)
        ctx['posts'] = Post.objects.filter(status=POST_STATUS_PUBLISHED, category=category).select_related()
        ctx['selected_category'] = category
        ctx['categories'] = Category.objects.all().order_by('name')

        return ctx


class BlogDetailView(DetailView):
    model = Post
    field_name = 'slug'
    page_template = "speedyblog/post_detail_page.html"

    def get_queryset(self):
        queryset = super(BlogDetailView, self).get_queryset()

        return queryset.select_related()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        post = self.object

        form = CommentForm(request.POST)

        context = self.get_context_data(object=post)
        context['comment_form'] = form

        if form.is_valid():

            if not self.verify_captcha(request):
                context['invalid_captcha'] = True
                return self.render_to_response(context)

            comment = form.save(commit=False)
            comment.post = post

            comment.ip = get_client_ip(request)
            comment.save()

            return redirect("{}?success=1".format(post.get_absolute_url()))

        return self.render_to_response(context)

    def verify_captcha(self, request):
        payload = {
            'response': request.POST['g-recaptcha-response'],
            'remoteip': get_client_ip(request),
            'secret': settings.CAPTCHA_SECRET_KEY
        }

        response = requests.post('https://www.google.com/recaptcha/api/siteverify', payload)

        if response.status_code == 200:
            response = response.json()
        else:
            return False

        return response['success']

    def get_context_data(self, **kwargs):
        form = CommentForm()

        context = {
            'page_template': self.page_template,
            'comment_form': form,
            'categories': Category.objects.all().order_by('name'),
            'post_url': '{}{}'.format(settings.BASE_URL, self.object.get_absolute_url()),
            'comments': Comment.objects.filter(
                post=self.object.id, status=COMMENT_STATUS_APPROVED
            ).select_related()
        }

        return super(BlogDetailView, self).get_context_data(**context)

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template depending if the request is ajax
        or not and it renders with the given context.
        """
        if self.request.is_ajax():
            template = self.page_template
        else:
            template = self.get_template_names()

        return self.response_class(
            request=self.request,
            template=template,
            context=context,
            **response_kwargs
        )
