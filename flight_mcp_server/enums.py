from enum import Enum

class PlaneType(Enum):
    ECONOMY = "economy"
    PREMIUM = "premium"
    BUSINESS = "business"
    FIRST = "first"

class SortOption(Enum):
    BEST_FLIGHT = "bestflight_a"
    QUICKEST = "duration_a"
    SLOWEST = "duration_b"
    CHEAPEST = "price_a"
    MOST_EXPENSIVE = "price_b"
    EARLIEST_TAKEOFF_A = "depart_a"
    LATEST_TAKEOFF_A = "depart_b"
    EARLIEST_LANDING_B = "arrive_a"
    LATEST_LANDING_B = "arrive_b"
    EARLIEST_TAKEOFF_B = "departReturn_a"
    LATEST_TAKEOFF_B = "departReturn_b"
    EARLIEST_LANDING_A = "arriveReturn_a"
    LATEST_LANDING_A = "arriveReturn_b"

class Alliance(Enum):
    VALUE_ALLIANCE = "VALUE_ALLIANCE"
    ONE_WORLD = "ONE_WORLD"
    SKY_TEAM = "SKY_TEAM"
    STAR_ALLIANCE = "STAR_ALLIANCE"

class ChildType(Enum):
    CHILD = "11"  # Children aged 2-11
    TODDLER_SEAT = "1S"  # Toddlers under 2 in own seat
    INFANT_LAP = "1L"  # Infants under 2 on lap