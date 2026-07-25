@echo off
cd /d "%~dp0"
python build_html.py
if not exist .git (
  git init
  git branch -M main
)
git add docs/index.html .gitignore README.md
git diff --cached --quiet
if %ERRORLEVEL%==0 (
  echo No changes to deploy.
) else (
  git commit -m "Update travel comparison page"
)
echo.
echo === GitHub Pages deploy ===
echo 1. Create a new repo on https://github.com/new
echo 2. Run these commands ^(replace YOUR_USER and YOUR_REPO^):
echo.
echo    git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
echo    git push -u origin main
echo.
echo 3. GitHub repo - Settings - Pages - Source: GitHub Actions
echo 4. After push, your site will be at:
echo    https://YOUR_USER.github.io/YOUR_REPO/
echo.
pause
