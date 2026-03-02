"""
FraudMesh Utility Functions

This module provides utility functions for geographic calculations,
time window operations, and set operations used throughout the system.
"""

import math
from datetime import datetime, timedelta
from typing import Tuple, List, Set, TypeVar


T = TypeVar('T')


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Uses the Haversine formula to compute the distance between two geographic
    coordinates specified as (latitude, longitude) pairs.
    
    Args:
        coord1: First coordinate as (latitude, longitude) in degrees
        coord2: Second coordinate as (latitude, longitude) in degrees
    
    Returns:
        Distance in kilometers
    
    Example:
        >>> haversine_distance((40.7128, -74.0060), (34.0522, -118.2437))
        3935.75  # New York to Los Angeles
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def is_within_window(timestamp: datetime, minutes: int, reference: datetime = None) -> bool:
    """
    Check if a timestamp falls within a time window.
    
    Args:
        timestamp: The timestamp to check
        minutes: Time window size in minutes
        reference: Reference timestamp (defaults to current time)
    
    Returns:
        True if timestamp is within the window, False otherwise
    
    Example:
        >>> now = datetime.now()
        >>> past = now - timedelta(minutes=5)
        >>> is_within_window(past, minutes=10)
        True
        >>> is_within_window(past, minutes=3)
        False
    """
    if reference is None:
        reference = datetime.now()
    
    time_diff = abs((reference - timestamp).total_seconds() / 60)
    return time_diff <= minutes


def merge_overlapping_sets(sets: List[Set[T]]) -> List[Set[T]]:
    """
    Merge overlapping sets into disjoint sets.
    
    Given a list of sets that may have overlapping elements, merge all sets
    that share at least one element into single sets.
    
    Args:
        sets: List of sets to merge
    
    Returns:
        List of disjoint (non-overlapping) sets
    
    Example:
        >>> sets = [{1, 2}, {2, 3}, {4, 5}, {5, 6}]
        >>> merge_overlapping_sets(sets)
        [{1, 2, 3}, {4, 5, 6}]
    """
    if not sets:
        return []
    
    # Convert to list of sets for easier manipulation
    merged = []
    
    for current_set in sets:
        # Find all sets that overlap with current_set
        overlapping = []
        non_overlapping = []
        
        for existing_set in merged:
            if current_set & existing_set:  # If sets have common elements
                overlapping.append(existing_set)
            else:
                non_overlapping.append(existing_set)
        
        # Merge current_set with all overlapping sets
        new_set = current_set.copy()
        for overlap in overlapping:
            new_set |= overlap
        
        # Add merged set back to list
        merged = non_overlapping + [new_set]
    
    return merged


def get_time_of_day_category(hour: int) -> str:
    """
    Categorize hour of day into time periods.
    
    Args:
        hour: Hour of day (0-23)
    
    Returns:
        Time category: "late_night", "early_morning", "business_hours", "evening"
    
    Example:
        >>> get_time_of_day_category(3)
        'late_night'
        >>> get_time_of_day_category(14)
        'business_hours'
    """
    if 0 <= hour < 6:
        return "late_night"
    elif 6 <= hour < 9:
        return "early_morning"
    elif 9 <= hour < 17:
        return "business_hours"
    else:
        return "evening"


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Numeric amount
        currency: Currency code (default: USD)
    
    Returns:
        Formatted currency string
    
    Example:
        >>> format_currency(1234.56)
        '$1,234.56'
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def calculate_velocity(timestamps: List[datetime], window_minutes: int = 60) -> float:
    """
    Calculate transaction velocity (transactions per hour).
    
    Args:
        timestamps: List of transaction timestamps
        window_minutes: Time window to consider (default: 60 minutes)
    
    Returns:
        Transactions per hour
    
    Example:
        >>> now = datetime.now()
        >>> timestamps = [now - timedelta(minutes=i*10) for i in range(5)]
        >>> calculate_velocity(timestamps, window_minutes=60)
        5.0
    """
    if not timestamps:
        return 0.0
    
    reference = max(timestamps)
    recent_timestamps = [
        ts for ts in timestamps
        if is_within_window(ts, window_minutes, reference)
    ]
    
    # Convert to transactions per hour
    velocity = len(recent_timestamps) * (60 / window_minutes)
    return velocity


def get_segment_id(dimension: str, value: any) -> str:
    """
    Generate segment ID for fairness monitoring.
    
    Args:
        dimension: Segmentation dimension (region, amount, age)
        value: Value to segment by
    
    Returns:
        Segment identifier string
    
    Example:
        >>> get_segment_id("region", "US")
        'region_US'
        >>> get_segment_id("amount", 1500.0)
        'amount_high'
    """
    if dimension == "region":
        return f"region_{value}"
    elif dimension == "amount":
        if value < 100:
            return "amount_low"
        elif value < 500:
            return "amount_medium"
        elif value < 1000:
            return "amount_high"
        else:
            return "amount_very_high"
    elif dimension == "age":
        if value < 7:
            return "age_new"
        elif value < 30:
            return "age_recent"
        elif value < 90:
            return "age_established"
        else:
            return "age_mature"
    else:
        return f"{dimension}_{value}"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        Clamped value
    
    Example:
        >>> clamp(0.95, 0.2, 0.8)
        0.8
        >>> clamp(0.15, 0.2, 0.8)
        0.2
    """
    return max(min_value, min(max_value, value))


def extract_region_from_location(location: Tuple[float, float]) -> str:
    """
    Extract geographic region from coordinates (simplified).
    
    Args:
        location: Coordinates as (latitude, longitude)
    
    Returns:
        Region identifier
    
    Example:
        >>> extract_region_from_location((40.7128, -74.0060))
        'North America'
    """
    lat, lon = location
    
    # Simplified region mapping based on coordinates
    if 25 <= lat <= 50 and -125 <= lon <= -65:
        return "North America"
    elif 35 <= lat <= 70 and -10 <= lon <= 40:
        return "Europe"
    elif -10 <= lat <= 35 and 60 <= lon <= 150:
        return "Asia Pacific"
    elif -55 <= lat <= 15 and -80 <= lon <= -35:
        return "Latin America"
    elif 10 <= lat <= 40 and 25 <= lon <= 60:
        return "Middle East"
    else:
        return "Other"
