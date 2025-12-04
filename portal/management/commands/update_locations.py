from django.core.management import BaseCommand

from portal.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stderr.write('Getting all parent locations Except Dubai')
        parents = Location.objects.filter(parent_id=None).exclude(slug='dubai')

        for loc in parents:
            self.stderr.write('*** Fetching all locations for {} ***'.format(loc.name))
            self.stderr.write('Disabling city ' + loc.name)
            loc.status = False
            loc.save()

            locations = Location.objects.filter(parent=loc, is_location=True)
            location_ids = locations.values_list('id')
            self.stderr.write('Disabling locations for ' + loc.name)
            locations.update(status=False)

            sublocations = Location.objects.filter(parent_id__in=location_ids, is_sublocation=True)
            self.stderr.write('Disabling sublocations for ' + loc.name)
            sublocations.update(status=False)
