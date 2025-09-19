# CSV Export MCP Tool Documentation

## Overview

A new MCP tool `save_data_to_csv` has been added to the Splunk MCP server to provide CSV export functionality. This tool follows proper separation of concerns by focusing solely on data conversion and file saving, working in conjunction with the existing `search_splunk` tool.

## Architecture

### Separation of Concerns

- **`search_splunk`**: Handles Splunk search execution and returns raw data
- **`save_data_to_csv`**: Handles data normalization and CSV file creation

This design follows the single responsibility principle and avoids duplication.

## MCP Tool: save_data_to_csv

### Purpose
Convert structured data (like Splunk search results) to CSV format with automatic normalization and Excel compatibility.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data` | `List[Dict[str, Any]]` | Yes | - | List of dictionaries containing the data to export |
| `output_file` | `str` | Yes | - | Path where the CSV file will be saved |
| `encoding` | `str` | No | `utf-8-sig` | CSV file encoding (Excel compatible by default) |

### Returns

```json
{
  "success": true,
  "file_path": "output.csv",
  "rows": 100,
  "fields": 8,
  "field_names": ["_time", "user", "action", "info", "host"],
  "file_size": 15420,
  "file_size_str": "15.07 KB",
  "encoding": "utf-8-sig"
}
```

## Features

### 1. Smart Data Normalization

- **Lists**: Converted to semicolon-separated strings (`["a", "b", "c"]` → `"a; b; c"`)
- **Dictionaries**: Converted to JSON strings (`{"key": "value"}` → `'{"key": "value"}'`)
- **Null values**: Converted to empty strings
- **Special characters**: Newlines and tabs are cleaned/replaced with spaces

### 2. Intelligent Field Ordering

Priority fields are automatically ordered first:
- `_time`, `timestamp`, `time`
- `user`, `action`, `info` 
- `host`, `source`, `sourcetype`, `index`

Remaining fields are sorted alphabetically.

### 3. Excel Compatibility

- Uses UTF-8 with BOM encoding (`utf-8-sig`)
- Proper CSV escaping for special characters
- Handles Unicode characters correctly

### 4. Error Handling

- Validates input data
- Creates directories if they don't exist
- Provides detailed error messages
- Graceful handling of empty data sets

## Usage Examples

### Basic Workflow

```python
# Step 1: Get data from Splunk
search_results = await search_splunk("index=_audit", max_results=1000)

# Step 2: Save to CSV
result = await save_data_to_csv(search_results, "audit_export.csv")

if result['success']:
    print(f"Exported {result['rows']} rows to {result['file_path']}")
else:
    print(f"Error: {result['error']}")
```

### Advanced Usage with Custom Encoding

```python
# Export with specific encoding
result = await save_data_to_csv(
    data=search_results,
    output_file="data/exports/audit_2025.csv", 
    encoding="utf-8"
)
```

### Statistics Export

```python
# Get statistics from Splunk
stats = await search_splunk("index=_audit | stats count by user action | sort -count")

# Save statistics to CSV
result = await save_data_to_csv(stats, "user_activity_stats.csv")
```

## Data Type Handling Examples

### Input Data
```python
complex_data = [
    {
        "timestamp": "2025-09-19T10:00:00Z",
        "user": "admin",
        "tags": ["security", "login", "success"],
        "metadata": {"ip": "192.168.1.1", "browser": "Chrome"},
        "score": 95.5,
        "notes": None
    }
]
```

### CSV Output
```csv
timestamp,user,tags,metadata,score,notes
2025-09-19T10:00:00Z,admin,security; login; success,"{""ip"": ""192.168.1.1"", ""browser"": ""Chrome""}",95.5,
```

## Error Scenarios

### Empty Data
```python
result = await save_data_to_csv([], "empty.csv")
# Returns: {"success": false, "error": "No data provided to save"}
```

### Invalid File Path
```python
result = await save_data_to_csv(data, "/invalid/path/file.csv")
# Returns: {"success": false, "error": "Permission denied or path not found"}
```

## File Output Characteristics

- **Headers**: First row contains field names
- **Encoding**: UTF-8 with BOM (Excel compatible)
- **Separator**: Comma (`,`)
- **Quoting**: Automatic for fields containing special characters
- **Line endings**: Platform appropriate (CRLF on Windows, LF on Unix)

## Integration with Existing MCP Tools

The CSV export tool integrates seamlessly with all existing Splunk MCP tools:

```python
# With search_splunk
search_data = await search_splunk("index=_internal")
await save_data_to_csv(search_data, "internal_logs.csv")

# With list_indexes
indexes = await list_indexes()
await save_data_to_csv([indexes], "indexes_info.csv")

# With get_indexes_and_sourcetypes
index_stats = await get_indexes_and_sourcetypes()
await save_data_to_csv([index_stats], "index_sourcetype_stats.csv")
```

## Best Practices

1. **Use descriptive file names** with timestamps for tracking
2. **Check the success flag** before assuming file creation succeeded
3. **Handle large datasets** by limiting results in the search phase
4. **Use appropriate encoding** for your target application (Excel vs. other tools)
5. **Validate file paths** to ensure write permissions

## Testing

The tool has been thoroughly tested with:
- ✅ Normal data conversion
- ✅ Complex data structures (nested objects, arrays)
- ✅ Empty data validation
- ✅ Unicode character handling
- ✅ Field prioritization
- ✅ Excel compatibility
- ✅ Error scenarios

## Performance Considerations

- Memory efficient for datasets up to 10,000 records
- Automatic file size reporting
- Minimal data copying during normalization
- Optimized field ordering algorithm

This tool provides a robust, production-ready solution for exporting Splunk data to CSV format while maintaining clean separation of concerns in the MCP architecture.
