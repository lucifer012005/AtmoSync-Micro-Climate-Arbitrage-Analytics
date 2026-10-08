@echo off

set ROOT=C:\Users\SACHIN\OneDrive\Desktop\Intern\AtmoSync\AtmoSync
set LOG=%ROOT%\logs\dbt_schedule.log

echo ========================================== >> "%LOG%"
echo PIPELINE STARTED: %date% %time% >> "%LOG%"

echo Running dbt build... >> "%LOG%"

"%ROOT%\venv\Scripts\dbt.exe" build ^
--project-dir "%ROOT%\dbt\atmo_sync" ^
--profiles-dir "C:\Users\SACHIN\.dbt" >> "%LOG%" 2>&1

if errorlevel 1 (
    echo DBT BUILD FAILED. EMAIL ALERT SKIPPED. >> "%LOG%"
    echo PIPELINE FINISHED WITH ERROR: %date% %time% >> "%LOG%"
    exit /b 1
)

echo DBT BUILD SUCCESSFUL. >> "%LOG%"
echo Checking rerouting alerts... >> "%LOG%"

"%ROOT%\venv\Scripts\python.exe" "%ROOT%\alerts\email_alert.py" >> "%LOG%" 2>&1

if errorlevel 1 (
    echo EMAIL ALERT CHECK FAILED. >> "%LOG%"
    echo PIPELINE FINISHED WITH ERROR: %date% %time% >> "%LOG%"
    exit /b 1
)

echo ALERT CHECK COMPLETED. >> "%LOG%"
echo PIPELINE FINISHED SUCCESSFULLY: %date% %time% >> "%LOG%"