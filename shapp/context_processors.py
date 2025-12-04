from django.conf import settings


def settings_processor(request):
    """Adds the settings as a variable to all templates"""
    canonical = f'https://www.idealspaces.com{request.path_info}'

    cs = {
        'facebook_link': settings.FACEBOOK_URL,
        'twitter_link': settings.TWITTER_URL,
        'linkedin_link': settings.LINKEDIN_URL,
        'instagram_link': settings.INSTAGRAM_URL,
        'googleplus_link': settings.GOOGLEPLUS_URL,
        'debug': settings.DEBUG,
        'currency': 'AED',
        'current_page_canonical': canonical
    }

    return cs
