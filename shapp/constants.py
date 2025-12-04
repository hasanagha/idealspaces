CATEGORY_SERVICED_OFFICES = 'serviced-offices'
CATEGORY_BANQUET_HALLS = 'banquet-halls'
CATEGORY_COWORKING_SPACES = 'coworking-spaces'
CATEGORY_MEETING_ROOMS = 'meeting-rooms'

LISTING_CATEGORIES = (
    (CATEGORY_SERVICED_OFFICES, 'Serviced Offices'),
    # (CATEGORY_BANQUET_HALLS, 'Banquet Halls'),
    # (CATEGORY_COWORKING_SPACES, 'Co-working Spaces'),
    (CATEGORY_MEETING_ROOMS, 'Meeting Rooms'),
)

VENUE_EVENTS = 'events'
VENUE_TRAINING = 'training-center'
VENUE_HOTEL3STAR = 'hotel-3-star'
VENUE_HOTEL4STAR = 'hotel-4-star'
VENUE_HOTEL5STAR = 'hotel-5-star'
VENUE_BUSINESS_CENTER = 'business-center'

LISTING_VENUES = (
    # (VENUE_EVENTS, 'Events'),
    # (VENUE_TRAINING, 'Training Center'),
    # (VENUE_HOTEL3STAR, '3 Star'),
    # (VENUE_HOTEL4STAR, '4 Star'),
    # (VENUE_HOTEL5STAR, '5 Star'),
    (VENUE_BUSINESS_CENTER, 'Business Center'),
)

LAYOUT_USHAPED = 'ushaped'
LAYOUT_VSHAPED = 'vshaped'
LAYOUT_THEATER = 'theater-auditorium'
LAYOUT_CLASSROOM = 'classroom'
LAYOUT_BOARDROOM = 'boardroom'
LAYOUT_BANQUET = 'banquet'
LAYOUT_COCKTAIL = 'cocktail'
LAYOUT_CABARET = 'cabaret'

LISTING_LAYOUTS = (
    (LAYOUT_BANQUET, 'Banquet'),
    (LAYOUT_BOARDROOM, 'Boardroom'),
    (LAYOUT_CABARET, 'Cabaret'),
    (LAYOUT_CLASSROOM, 'Classroom'),
    (LAYOUT_COCKTAIL, 'Cocktail'),
    (LAYOUT_THEATER, 'Theater/Auditorium'),
    (LAYOUT_USHAPED, 'U Shaped'),
    (LAYOUT_VSHAPED, 'V Shaped'),
)

LISTING_AMENITIES = (
    (0, 'Connectors'),
    (1, 'Flipchart'),
    (2, 'Metro'),
    (3, 'Mic/Audio Equipment'),
    (4, 'Printers'),
    (5, 'Projector Screen'),
    (6, 'Stationary'),
    (7, 'Tea/Coffee'),
    (8, 'Video Conferencing'),
    (9, 'Whiteboard'),
    (10, 'Wifi'),
    (11, 'Parking'),

# Receptionist Service
# Printer & Scanner
# Fax
# Mailing Address
# Registered Address
# Meeting Room
# Conference Room
# Voicemail
# Phone Answering Service
# Executive Suite
# Dedicated Desk
# Private Offices
# Organic Coffee
# Purified Water
# Parking
# Lounge
# Open Desk
# Library
# Dinning Space
# Online Booking
# High Speed Internet
# Gaming Room
# Mini Gym
# Pet Friendly
# Video-conferencing Facilities
# Maintained Restrooms
# Office supply items
# Courier Service
# Connectors
# Flipchart
# Metro
# Mic/Audio Equipment
# Wifi
# Whiteboard

)

LISTING_FREQUENCIES_PREFIX = (
    ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
    ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')
)

LISTING_NUMBER_OF_PEOPLE = (
    ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
    ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
    ('10+', '10+'), ('20+', '20+'), ('30+', '30+'), ('50+', '50+'), ('100+', '100+'), ('500+', '500+')
)

LISTING_FREQUENCIES = (
    ('hourly', 'Hourly'),
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
)
