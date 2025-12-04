import csv

from django.core.management import BaseCommand

from portal.models import Location


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input')

    def handle(self, *args, **options):
        self.stderr.write('Dropping all locations')
        Location.objects.all().delete()

        dubai = Location.objects.create(parent=None, name='Dubai', slug='dubai', is_city=True)
        abu_dhabi = Location.objects.create(parent=None, name='Abu Dhabi', slug='abu-dhabi', is_city=True)
        sharjah = Location.objects.create(parent=None, name='Sharjah', slug='sharjah', is_city=True)
        ajman = Location.objects.create(parent=None, name='Ajman', slug='ajman', is_city=True)
        umm_al_quwain = Location.objects.create(parent=None, name='Umm Al Quwain', slug='umm-al-quwain', is_city=True)
        ras_al_khaimah = Location.objects.create(parent=None, name='Ras Al Khaimah', slug='ras-al-khaimah', is_city=True)
        fujairah = Location.objects.create(parent=None, name='Fujairah', slug='fujairah', is_city=True)
        al_ain = Location.objects.create(parent=None, name='Al Ain', slug='al-ain', is_city=True)

        loop_again = True
        loops = 0
        pk_map = {}
        while loop_again and loops < 5:
            self.stderr.write('-' * 5)
            loop_again = False
            loops = loops + 1

            with open(options['input']) as f:
                ignored_parents = []

                r = csv.reader(f)
                for row in r:
                    pk, parent_pk, name, slug, is_city, is_location, is_sublocation, lat, lng = row
                    if parent_pk == '7097':
                        if name not in ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Umm Al Quwain',
                                        'Ras Al Khaimah', 'Fujairah', 'Al Ain']:
                            ignored_parents.append(pk)
                        continue
                    elif parent_pk in ignored_parents:
                        continue
                    elif parent_pk == '0':
                        continue

                    if parent_pk == '2':
                        parent_pk = abu_dhabi.pk
                    elif parent_pk == '7':
                        parent_pk = fujairah.pk
                    elif parent_pk == '3':
                        parent_pk = sharjah.pk
                    elif parent_pk == '8611':
                        parent_pk = al_ain.pk
                    elif parent_pk == '5':
                        parent_pk = umm_al_quwain.pk
                    elif parent_pk == '4':
                        parent_pk = ajman.pk
                    elif parent_pk == '1':
                        parent_pk = dubai.pk
                    elif parent_pk == '6':
                        parent_pk = ras_al_khaimah.pk
                    else:
                        try:
                            parent_pk = pk_map[parent_pk]
                        except KeyError:
                            self.stderr.write("No parent found for {}. Will loop again".format(name))
                            loop_again = True
                            continue

                    if Location.objects.filter(slug=slug).exists():
                        continue

                    if not lat:
                        lat = 0.0
                    if not lng:
                        lng = 0.0
                    location = Location.objects.create(parent_id=parent_pk, name=name, slug=slug, is_city=is_city,
                                                       is_location=is_location, is_sublocation=is_sublocation,
                                                       latitude=lat, longitude=lng)

                    pk_map[pk] = location.pk
