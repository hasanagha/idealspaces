import re
import phonenumbers

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from phonenumbers.phonenumberutil import NumberParseException


def is_valid_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, "AE")
    except NumberParseException:
        return False

    return phonenumbers.is_possible_number(parsed_number) and phonenumbers.is_valid_number(parsed_number)


def normalize_phone_number(phone_number):
    """Given a phone number as a string, `normalize_phone_number` converts it into a standard form that we use
    all across the project.

    This is needed so that when both inserting and searching for phone numbers we work with a standard representation of
    it. Right now that representation is the `phonenumbers.PhoneNumberFormat.E164`."""
    parsed_number = phonenumbers.parse(phone_number, "AE")
    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)


def add_empty_choice(choices, empty_label=''):
    return [(None, empty_label)] + list(choices)


def get_initials_from_the_name(name):
    initials = ''

    if name:
        name_parts = name.split(' ')[:2]
        if not name_parts:
            return ''

        if len(name_parts) == 1:
            initials = name[:2]
        else:
            for part in name_parts:
                if not part:
                    continue

                initials += part[0]

    return initials.upper()


def serialize_to_json(obj):
    return [{
        'value': item[0],
        'text': item[1]
    } for item in obj]


def clean_and_validate_email_addresses(email_addresses):
    delimiters = ',|;'
    final_email_addresses = list()

    for email in re.split(delimiters, email_addresses):
        email = email.strip()
        if not email:
            continue

        try:
            validate_email(email)
            final_email_addresses.append(email)
        except ValidationError:
            return False

    final_email_addresses = set(final_email_addresses)

    return '; '.join(final_email_addresses)


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)

    return cleantext
