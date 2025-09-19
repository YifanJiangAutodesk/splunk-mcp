@echo off
chcp 65001 >nul
echo.
echo =====================================================
echo     Splunk to CSV Converter - Quick Tool
echo =====================================================
echo.

:: Set environment variables
set VERIFY_SSL=false
set SPLUNK_HOST=localhost
set SPLUNK_PORT=18089
set SPLUNK_USERNAME=admin
set SPLUNK_PASSWORD=changeme123

:: Activate virtual environment
call .\venv\Scripts\activate.bat

echo Please select an operation:
echo.
echo 1. Export _audit index data (latest 1000 records)
echo 2. Export user activity statistics
echo 3. Export all index statistics
echo 4. Export error logs (last 1 hour)
echo 5. Custom search query
echo 6. Preview mode (don't save file)
echo 0. Exit
echo.

set /p choice="Enter your choice (0-6): "

if "%choice%"=="1" (
    echo.
    echo Exporting _audit index data...
    python splunk_to_csv.py --query "index=_audit" --max-results 1000 --output audit_data.csv
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Exporting user activity statistics...
    python splunk_to_csv.py --query "index=_audit | stats count by user action | sort -count" --output user_action_stats.csv
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Exporting index statistics...
    python splunk_to_csv.py --query "| rest /services/data/indexes | table title totalEventCount currentDBSizeMB maxDataSize" --output indexes_stats.csv
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Exporting error logs...
    python splunk_to_csv.py --query "search error OR failed OR exception OR ERROR" --time-range "-1h,now" --max-results 500 --output errors_recent.csv
    goto end
)

if "%choice%"=="5" (
    echo.
    set /p custom_query="Enter Splunk search query: "
    set /p output_file="Enter output filename (without extension): "
    echo.
    echo Executing custom query...
    python splunk_to_csv.py --query "%custom_query%" --output "%output_file%.csv"
    goto end
)

if "%choice%"=="6" (
    echo.
    set /p preview_query="Enter search query to preview: "
    echo.
    echo Previewing data...
    python splunk_to_csv.py --query "%preview_query%" --preview
    goto end
)

if "%choice%"=="0" (
    echo Goodbye!
    goto end
)

echo Invalid choice, please run the script again.

:end
echo.
pause