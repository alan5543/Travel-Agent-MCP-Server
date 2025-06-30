from enum import Enum

# Enum definitions for parameters with predefined values
class SortBy(Enum):
    """Enum for sorting options in Google Hotels API."""
    LOWEST_PRICE = "3"
    HIGHEST_RATING = "8"
    MOST_REVIEWED = "13"

class Rating(Enum):
    """Enum for minimum rating filter in Google Hotels API."""
    THREE_POINT_FIVE_PLUS = "7"
    FOUR_PLUS = "8"
    FOUR_POINT_FIVE_PLUS = "9"

class HotelClass(Enum):
    """Enum for hotel class filter in Google Hotels API."""
    TWO_STAR = "2"
    THREE_STAR = "3"
    FOUR_STAR = "4"
    FIVE_STAR = "5"

class PropertyType(Enum):
    """Enum for property types in Google Hotels API."""
    BEACH_HOTELS = "12"
    BOUTIQUE_HOTELS = "13"
    HOSTELS = "14"
    INNS = "15"
    MOTELS = "16"
    RESORTS = "17"
    SPA_HOTELS = "18"
    BED_AND_BREAKFASTS = "19"
    OTHER = "20"
    APARTMENT_HOTELS = "21"
    MINSHUKU = "22"
    JAPANESE_STYLE_BUSINESS_HOTELS = "23"
    RYOKAN = "24"

class Amenity(Enum):
    """Enum for amenities in Google Hotels API."""
    FREE_PARKING = "1"
    PARKING = "3"
    INDOOR_POOL = "4"
    OUTDOOR_POOL = "5"
    POOL = "6"
    FITNESS_CENTER = "7"
    RESTAURANT = "8"
    FREE_BREAKFAST = "9"
    SPA = "10"
    BEACH_ACCESS = "11"
    CHILD_FRIENDLY = "12"
    BAR = "15"
    PET_FRIENDLY = "19"
    ROOM_SERVICE = "22"
    FREE_WIFI = "35"
    AIR_CONDITIONED = "40"
    ALL_INCLUSIVE_AVAILABLE = "52"
    WHEELCHAIR_ACCESSIBLE = "53"
    EV_CHARGER = "61"