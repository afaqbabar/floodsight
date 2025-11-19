#!/usr/bin/env python3
"""Test EWDS GloFAS dataset parameters"""

import cdsapi
import json

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("Testing EWDS GloFAS Dataset Access")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

client = cdsapi.Client(
    url="https://ewds.climate.copernicus.eu/api",
    key="ff5874bb-e24c-495f-878c-e206f74e0c36"
)

# Test 1: Minimal request
print("Test 1: Minimal request (just required parameters)\n")

try:
    print("Requesting cems-glofas-forecast with minimal params...")
    result = client.retrieve(
        'cems-glofas-forecast',
        {
            'product_type': 'control_forecast',
            'variable': 'river_discharge_in_the_last_24_hours',
            'year': '2025',
            'month': '11',
            'day': '12',  # Yesterday
            'leadtime_hour': '24',
            'format': 'netcdf',
        },
        'test_minimal.nc'
    )
    print("✅ SUCCESS with minimal params!")
    print(f"Result: {result}\n")
except Exception as e:
    print(f"❌ Error with minimal params:")
    print(f"{str(e)}\n")

# Test 2: Without system_version
print("\nTest 2: Without system_version and hydrological_model\n")

try:
    result = client.retrieve(
        'cems-glofas-forecast',
        {
            'product_type': 'control_forecast',
            'variable': 'river_discharge_in_the_last_24_hours',
            'year': '2025',
            'month': '11',
            'day': '12',
            'leadtime_hour': ['24', '48'],
            'area': [54, 5, 46, 18],  # North, West, South, East
            'format': 'netcdf',
        },
        'test_no_version.nc'
    )
    print("✅ SUCCESS without version params!")
    print(f"Result: {result}\n")
except Exception as e:
    print(f"❌ Error without version params:")
    print(f"{str(e)}\n")

# Test 3: Different variable name
print("\nTest 3: Try simpler variable name\n")

try:
    result = client.retrieve(
        'cems-glofas-forecast',
        {
            'product_type': 'control_forecast',
            'variable': 'river_discharge',  # Simpler name
            'year': '2025',
            'month': '11',
            'day': '12',
            'leadtime_hour': '24',
            'format': 'netcdf',
        },
        'test_simple_var.nc'
    )
    print("✅ SUCCESS with simple variable name!")
    print(f"Result: {result}\n")
except Exception as e:
    print(f"❌ Error with simple variable:")
    print(f"{str(e)}\n")

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("Summary:")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("If all tests fail with same error:")
print("  → You likely need to accept Terms of Use on the EWDS portal")
print()
print("If some tests work:")
print("  → Update backend code with working parameters")
print()
print("To accept Terms of Use:")
print("  1. Visit: https://ewds.climate.copernicus.eu/")
print("  2. Search for: cems-glofas-forecast")
print("  3. Scroll to bottom and accept Terms")
print("  4. Run this script again")
print()

