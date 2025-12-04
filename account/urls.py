from django.conf import settings
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordResetConfirmView

from django.views.decorators.csrf import csrf_exempt

from account.views import ActivateView, EditListingView
from account.views import UnpublishListingView, PublishListingView, DeleteListingView
from account.views import DashboardView
from account.views import PlansView
from account.views import ProfilePasswordChangeView
from account.views import ProfileView
from account.views import RegisterSuccessView
from account.views import RegisterView
from account.views import AddListingView
from account.views import UserFavoritesView
from account.views import UserListingsView
from account.views import DocumentUploadView
from account.views import UserFavoriteListingUpdateView
from account.views import ListingSuccessView
from account.views import InquiriesView
from account.views import ContractsView
from account.views import StatsView


app_name = 'account'

urlpatterns = [
    path('', DashboardView.as_view(), name="user-dashboard"),
    path('profile/', ProfileView.as_view(), name="user-profile"),
    path('password/', ProfilePasswordChangeView.as_view(), name="user-change-password"),
    path('listings/', UserListingsView.as_view(), name="user-listings"),
    path('inquiries/', InquiriesView.as_view(), name="listing-inquiries"),
    path('contracts/', ContractsView.as_view(), name="contracts"),
    path('stats/', StatsView.as_view(), name="stats"),
    path('favorites/', UserFavoritesView.as_view(), name="user-favorites"),
    path('favorites/ae/', csrf_exempt(UserFavoriteListingUpdateView.as_view()), name='user-ae-favorites'),

    # path('plans/buy/', PlansView.as_view(), name="user-listing-plans"),

    path('listing/add/', AddListingView.as_view(), name="user-add-listing"),
    path('listing/<int:pk>/edit/', EditListingView.as_view(), name='user-edit-listing'),
    path('listing/unpublish/<int:pk>/', csrf_exempt(UnpublishListingView.as_view()), name='unpublish-listing'),
    path('listing/publish/<int:pk>/', csrf_exempt(PublishListingView.as_view()), name='publish-listing'),
    path('listing/delete/<int:pk>/', csrf_exempt(DeleteListingView.as_view()), name='delete-listing'),
    path('listing/success/', ListingSuccessView.as_view(), name='listing-success'),

    path('login/', LoginView.as_view(
        template_name='account/login.djhtml', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(template_name='account/login.djhtml'), name='logout'),

    # path('register/', RegisterView.as_view(), name='user-register'),
    # path('register/success/', RegisterSuccessView.as_view(), name='user-register-success'),
    # re_path(r'activate/(?P<token>.+)/', ActivateView.as_view(), name='user-activate'),

    path('upload/', csrf_exempt(DocumentUploadView.as_view()), name='docs-upload'),

    # Password reset/confirm
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='account/password_reset.djhtml',
        email_template_name='account/password_reset_email.djhtml',
        # post_reset_redirect='account:password_reset_sent',
        from_email=settings.DEFAULT_EMAIL
    ), name='password_reset'),

    path('password_reset/success/', auth_views.PasswordResetDoneView.as_view(
        template_name='account/password_reset_sent.djhtml'), name='password_reset_sent'),

    re_path(r'reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/', PasswordResetConfirmView.as_view(
        template_name='account/password_reset_new_form.djhtml',
        success_url='/account/reset/success/'
    ), name='password_reset_confirm'),

    path('reset/success/', auth_views.PasswordResetCompleteView.as_view(
        template_name='account/password_reset_success.djhtml'), name='password_reset_success'),

]
