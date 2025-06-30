from dataclasses import dataclass
from typing import Optional, List, Set, Dict, Any
from enums import ChildType, Alliance
import re

@dataclass
class FlightPassengers:
    adults: int = 1
    students: int = 0
    children: List[ChildType] = None

    def __post_init__(self):
        self.children = self.children or []
        if self.adults < 0 or self.students < 0:
            raise ValueError("Adults and students cannot be negative")
        if self.adults == 0 and self.students == 0 and not self.children:
            raise ValueError("At least one passenger is required")

    def to_url_string(self) -> str:
        parts = []
        if self.adults > 0:
            parts.append(f"{self.adults}adults")
        if self.students > 0:
            parts.append(f"{self.students}students")
        if self.children:
            child_counts = {}
            for child in self.children:
                child_counts[child] = child_counts.get(child, 0) + 1
            child_str = "-".join(f"{count}{child.value}" if count > 1 else child.value
                                 for child, count in sorted(child_counts.items(), key=lambda x: x[0].value))
            parts.append(f"children-{child_str}")
        return "-".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adults": self.adults,
            "students": self.students,
            "children": [child.value for child in self.children]
        }

@dataclass
class FlightFilters:
    carry_on_free: Optional[int] = None
    checked_bags_free: Optional[int] = None
    stops: Optional[int] = None
    max_price: Optional[int] = None
    alliance: Optional[Alliance] = None
    include_airlines: Optional[Set[str]] = None
    exclude_airlines: Optional[Set[str]] = None
    wifi_only: bool = False

    def to_url_string(self) -> str:
        parts = []
        if self.carry_on_free is not None:
            if self.carry_on_free < 0:
                raise ValueError("Carry-on bags cannot be negative")
            parts.append(f"cfc={self.carry_on_free}")
        if self.checked_bags_free is not None:
            if self.checked_bags_free < 0:
                raise ValueError("Checked bags cannot be negative")
            parts.append(f"bfc={self.checked_bags_free}")
        if self.stops is not None:
            if self.stops < 0:
                raise ValueError("Stops cannot be negative")
            parts.append(f"stops={self.stops}")
        if self.max_price is not None:
            if self.max_price <= 0:
                raise ValueError("Max price must be positive")
            parts.append(f"price=-{self.max_price}")
        if self.alliance:
            parts.append(f"alliance={self.alliance.value}")
        if self.include_airlines:
            if not all(re.match(r"^[A-Z0-9]{2}$", code) for code in self.include_airlines):
                raise ValueError("Invalid airline codes in include_airlines")
            parts.append(f"airlines={','.join(self.include_airlines)}")
        if self.exclude_airlines:
            if not all(re.match(r"^[A-Z0-9]{2}$", code) for code in self.exclude_airlines):
                raise ValueError("Invalid airline codes in exclude_airlines")
            parts.append(f"airlines=-{','.join(self.exclude_airlines)}")
        if self.wifi_only:
            parts.append("wifi=wifi")
        return ";".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "carry_on_free": self.carry_on_free,
            "checked_bags_free": self.checked_bags_free,
            "stops": self.stops,
            "max_price": self.max_price,
            "alliance": self.alliance.value if self.alliance else None,
            "include_airlines": list(self.include_airlines) if self.include_airlines else None,
            "exclude_airlines": list(self.exclude_airlines) if self.exclude_airlines else None,
            "wifi_only": self.wifi_only
        }