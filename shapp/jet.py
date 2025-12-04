# encoding: utf-8
import datetime

from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard

from portal.models import Listing
from portal.models import ListingEnquiry
from portal.models import ContactUsEnquiry
from portal.models import ListingStats


class ListingDetails(modules.DashboardModule):
    template = 'admin/modules/properties.djhtml'
    title = 'Quick Actions'

    def get_context_data(self):
        ctx = super().get_context_data()

        listings = Listing.objects.all()
        enquiries = ListingEnquiry.objects.all()
        contact = ContactUsEnquiry.objects.all()

        user = ctx['user']

        if user.is_superuser:

            ctx['published_listings'] = listings.filter(status=Listing.STATUS_PUBLISHED).count()
            ctx['inreview_listings'] = 0

            ctx['new_enquiries'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_NEW).count()
            ctx['working_enquiries'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_WORKING).count()

            ctx['new_enquiries_bav'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_NEW).count()
            ctx['working_enquiries_bav'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_WORKING).count()

            ctx['new_contact'] = contact.filter(status=ContactUsEnquiry.CONTACT_STATUS_NEW).count()
            ctx['working_contact'] = contact.filter(
                status=ContactUsEnquiry.CONTACT_STATUS_WORKING).count()
        else:
            ctx['published_listings'] = listings.filter(status=Listing.STATUS_PUBLISHED, manager=user).count()
            ctx['inreview_listings'] = 0

            ctx['new_enquiries'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_NEW, listing__manager=user).count()
            ctx['working_enquiries'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_WORKING, listing__manager=user).count()

            ctx['new_enquiries_bav'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_NEW, listing__manager=user).count()
            ctx['working_enquiries_bav'] = enquiries.filter(
                status=ListingEnquiry.ENQUIRY_STATUS_WORKING, listing__manager=user).count()

            ctx['new_contact'] = contact.filter(status=ContactUsEnquiry.CONTACT_STATUS_NEW).count()
            ctx['working_contact'] = contact.filter(
                status=ContactUsEnquiry.CONTACT_STATUS_WORKING).count()

        return ctx


class Reports(modules.DashboardModule):
    template = 'admin/modules/reports.djhtml'
    title = 'Reports'

    def get_context_data(self):
        ctx = super().get_context_data()
        params = self.context['request'].GET

        filters = {}
        message_top = ''

        if len(params):
            start_date = params.get('start_date', None)
            end_date = params.get('end_date', None)
            if start_date or end_date:
                message_top = 'Dates: '

            if start_date:
                filters['date__gte'] = start_date
                message_top = '{} from {}'.format(message_top, start_date)
            if end_date:
                filters['date__lte'] = end_date
                message_top = '{} till {}'.format(message_top, end_date)

        ctx['stats'] = ListingStats.objects.filter(**filters).order_by('-date')
        ctx['messageTop'] = message_top

        return ctx

    def get_aggregated_data(self, recordset):
        counts = {}
        for item in recordset:
            date = item['date']
            date_formatted = "{}-{}-{}".format(
                date.year,
                date.month,
                date.day
            )
            counts[date_formatted] = item['counts']

        return counts

    def prepare_data(self, quotes, leads):
        result = []
        for i in range(7):
            date = datetime.datetime.now() - datetime.timedelta(days=i)
            date_formatted = "{}-{}-{}".format(
                date.year,
                date.month,
                date.day
            )

            result.append({
                'date': date_formatted,
                'leads': leads.get(date_formatted, 0),
                'quotes': quotes.get(date_formatted, 0)
            })

        return result


class CustomIndexDashboard(Dashboard):
    columns = 1

    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)
        self.available_children.append(ListingDetails)
        self.available_children.append(Reports)
