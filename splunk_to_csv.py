#!/usr/bin/env python3
"""
Splunk to CSV Converter Tool
Convert any Splunk search results to CSV format via direct connection

Usage:
python splunk_to_csv.py --query "index=_audit" --output audit_data.csv
python splunk_to_csv.py --query "index=* | stats count by sourcetype" --time-range "-7d,now"
"""

import json
import csv
import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

# Import required libraries
try:
    import requests
    import splunklib.client
    from decouple import config
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please run: pip install requests splunk-sdk python-decouple")
    sys.exit(1)

# Splunk connection configuration
SPLUNK_HOST = os.environ.get("SPLUNK_HOST", "localhost")
SPLUNK_PORT = int(os.environ.get("SPLUNK_PORT", "18089"))
SPLUNK_SCHEME = os.environ.get("SPLUNK_SCHEME", "https")
SPLUNK_USERNAME = os.environ.get("SPLUNK_USERNAME", "admin")
SPLUNK_PASSWORD = os.environ.get("SPLUNK_PASSWORD", "changeme123")
SPLUNK_TOKEN = os.environ.get("SPLUNK_TOKEN")
VERIFY_SSL = config("VERIFY_SSL", default="false", cast=bool)

class SplunkToCSV:
    def __init__(self):
        self.service = None
        
    def connect_to_splunk(self):
        """Connect to Splunk"""
        try:
            if SPLUNK_TOKEN:
                print(f"🔌 Connecting to Splunk with token: {SPLUNK_SCHEME}://{SPLUNK_HOST}:{SPLUNK_PORT}")
                self.service = splunklib.client.connect(
                    host=SPLUNK_HOST,
                    port=SPLUNK_PORT,
                    scheme=SPLUNK_SCHEME,
                    verify=VERIFY_SSL,
                    token=f"Bearer {SPLUNK_TOKEN}"
                )
            else:
                print(f"🔌 Connecting to Splunk with credentials: {SPLUNK_SCHEME}://{SPLUNK_HOST}:{SPLUNK_PORT}")
                self.service = splunklib.client.connect(
                    host=SPLUNK_HOST,
                    port=SPLUNK_PORT,
                    username=SPLUNK_USERNAME,
                    password=SPLUNK_PASSWORD,
                    scheme=SPLUNK_SCHEME,
                    verify=VERIFY_SSL
                )
            print("✅ Connected to Splunk successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Splunk: {str(e)}")
            return False
    
    def execute_search(self, query: str, earliest_time: str = "-24h", 
                      latest_time: str = "now", max_results: int = 10000) -> List[Dict[str, Any]]:
        """Execute Splunk search"""
        if not self.service:
            raise Exception("Not connected to Splunk")
        
        # Auto-add search prefix if needed
        stripped_query = query.lstrip()
        if not (stripped_query.startswith('|') or stripped_query.lower().startswith('search')):
            query = f"search {query}"
        
        print(f"🔍 Executing search: {query}")
        print(f"⏰ Time range: {earliest_time} to {latest_time}")
        
        try:
            # Create search job
            kwargs_search = {
                "earliest_time": earliest_time,
                "latest_time": latest_time,
                "preview": False,
                "exec_mode": "blocking"
            }
            
            job = self.service.jobs.create(query, **kwargs_search)
            
            # Get results
            result_stream = job.results(output_mode='json', count=max_results)
            results_data = json.loads(result_stream.read().decode('utf-8'))
            
            results = results_data.get("results", [])
            print(f"📊 Found {len(results)} records")
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            raise
    
    def normalize_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Normalize data format"""
        if not data:
            return []
        
        # Collect all possible fields
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        # Sort fields, prioritize common fields
        priority_fields = ['_time', 'timestamp', 'time', 'user', 'action', 'info', 'host', 'source', 'sourcetype', 'index']
        sorted_fields = []
        
        # Add priority fields first
        for field in priority_fields:
            if field in all_fields:
                sorted_fields.append(field)
                all_fields.remove(field)
        
        # Add remaining fields alphabetically
        sorted_fields.extend(sorted(all_fields))
        
        # Normalize each record
        normalized_data = []
        for record in data:
            normalized_record = {}
            for field in sorted_fields:
                value = record.get(field, "")
                
                # Handle special values
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                elif isinstance(value, dict):
                    value = json.dumps(value, ensure_ascii=False)
                elif value is None:
                    value = ""
                else:
                    value = str(value)
                
                # Clean newlines and tabs
                value = value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                normalized_record[field] = value
            
            normalized_data.append(normalized_record)
        
        return normalized_data
    
    def save_to_csv(self, data: List[Dict[str, str]], output_file: str, encoding: str = 'utf-8-sig'):
        """Save data to CSV file"""
        if not data:
            print("⚠️ No data to save")
            return False
        
        try:
            # Get field names
            fieldnames = list(data[0].keys())
            
            # Write CSV file
            with open(output_file, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✅ Data saved to: {output_file}")
            print(f"📄 File contains {len(data)} rows, {len(fieldnames)} fields")
            print(f"🏷️ Fields: {', '.join(fieldnames[:10])}{'...' if len(fieldnames) > 10 else ''}")
            
            # Show file size
            file_size = os.path.getsize(output_file)
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            elif file_size > 1024:
                size_str = f"{file_size / 1024:.2f} KB"
            else:
                size_str = f"{file_size} bytes"
            print(f"💾 File size: {size_str}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save CSV file: {str(e)}")
            return False
    
    def preview_data(self, data: List[Dict[str, str]], rows: int = 5):
        """Preview data"""
        if not data:
            print("No data to preview")
            return
        
        print(f"\n📋 Data Preview (first {min(rows, len(data))} rows):")
        print("=" * 80)
        
        # Get field names
        fieldnames = list(data[0].keys())
        
        # Show header
        header = " | ".join(f"{field[:15]:15}" for field in fieldnames[:6])
        print(header)
        print("-" * len(header))
        
        # Show data rows
        for i, row in enumerate(data[:rows]):
            row_data = " | ".join(f"{str(row.get(field, ''))[:15]:15}" for field in fieldnames[:6])
            print(f"{row_data}")
        
        if len(fieldnames) > 6:
            print(f"\n... {len(fieldnames) - 6} more fields not displayed")
        
        print("=" * 80)

def parse_time_range(time_range: str) -> tuple:
    """Parse time range"""
    if ',' in time_range:
        earliest, latest = time_range.split(',', 1)
        return earliest.strip(), latest.strip()
    else:
        return time_range.strip(), "now"

def main():
    parser = argparse.ArgumentParser(
        description="Splunk to CSV Converter Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s --query "index=_audit" --output audit.csv
  %(prog)s --query "index=* | stats count by sourcetype" --time-range "-7d,now" --max-results 5000
  %(prog)s --query "search error | head 100" --preview
  %(prog)s --query "| rest /services/server/info" --output server_info.csv --encoding utf-8
        """
    )
    
    parser.add_argument("--query", "-q", required=True, help="Splunk search query")
    parser.add_argument("--output", "-o", help="Output CSV file path")
    parser.add_argument("--time-range", "-t", default="-24h,now", 
                       help="Time range, format: earliest,latest (default: -24h,now)")
    parser.add_argument("--max-results", "-m", type=int, default=10000,
                       help="Maximum number of results (default: 10000)")
    parser.add_argument("--encoding", "-e", default="utf-8-sig",
                       help="CSV file encoding (default: utf-8-sig, Excel compatible)")
    parser.add_argument("--preview", "-p", action="store_true",
                       help="Preview data only, don't save file")
    parser.add_argument("--preview-rows", type=int, default=5,
                       help="Number of preview rows (default: 5)")
    
    args = parser.parse_args()
    
    # Parse time range
    earliest_time, latest_time = parse_time_range(args.time_range)
    
    # Generate default output filename
    if not args.output and not args.preview:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"splunk_data_{timestamp}.csv"
    
    # Create converter
    converter = SplunkToCSV()
    
    try:
        # Connect to Splunk
        if not converter.connect_to_splunk():
            sys.exit(1)
        
        # Execute search
        results = converter.execute_search(
            args.query, 
            earliest_time, 
            latest_time, 
            args.max_results
        )
        
        if not results:
            print("⚠️ No matching data found")
            sys.exit(0)
        
        # Normalize data
        normalized_data = converter.normalize_data(results)
        
        # Preview data
        converter.preview_data(normalized_data, args.preview_rows)
        
        # Save to CSV (if not preview only mode)
        if not args.preview:
            success = converter.save_to_csv(normalized_data, args.output, args.encoding)
            if not success:
                sys.exit(1)
        else:
            print("\n🔍 Preview mode - file not saved")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
