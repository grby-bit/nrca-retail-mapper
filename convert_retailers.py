#!/usr/bin/env python3
"""
NRCA Retailer Database Converter
Converts Excel files containing 600k+ retailer POI data
to JavaScript format for the NRCA Retail Mapper web application
"""

import os
import json
import pandas as pd
import subprocess
from pathlib import Path

# Configuration
REPO_PATH = r"C:\Users\GeorgeKirby\nrca-retail-mapper"
DATA_OUTPUT_PATH = os.path.join(REPO_PATH, "data")
OUTPUT_FILE = os.path.join(DATA_OUTPUT_PATH, "retailers.js")

# Ensure data directory exists
os.makedirs(DATA_OUTPUT_PATH, exist_ok=True)

def parse_excel_file(filepath):
    """Parse Excel file and extract ALL retailer POI data"""
    try:
        print(f"  Reading Excel file: {os.path.basename(filepath)}")
        
        all_retailers = []
        xls = pd.ExcelFile(filepath)
        
        # Read all sheets
        for sheet_name in xls.sheet_names:
            try:
                print(f"    Processing sheet: {sheet_name}")
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                
                # Process EVERY row - don't filter out any data
                for idx, row in df.iterrows():
                    retailer = {
                        'id': str(row.get('poi_id') or row.get('ID') or idx),
                        'name': str(row.get('name') or row.get('Name') or 'Unknown'),
                        'locality': str(row.get('locality') or row.get('Locality') or ''),
                        'postcode': str(row.get('postcode') or row.get('Postcode') or ''),
                        'address': str(row.get('address') or row.get('Address') or ''),
                        'latitude': float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,\n                        'longitude': float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,\n                        'category': str(row.get('category_level1') or row.get('Category') or ''),\n                        'subcategory': str(row.get('category_level2') or row.get('Subcategory') or ''),\n                        'category_detail': str(row.get('category_level3') or row.get('Detail') or ''),\n                        'business_status': str(row.get('business_status') or row.get('Status') or ''),\n                        'police_force': str(row.get('Police_Force') or row.get('Force') or ''),\n                        'tactical_area': str(row.get('Tactical_Area') or ''),\n                        'local_authority': str(row.get('Local_Authority') or ''),\n                        'rating': float(row.get('rating')) if pd.notna(row.get('rating')) else None,\n                        'rating_count': int(row.get('rating_count')) if pd.notna(row.get('rating_count')) else None,\n                        'phone': str(row.get('phone') or ''),\n                        'website': str(row.get('website_domain') or '')\n                    }\n                    all_retailers.append(retailer)\n                    \n                    # Progress indicator for large datasets\n                    if len(all_retailers) % 50000 == 0:\n                        print(f\"      Processed {len(all_retailers):,} records...\")\n                        \n            except Exception as e:\n                print(f\"    ⚠️  Error in sheet '{sheet_name}': {str(e)}\")\n                continue\n        \n        return all_retailers\n        \n    except Exception as e:\n        print(f\"❌ Error reading {filepath}: {str(e)}\")\n        return []\n\ndef main():\n    print(\"=\" * 70)\n    print(\"🚀 NRCA Retailer Database Converter (600k+ records)\")\n    print(\"=\" * 70)\n    \n    # Find all Excel files\n    excel_files = []\n    for f in os.listdir(REPO_PATH):\n        if f.endswith(\".xlsx\") and not f.startswith(\"~\"):\n            excel_files.append(os.path.join(REPO_PATH, f))\n    \n    if not excel_files:\n        print(f\"\\n❌ No Excel files found in {REPO_PATH}\")\n        return\n    \n    print(f\"\\n📁 Found {len(excel_files)} Excel file(s) to process\")\n    \n    # Collect all retailers from all files\n    all_retailers = []\n    source_files = []\n    \n    for filepath in sorted(excel_files):\n        filename = os.path.basename(filepath)\n        source_files.append(filename)\n        \n        print(f\"\\n📖 Processing: {filename}\")\n        retailers = parse_excel_file(filepath)\n        all_retailers.extend(retailers)\n        \n        print(f\"   ✅ Got {len(retailers):,} records from this file\")\n        print(f\"   📊 Running total: {len(all_retailers):,} records\")\n    \n    # Create JavaScript file with ALL data\n    print(\"\\n\" + \"=\" * 70)\n    print(f\"💾 Creating retailers.js with {len(all_retailers):,} records...\")\n    \n    js_content = \"// NRCA Retailer Database - Auto-generated\\n\"\n    js_content += \"// Complete POI (Point-of-Interest) dataset\\n\"\n    js_content += f\"// Generated from: {', '.join(source_files)}\\n\"\n    js_content += f\"// Total records: {len(all_retailers):,}\\n\"\n    js_content += \"// Structure: Array of retailer objects with full details\\n\\n\"\n    \n    # Convert to JSON\n    print(\"  Converting to JSON format...\")\n    retailers_json = json.dumps(all_retailers, indent=2)\n    \n    js_content += \"const RETAILERS_DATA = \" + retailers_json + \";\\n\"\n    js_content += f\"\\n// Metadata\\n\"\n    js_content += f\"const RETAILER_COUNT = {len(all_retailers):,};\\n\"\n    \n    # Calculate unique values for reference\n    unique_forces = len(set(r.get('police_force', '') for r in all_retailers if r.get('police_force')))\n    unique_localities = len(set(r.get('locality', '') for r in all_retailers if r.get('locality')))\n    unique_categories = len(set(r.get('category', '') for r in all_retailers if r.get('category')))\n    \n    js_content += f\"const UNIQUE_POLICE_FORCES = {unique_forces};\\n\"\n    js_content += f\"const UNIQUE_LOCALITIES = {unique_localities};\\n\"\n    js_content += f\"const UNIQUE_CATEGORIES = {unique_categories};\\n\"\n    \n    # Write complete file to disk\n    print(f\"  Writing to disk: {OUTPUT_FILE}\")\n    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:\n        f.write(js_content)\n    \n    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)\n    print(f\"   ✅ File created: {file_size_mb:.2f} MB\")\n    print(f\"   📊 Total retailers: {len(all_retailers):,}\")\n    print(f\"   🗺️  Police forces: {unique_forces}\")\n    print(f\"   📍 Locations: {unique_localities}\")\n    print(f\"   🏪 Categories: {unique_categories}\")\n    \n    # Push to GitHub\n    print(\"\\n\" + \"=\" * 70)\n    print(\"📤 Pushing to GitHub...\")\n    \n    try:\n        os.chdir(REPO_PATH)\n        subprocess.run([\"git\", \"add\", \"data/retailers.js\"], check=True)\n        subprocess.run([\"git\", \"commit\", \"-m\", f\"Update: Add {len(all_retailers):,} retailer records to database\"], check=True)\n        subprocess.run([\"git\", \"push\", \"origin\", \"main\"], check=True)\n        print(\"   ✅ Successfully pushed to GitHub!\")\n    except subprocess.CalledProcessError as e:\n        print(f\"   ⚠️  Git error: {str(e)}\")\n        print(\"   ℹ️  File created locally. Push manually with:\")\n        print(\"       git add data/retailers.js\")\n        print(f\"       git commit -m 'Add {len(all_retailers):,} retailer records'\")\n        print(\"       git push origin main\")\n    \n    print(\"\\n\" + \"=\" * 70)\n    print(\"✨ Conversion complete!\")\n    print(\"=\" * 70)\n\nif __name__ == \"__main__\":\n    main()
