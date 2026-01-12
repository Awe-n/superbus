#!/usr/bin/env python3
"""
Bus Stop Finder - Universal Stop ID Finder for Île-de-France
Find STIF Stop IDs for any bus/transit line using IDFM open data

Usage: python3 stop_id.py
"""

import requests
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

# Your PRIM API key (for testing stops)
API_KEY = "CK5M767DwRvWjb5MP1KsNSdPrS6RbbnP"

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def search_stops_by_name(search_term):
    """
    Search for stops by name across all lines using IDFM open data
    This is the most reliable method - no API key required!
    """
    
    if not search_term:
        print("❌ Search term cannot be empty")
        return
    
    print(f"\n⏳ Searching IDFM database for '{search_term}'...")
    print("   (Downloading ~30MB of stop data, may take 10-20 seconds)")
    print()
    
    try:
        # Download the complete stops-lines dataset from IDFM
        endpoint = 'https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/arrets-lignes/exports/json'
        response = requests.get(endpoint, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Error accessing IDFM database: {response.status_code}")
            return
        
        data = json.loads(response.text)
        print(f"✓ Downloaded {len(data)} stop-line combinations")
        print()
        
        # Search for matching stops
        search_lower = search_term.lower()
        matching_stops = {}
        
        for entry in data:
            stop_name = entry.get('stop_name', '')
            stop_id = entry.get('stop_id', '')
            line_name = entry.get('route_long_name', '')
            
            if search_lower in stop_name.lower():
                # Group by stop_id to avoid duplicates
                if stop_id not in matching_stops:
                    matching_stops[stop_id] = {
                        'name': stop_name,
                        'idfm_id': stop_id,
                        'stif_id': convert_idfm_to_stif(stop_id),
                        'lines': [],
                        'location': entry.get('nom_commune', 'Unknown'),
                        'operator': entry.get('operatorname', 'Unknown'),
                        'coords': (entry.get('stop_lat', 'N/A'), entry.get('stop_lon', 'N/A'))
                    }
                matching_stops[stop_id]['lines'].append(line_name)
        
        if not matching_stops:
            print(f"⚠️  No stops found matching '{search_term}'")
            print("\n💡 TIP: Try a simpler search term (e.g., just 'carrel' instead of full name)")
            return
        
        # Display results
        print("=" * 80)
        print(f"📍 FOUND {len(matching_stops)} MATCHING STOP(S):")
        print("=" * 80)
        print()
        
        for idx, (stop_id, info) in enumerate(sorted(matching_stops.items(), key=lambda x: x[1]['name']), 1):
            print(f"{idx}. {info['name']}")
            print(f"   Location: {info['location']}")
            print(f"   Operator: {info['operator']}")
            print(f"   Lines: {', '.join(sorted(set(info['lines'][:10])))}")
            if len(info['lines']) > 10:
                print(f"          ... and {len(info['lines']) - 10} more")
            print(f"   Coordinates: {info['coords']}")
            print()
            print(f"   📋 IDFM ID: {info['idfm_id']}")
            print(f"   📋 STIF ID: {info['stif_id']}")
            print()
        
        return matching_stops
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def convert_idfm_to_stif(idfm_id):
    """
    Convert IDFM ID format to STIF format required by the API
    IDFM:12345 -> STIF:StopPoint:Q:12345:
    """
    if ':' in idfm_id:
        number = idfm_id.split(':')[1]
    else:
        number = idfm_id
    
    return f"STIF:StopPoint:Q:{number}:"

if __name__ == "__main__":
    search_stops_by_name("carrel")
