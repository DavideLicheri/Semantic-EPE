"""
Test configuration for EURING Code Recognition System
"""
import pytest
from hypothesis import settings, Verbosity
from hypothesis.strategies import composite, text, integers, lists, sampled_from
from typing import List
import string

# Configure Hypothesis settings
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.load_profile("default")

# EURING version years for testing
EURING_YEARS = list(range(1963, 2024))

# Common EURING field patterns
EURING_FIELD_PATTERNS = {
    "species_code": string.digits,
    "ring_number": string.ascii_uppercase + string.digits,
    "date": string.digits,
    "location": string.ascii_uppercase + string.digits,
    "age": string.digits,
    "sex": "MFU",  # Male, Female, Unknown
    "condition": string.digits
}

@composite
def euring_string_strategy(draw, version_year=None):
    """Generate valid EURING strings for testing"""
    if version_year is None:
        version_year = draw(sampled_from(EURING_YEARS))
    
    # Generate fields based on version year
    if version_year < 1980:
        # Early format - shorter strings
        species = draw(text(alphabet=string.digits, min_size=4, max_size=4))
        ring_num = draw(text(alphabet=string.ascii_uppercase + string.digits, min_size=6, max_size=8))
        date = draw(text(alphabet=string.digits, min_size=6, max_size=6))
        return f"{species}{ring_num}{date}"
    elif version_year < 2000:
        # Middle format - extended fields
        species = draw(text(alphabet=string.digits, min_size=5, max_size=5))
        ring_num = draw(text(alphabet=string.ascii_uppercase + string.digits, min_size=8, max_size=10))
        date = draw(text(alphabet=string.digits, min_size=8, max_size=8))
        location = draw(text(alphabet=string.ascii_uppercase + string.digits, min_size=4, max_size=6))
        return f"{species}{ring_num}{date}{location}"
    else:
        # Modern format - full fields
        species = draw(text(alphabet=string.digits, min_size=5, max_size=5))
        ring_num = draw(text(alphabet=string.ascii_uppercase + string.digits, min_size=8, max_size=12))
        date = draw(text(alphabet=string.digits, min_size=8, max_size=8))
        location = draw(text(alphabet=string.ascii_uppercase + string.digits, min_size=6, max_size=8))
        age = draw(sampled_from(["1", "2", "3", "4", "5", "6", "7", "8", "9"]))
        sex = draw(sampled_from(["M", "F", "U"]))
        condition = draw(text(alphabet=string.digits, min_size=2, max_size=2))
        return f"{species}{ring_num}{date}{location}{age}{sex}{condition}"

@composite
def euring_batch_strategy(draw, min_size=1, max_size=10, same_version=None):
    """Generate batches of EURING strings for testing"""
    batch_size = draw(integers(min_value=min_size, max_value=max_size))
    
    if same_version:
        # All strings from same version
        version_year = draw(sampled_from(EURING_YEARS))
        return [draw(euring_string_strategy(version_year=version_year)) for _ in range(batch_size)]
    else:
        # Mixed versions
        return [draw(euring_string_strategy()) for _ in range(batch_size)]

@composite
def user_credentials_strategy(draw, valid=True):
    """Generate user credentials for testing"""
    if valid:
        username = draw(text(alphabet=string.ascii_letters + string.digits, min_size=3, max_size=20))
        password = draw(text(alphabet=string.ascii_letters + string.digits + "!@#$%", min_size=8, max_size=50))
    else:
        # Generate invalid credentials
        username = draw(text(alphabet=string.ascii_letters + string.digits, min_size=0, max_size=2))
        password = draw(text(alphabet=string.ascii_letters, min_size=0, max_size=3))
    
    return {"username": username, "password": password}

@pytest.fixture
def sample_euring_versions():
    """Fixture providing sample EURING versions for testing"""
    return [
        {
            "id": "euring_1966",
            "name": "EURING 1966",
            "year": 1966,
            "description": "Original EURING format from 1963"
        },
        {
            "id": "euring_1985", 
            "name": "EURING 1985",
            "year": 1985,
            "description": "Extended EURING format from 1985"
        },
        {
            "id": "euring_2010",
            "name": "EURING 2010", 
            "year": 2010,
            "description": "Modern EURING format from 2010"
        }
    ]

@pytest.fixture
def sample_conversion_mappings():
    """Fixture providing sample conversion mappings for testing"""
    return [
        {
            "from_version": "euring_1966",
            "to_version": "euring_1985",
            "compatibility_level": "partial"
        },
        {
            "from_version": "euring_1985", 
            "to_version": "euring_2010",
            "compatibility_level": "full"
        }
    ]