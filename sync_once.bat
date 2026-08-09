@echo off
cd /d "%~dp0"
echo.
echo [1/2] 브라우저가 열리면 CAPTCHA가 뜰 경우 직접 통과해 주세요.
echo [2/2] Skyscanner / KAYAK / Google / Airbnb / NYC-ORD 국내선 가격을 수집하고 flights.html 을 갱신합니다.
echo.
python sync_all.py
if exist flights.html start "" "%~dp0flights.html"
pause
