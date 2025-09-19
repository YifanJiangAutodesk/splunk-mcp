@echo off
echo Splunk to CSV Converter - Usage Examples
echo ==========================================
echo.

echo 1. Export _audit index data (latest 1000 records):
echo python splunk_to_csv.py --query "index=_audit" --max-results 1000 --output audit_1000.csv
echo.

echo 2. Export index statistics:
echo python splunk_to_csv.py --query "| rest /services/data/indexes | table title totalEventCount currentDBSizeMB" --output indexes_stats.csv
echo.

echo 3. Export error logs (last 7 days):
echo python splunk_to_csv.py --query "search error OR failed OR exception" --time-range "-7d,now" --output errors_7days.csv
echo.

echo 4. Preview search results (don't save file):
echo python splunk_to_csv.py --query "index=_internal | head 10" --preview
echo.

echo 5. Export user activity statistics:
echo python splunk_to_csv.py --query "index=_audit | stats count by user action | sort -count" --output user_activity.csv
echo.

echo Choose an example to run, or press any key to exit...
pause