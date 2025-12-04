import io
import logging
import random
import string

import requests
import sendwithus

from django.conf import settings

SENDER_NAME = "IdealSpaces"
SENDER_EMAIL = "noreply@idealspaces.com"
SENDER_REPLYTO = "tech@idealspaces.com"

api_logger = logging.getLogger("api.sendwithus")


class EmailService:
    def send_email(self, request_body):
        api = sendwithus.api(api_key=settings.SENDWITHUS_API_KEY)
        response = api.send(**request_body)

        if response.status_code != requests.codes.ok:
            api_logger.error(
                "Got non-OK response code while sending an email. \nResponse code: {}\nContent: {}"
                .format(response.status_code, response.content)
            )
            raise Exception("Error occurred while sending an Email")

        return response

    def send_email_to_single_recipient(self, data, user_email, user_name='', template_id=''):
        """Send email to a single recipient. A helper method that delegates to the main send_email method"""
        recipient = {
            'address': user_email,
            'name': user_name,
        }

        request_body = self.prepare_request(data, recipient, template_id)

        self.send_email(request_body)

    def send_account_activation_email(self, user_email, user_name, data):
        self.send_email_to_single_recipient(
            data=data,
            user_email=user_email,
            user_name=user_name,
            template_id=settings.SENDWITHUS_TEMPLATES['ACTIVATION_LINK']
        )

    def send_listing_enquiry_email(self, user_email, user_name, data):
        self.send_email_to_single_recipient(
            data=data,
            user_email=user_email,
            user_name=user_name,
            template_id=settings.SENDWITHUS_TEMPLATES['LISTING_ENQUIRY']
        )

    def send_listing_enquiry_email_agent(self, user_email, user_name, data):
        self.send_email_to_single_recipient(
            data=data,
            user_email=user_email,
            user_name=user_name,
            template_id=settings.SENDWITHUS_TEMPLATES['LISTING_ENQUIRY_AGENT']
        )

    def send_contact_emails(self, user_email, user_name, data):
        self.send_email_to_single_recipient(
            data=data,
            user_email=user_email,
            user_name=user_name,
            template_id=settings.SENDWITHUS_TEMPLATES['CONTACT_US']
        )

        # Sending to Admins
        data['subject'] = 'IdealSpaces.com: User submitted {}'.format(data['type'])
        data['cc_email'] = settings.ADMIN_EMAIL2

        self.send_email_to_single_recipient(
            data=data,
            user_email=settings.ADMIN_EMAIL,
            user_name='IS Admins',
            template_id=settings.SENDWITHUS_TEMPLATES['CONTACT_US']
        )

    def send_email_with_attachment(self, template_id, user_email, user_name, files, data):
        recipient = {
            "name": user_name,
            "address": user_email
        }

        request_body = self.prepare_request(
            data=data,
            recipient=recipient,
            template_id=template_id,
            files=files
        )

        response = self.send_email(request_body)

        if response.status_code != requests.codes.ok:
            api_logger.error(
                "Got non-OK response code while sending an email with attachment. \nResponse code: {}\nContent: {}"
                .format(response.status_code, response.content)
            )
            raise Exception("Error occurred while sending an Email with attachment")

        return response

    def prepare_request(self, data, recipient, template_id='', files=None):
        if not template_id:
            template_id = settings.SENDWITHUS_TEMPLATES['BASIC']

        request_body = {
            "email_id": template_id,
            "recipient": recipient,
            "email_data": data,
            "sender": {
                "name": data.get('override_sender_name', SENDER_NAME),
                "address": data.get('override_sender_email', SENDER_EMAIL),
                "reply_to": data.get('override_sender_replyto', SENDER_REPLYTO)
            }
        }

        if files:
            request_body['files'] = self.cleaned_files(files)

        if 'cc_email' in data:
            request_body['cc'] = [{
                'address': data['cc_email'].strip()
            }]

        if 'bcc_email' in data:
            request_body['bcc'] = [{
                'address': address.strip()
            } for address in data['bcc_email'].split(',')]

        if 'headers' in data:
            request_body['headers'] = data['headers']

        return request_body

    def cleaned_files(self, files):
        cleaned_files = list()

        for current_file in files:
            filename = current_file.get('filename', self.get_random_filename())
            file_encoded_data = io.BytesIO(current_file['file'])
            if file_encoded_data:
                cleaned_files.append({'file': file_encoded_data, 'filename': filename})

        return cleaned_files

    def get_random_filename(self):
        size = 6
        chars = string.ascii_uppercase + string.digits

        return ''.join(random.choice(chars) for x in range(size))
