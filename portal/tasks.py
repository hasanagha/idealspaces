import short_url

from shapp.email import EmailService
from django.conf import settings

from django.urls import reverse


def send_listing_email_on_successful_submission(form_data, listing):
    email = EmailService()

    listing_url = "{}{}".format(settings.BASE_URL, listing.get_listing_url())

    data = {
        'listing_title': listing.title,
        'listing_url': listing_url,
        'listing_image': listing.get_default_image(),
        'listing_location': listing.location.name,
        'listing_reference': listing.get_reference_code(),

        'user_name': form_data['name'],
        'user_email': form_data['email'],
        'user_phone': form_data['phone'],
        'user_message': form_data['message'],
    }

    email.send_listing_enquiry_email(form_data['email'], form_data['name'], data)

    company_name = listing.company.name
    company_email = settings.ADMIN_EMAIL

    if listing.company.send_email and listing.company.inquiry_email:
        company_email = listing.company.inquiry_email
        if company_email != settings.ADMIN_EMAIL:
            data['bcc_email'] = settings.ADMIN_EMAIL

    email.send_listing_enquiry_email_agent(company_email, company_name, data)


def send_activation_email_on_successful_signup(user):
    email = EmailService()

    encoded_id = short_url.encode_url(user.pk)
    activation_url = reverse('account:user-activate', kwargs={'token': encoded_id})

    data = {
        'activation_url': "{}{}".format(settings.BASE_URL, activation_url),
        'user_name': user.get_full_name()
    }

    email.send_account_activation_email(user.email, user.get_full_name(), data)
