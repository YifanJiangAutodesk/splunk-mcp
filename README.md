# Splunk to CSV Converter

A powerful Python tool for converting Splunk search results to CSV format. This tool supports any Splunk search query and can handle various data formats automatically.

## Features

- 🔍 **Universal Search Support** - Works with any Splunk query (searches, stats, REST API calls, etc.)
- 📊 **Automatic Data Normalization** - Handles different data types and formats automatically
- 🎯 **Smart Field Ordering** - Prioritizes common fields like _time, user, action, etc.
- 📁 **Excel Compatible** - Outputs UTF-8 with BOM for perfect Excel compatibility
- 👀 **Preview Mode** - View data before saving to file
- ⚙️ **Flexible Configuration** - Support for both username/password and token authentication
- 🚀 **High Performance** - Can handle large datasets efficiently

## Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install requests splunk-sdk python-decouple
   ```
   Or if using the project's virtual environment:
   ```bash
   .\venv\Scripts\activate
   pip install -e .
   ```

## Configuration

Set up your Splunk connection using environment variables:

```bash
# Basic configuration
set SPLUNK_HOST=localhost
set SPLUNK_PORT=8089
set SPLUNK_USERNAME=admin
set SPLUNK_PASSWORD=your_password
set SPLUNK_SCHEME=https
set VERIFY_SSL=false

# For token-based authentication (optional)
set SPLUNK_TOKEN=your_token_here
```

## Quick Start

### Using the Interactive Tool

Run the interactive batch file for easy access:
```bash
convert_splunk_data.bat
```

### Command Line Usage

Basic search export:
```bash
python splunk_to_csv.py --query "index=_audit" --output audit_data.csv
```

Statistics export:
```bash
python splunk_to_csv.py --query "index=* | stats count by sourcetype" --output sourcetype_stats.csv
```

Preview mode (no file saved):
```bash
python splunk_to_csv.py --query "index=_internal | head 10" --preview
```

Custom time range:
```bash
python splunk_to_csv.py --query "search error" --time-range "-7d,now" --max-results 5000 --output errors_week.csv
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--query` | `-q` | Splunk search query (required) | - |
| `--output` | `-o` | Output CSV file path | Auto-generated |
| `--time-range` | `-t` | Time range (earliest,latest) | `-24h,now` |
| `--max-results` | `-m` | Maximum number of results | `10000` |
| `--encoding` | `-e` | CSV file encoding | `utf-8-sig` |
| `--preview` | `-p` | Preview only, don't save file | `false` |
| `--preview-rows` | | Number of preview rows | `5` |

## Usage Examples

### 1. Audit Log Export
```bash
python splunk_to_csv.py --query "index=_audit" --max-results 1000 --output audit_1000.csv
```

### 2. User Activity Analysis
```bash
python splunk_to_csv.py --query "index=_audit | stats count by user action | sort -count" --output user_activity.csv
```

### 3. Index Statistics
```bash
python splunk_to_csv.py --query "| rest /services/data/indexes | table title totalEventCount currentDBSizeMB" --output index_stats.csv
```

### 4. Error Log Analysis
```bash
python splunk_to_csv.py --query "search error OR failed OR exception" --time-range "-7d,now" --output errors_7days.csv
```

### 5. Custom REST API Query
```bash
python splunk_to_csv.py --query "| rest /services/server/info" --output server_info.csv
```

### 6. Preview Large Dataset
```bash
python splunk_to_csv.py --query "index=* | stats count by index sourcetype" --preview --preview-rows 10
```

## Supported Query Types

The tool automatically handles various Splunk query formats:

- **Simple searches**: `index=_audit user=admin`
- **Statistical queries**: `index=* | stats count by sourcetype`
- **REST API calls**: `| rest /services/data/indexes`
- **Complex searches**: `search error | eval severity=if(match(_raw, "CRITICAL"), "high", "low") | stats count by severity`

## Data Processing Features

### Automatic Field Prioritization
Common fields are automatically ordered first:
- `_time`, `timestamp`, `time`
- `user`, `action`, `info`
- `host`, `source`, `sourcetype`, `index`

### Data Type Handling
- **Lists**: Converted to semicolon-separated strings
- **Dictionaries**: Converted to JSON strings
- **Null values**: Converted to empty strings
- **Special characters**: Newlines and tabs are cleaned

### File Size Optimization
- Automatic file size reporting
- Support for large datasets (10,000+ records)
- Memory-efficient processing

## Authentication Methods

### Username/Password Authentication
```bash
set SPLUNK_USERNAME=admin
set SPLUNK_PASSWORD=your_password
```

### Token-Based Authentication
```bash
set SPLUNK_TOKEN=your_token_here
# Username/password will be ignored when token is set
```

### SSL Configuration
```bash
set VERIFY_SSL=false  # For self-signed certificates
set VERIFY_SSL=true   # For production environments
```

## File Output

### CSV Format
- UTF-8 with BOM encoding (Excel compatible)
- Comma-separated values
- Quoted fields for special characters
- Header row with field names

### File Naming
If no output file is specified, files are auto-named:
```
splunk_data_YYYYMMDD_HHMMSS.csv
```

## Error Handling

The tool provides detailed error messages for common issues:

- **Connection errors**: SSL, network, authentication
- **Query errors**: Invalid syntax, permissions
- **File errors**: Write permissions, disk space
- **Data errors**: Malformed results, encoding issues

## Performance Tips

1. **Use specific time ranges** to limit data volume
2. **Set appropriate max-results** for large datasets
3. **Use preview mode** to test queries before full export
4. **Filter data in Splunk** rather than post-processing

## Troubleshooting

### Common Issues

**SSL Certificate Error**:
```bash
set VERIFY_SSL=false
```

**Authentication Failed**:
- Check username/password or token
- Verify Splunk server accessibility
- Check user permissions

**No Data Returned**:
- Verify query syntax
- Check time range
- Confirm data exists in specified indexes

**Large File Processing**:
- Increase max-results gradually
- Use time-based chunking for very large datasets
- Consider using Splunk's native export features for massive datasets

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## License

This project is open source and available under the MIT License.