@echo off
cd /d "%~dp0"
python build_html.py
git add docs/index.html README.md
git diff --cached --quiet
if %ERRORLEVEL%==0 (
  echo No changes to deploy.
) else (
  git commit -m "Update travel comparison page"
  git push
  echo.
  echo Deployed: https://adventistcho-art.github.io/chicago-trip/
)
pause
