#!/usr/bin/env python3
"""
Script to convert skincare catalog Excel file to products.json format.
Reads actual data from Excel and converts to the required JSON structure.
"""

import pandas as pd
import json
import sys
from pathlib import Path

def convert_excel_to_json(excel_file_path, output_json_path=None):
    """
    Convert Excel file to products.json format.
    
    Args:
        excel_file_path (str): Path to the Excel file
        output_json_path (str, optional): Output JSON file path. Defaults to 'products.json'
    """
    
    if output_json_path is None:
        output_json_path = "products.json"
    
    try:
        # Read Excel file
        print(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Display basic info about the data
        print(f"Found {len(df)} products")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
        
        # Convert to the required JSON format
        products = []
        
        for _, row in df.iterrows():
            # Handle different possible column names
            product = {}
            
            # Product ID
            product["product_id"] = str(row.get("product_id", "")).strip()
            
            # Product Name
            product["name"] = str(row.get("name", "")).strip()
            
            # Category (convert to lowercase)
            category = str(row.get("category", "")).strip().lower()
            product["category"] = category
            
            # Description
            product["description"] = str(row.get("description", "")).strip()
            
            # Top Ingredients
            product["top_ingredients"] = str(row.get("top_ingredients", "")).strip()
            
            # Tags (keep as-is, assuming pipe-separated format)
            product["tags"] = str(row.get("tags", "")).strip()
            
            # Price (handle different possible column names)
            price_cols = ["price (USD)", "price_usd", "price", "Price (USD)", "Price"]
            price = None
            for col in price_cols:
                if col in row and pd.notna(row[col]):
                    price = float(row[col])
                    break
            product["price_usd"] = price if price is not None else 0.0
            
            # Margin (handle different possible column names and formats)
            margin_cols = ["margin (%)", "margin_percent", "margin", "Margin (%)", "Margin"]
            margin = None
            for col in margin_cols:
                if col in row and pd.notna(row[col]):
                    margin_val = float(row[col])
                    # If margin is in decimal format (0.45), convert to percentage (45.0)
                    if margin_val <= 1.0:
                        margin = round(margin_val * 100, 1)
                    else:
                        margin = round(margin_val, 1)
                    break
            product["margin_percent"] = margin if margin is not None else 0.0
            
            products.append(product)
        
        # Save to JSON file
        print(f"\nSaving to {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully converted {len(products)} products to {output_json_path}")
        
        # Display summary
        categories = {}
        for product in products:
            cat = product["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nProducts by category:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: File '{excel_file_path}' not found")
        return False
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return False

def main():
    """Main function to run the converter."""
    
    # Default file names
    excel_file = "skincare_catalog.xlsx"  # Adjust this to your actual file name
    json_file = "products.json"
    
    # Check if custom file paths are provided as command line arguments
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    if len(sys.argv) > 2:
        json_file = sys.argv[2]
    
    # Check if Excel file exists
    if not Path(excel_file).exists():
        print(f"❌ Excel file '{excel_file}' not found in current directory")
        print(f"Usage: python {sys.argv[0]} [excel_file] [output_json_file]")
        print(f"Example: python {sys.argv[0]} skincare_catalog.xlsx products.json")
        return
    
    # Convert the file
    success = convert_excel_to_json(excel_file, json_file)
    
    if success:
        print(f"\n🎉 Conversion completed successfully!")
        print(f"Your products.json file is ready to use.")
    else:
        print(f"\n💥 Conversion failed. Please check the error messages above.")

if __name__ == "__main__":
    main()


# Alternative function for Jupyter notebooks or direct usage
def quick_convert(excel_file="skincare_catalog.xlsx"):
    """
    Quick conversion function for interactive use.
    
    Usage:
        quick_convert("your_file.xlsx")
    """
    return convert_excel_to_json(excel_file)