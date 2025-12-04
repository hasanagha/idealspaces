SORT_ORDER_RECENT = 'r'
SORT_ORDER_PRICE_ASC = 'pa'
SORT_ORDER_PRICE_DESC = 'pd'

SORT_ORDER_OPTIONS = (
    (SORT_ORDER_RECENT, 'Most Recent'),
    (SORT_ORDER_PRICE_ASC, 'Price (High)'),
    (SORT_ORDER_PRICE_DESC, 'Price (Low)'),
)

AMENITIES = (
    (0, 'Balcony'),
    (1, 'Built in Kitchen Appliances'),
    (2, 'Built in Wardrobes'),
    (3, 'Central A/C & Heating'),
    (4, 'Concierge Service'),
    (5, 'Covered Parking'),
    (6, 'Maid Service'),
    (7, 'Maids Room'),
    (8, 'Pets Allowed'),
    (9, 'Private Garden'),
    (10, 'Private Gym'),
    (11, 'Private Jacuzzi'),
    (12, 'Private Pool'),
    (13, 'Security'),
    (14, 'Shared Gym'),
    (15, 'Shared Pool'),
    (16, 'Shared Spa'),
    (17, 'Study'),
    (18, 'View of Landmark'),
    (19, 'View of Water'),
    (20, 'Walk-in Closet'),
)

DEFAULT_ENQUIRY_MESSAGE = (
    'Hello,\n',
    'I found your property on {domain}. Please send me more information about this property.\n',
    'Thank you'
)

rent_price_ranges = ['', 0, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 140000, 160000, 180000, 200000, 220000, 250000, 300000, 350000, 400000, 500000, 600000, 700000]
sale_price_ranges = ['', 0, 200000, 250000, 300000, 350000, 400000, 450000, 500000, 600000, 700000, 800000, 900000, 1000000, 1250000, 1500000, 1750000, 2000000, 2250000, 2500000, 2750000, 3000000, 3250000, 3500000, 3750000, 4000000, 4500000, 5000000, 5500000, 6000000, 6500000, 7000000, 8000000, 9000000, 10000000, 12000000, 14000000, 16000000, 18000000, 20000000, 30000000, 40000000, 50000000, 100000000, 200000000, 300000000]

area_ranges = ['', 0, 500, 600, 700, 800, 900, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000, 12500, 13000, 13500, 14000, 14500, 15000, 15500, 16000, 16500, 17000, 17500, 18000, 18500, 19000, 19500, 20000]

RENT_PRICE_RANGES_LIST = [(val, "{:,}".format(int(val)) if val else val) for val in rent_price_ranges]
SALE_PRICE_RANGES_LIST = [(val, "{:,}".format(int(val)) if val else val) for val in sale_price_ranges]

AREA_RANGE_LIST = [(val, "{:,} sqft".format(int(val)) if val else val) for val in area_ranges]

BANNED_WORDS = ['cialis', 'viagra', 'buy']
