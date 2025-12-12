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
DATA_FILE = r"C:\Users\GeorgeKirby\OneDrive - National Business Crime Solution\Mass DATA DUMP\Retail_Data_Template_With_Formulas.xlsx"
DATA_OUTPUT_PATH = os.path.join(REPO_PATH, "data")
OUTPUT_FILE = os.path.join(DATA_OUTPUT_PATH, "retailers.js")

# Ensure data directory exists
os.makedirs(DATA_OUTPUT_PATH, exist_ok=True)

def parse_excel_file(filepath):
    """Parse Excel file and extract ALL 600k+ retailer POI data"""
    try:
        print(f"  Reading Excel file: {os.path.basename(filepath)}")
        print(f"  File size: {os.path.getsize(filepath) / (1024*1024):.2f} MB")
        
        all_retailers = []
        
        # Read Excel file - handle large files
        print("  Loading into memory...")
        df = pd.read_excel(filepath)
        
        print(f"  Total rows in file: {len(df):,}")
        
        # Process EVERY row - don't filter out any data
        print("  Processing all records...")
        for idx, row in df.iterrows():
            retailer = {
                'id': str(row.get('poi_id') or row.get('ID') or idx),
                'name': str(row.get('name') or row.get('Name') or 'Unknown'),
                'locality': str(row.get('locality') or row.get('Locality') or ''),
                'postcode': str(row.get('postcode') or row.get('Postcode') or ''),
                'address': str(row.get('address') or row.get('Address') or ''),
                'latitude': float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                'longitude': float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,
                'category': str(row.get('category_level1') or row.get('Category') or ''),
                'subcategory': str(row.get('category_level2') or row.get('Subcategory') or ''),
                'category_detail': str(row.get('category_level3') or row.get('Detail') or ''),
                'business_status': str(row.get('business_status') or row.get('Status') or ''),
                'police_force': str(row.get('Police_Force') or row.get('Force') or ''),
                'tactical_area': str(row.get('Tactical_Area') or ''),
                'local_authority': str(row.get('Local_Authority') or ''),
                'rating': float(row.get('rating')) if pd.notna(row.get('rating')) else None,
                'rating_count': int(row.get('rating_count')) if pd.notna(row.get('rating_count')) else None,
                'phone': str(row.get('phone') or ''),
                'website': str(row.get('website_domain') or '')
            }
            all_retailers.append(retailer)
            
            # Progress indicator for large datasets
            if (idx + 1) % 50000 == 0:
                print(f"      Processed {idx + 1:,} records...")
        
        print(f"  ✅ Successfully loaded {len(all_retailers):,} retailer records")
        return all_retailers
        
    except Exception as e:
        print(f"❌ Error reading {filepath}: {str(e)}")
        return []

def main():
    print("=" * 70)
    print("🚀 NRCA Retailer Database Converter (600k+ records)")
    print("=" * 70)
    
    # Check if file exists
    if not os.path.exists(DATA_FILE):
        print(f"\n❌ File not found: {DATA_FILE}")
        print("Please check the file path and try again.")
        return
    
    print(f"\n📄 Data file: {DATA_FILE}")
    
    # Parse the Excel file
    print(f"\n📖 Reading retailer data...")
    all_retailers = parse_excel_file(DATA_FILE)
    
    if not all_retailers:
        print("❌ No retailers extracted from file!")
        return
    
    # Create JavaScript file with ALL data
    print("\n" + "=" * 70)
    print(f"💾 Creating retailers.js with {len(all_retailers):,} records...")
    
    js_content = "// NRCA Retailer Database - Auto-generated\n"
    js_content += "// Complete POI (Point-of-Interest) dataset\n"
    js_content += f"// Source: Retail_Data_Template_With_Formulas.xlsx\n"
    js_content += f"// Total records: {len(all_retailers):,}\n"
    js_content += "// Structure: Array of retailer objects with full details\n\n"
    
    # Convert to JSON
    print("  Converting to JSON format...")
    retailers_json = json.dumps(all_retailers, indent=2)
    
    js_content += "const RETAILERS_DATA = " + retailers_json + ";\n"
    js_content += f"\n// Metadata\n"
    
    # Calculate unique values for reference
    unique_forces = len(set(r.get('police_force', '') for r in all_retailers if r.get('police_force')))
    unique_localities = len(set(r.get('locality', '') for r in all_retailers if r.get('locality')))
    unique_categories = len(set(r.get('category', '') for r in all_retailers if r.get('category')))
    
    js_content += f"const RETAILER_COUNT = {len(all_retailers):,};\n"
    js_content += f"const UNIQUE_POLICE_FORCES = {unique_forces};\n"
    js_content += f"const UNIQUE_LOCALITIES = {unique_localities};\n"
    js_content += f"const UNIQUE_CATEGORIES = {unique_categories};\n"
    
    # Write complete file to disk
    print(f"  Writing to disk: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"   ✅ File created: {file_size_mb:.2f} MB")
    print(f"   📊 Total retailers: {len(all_retailers):,}")
    print(f"   🗺️  Police forces: {unique_forces}")
    print(f"   📍 Locations: {unique_localities}")
    print(f"   🏪 Categories: {unique_categories}")
    
    # Push to GitHub
    print("\n" + "=" * 70)
    print("📤 Pushing to GitHub...")
    
    try:
        os.chdir(REPO_PATH)
        subprocess.run(["git", "add", "data/retailers.js"], check=True)
        subprocess.run(["git", "commit", "-m", f"Update: Add {len(all_retailers):,} retailer records to database"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("   ✅ Successfully pushed to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Git error: {str(e)}")
        print("   ℹ️  File created locally. Push manually with:")
        print("       git add data/retailers.js")
        print(f"       git commit -m 'Add {len(all_retailers):,} retailer records'")
        print("       git push origin main")
    
    print("\n" + "=" * 70)
    print("✨ Conversion complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
