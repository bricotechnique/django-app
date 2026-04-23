@echo off
REM ============================================
REM Backup PostgreSQL PROD (Railway) -> LOCAL
REM ============================================

REM ---- Chemins PostgreSQL ----
set PG_BIN="C:\Program Files\PostgreSQL\18\bin"

REM ---- DATABASE URL PROD (Railway - PUBLIC) ----
set DATABASE_URL=postgresql://postgres:ggKAYkmImDrPBWSZUEvBUeCPUHKbQWra@yamabiko.proxy.rlwy.net:50573/railway

REM ---- Nom base locale ----
set LOCAL_DB=reglages_machine_dev
set LOCAL_USER=postgres
set LOCAL_HOST=localhost
set LOCAL_PORT=5432

REM ---- Fichier dump ----
set DUMP_FILE=prod_backup.dump

echo.
echo ==============================
echo Export de la base PROD Railway
echo ==============================

%PG_BIN%\pg_dump.exe ^
  --dbname=%DATABASE_URL% ^
  --format=custom ^
  --no-owner ^
  --file=%DUMP_FILE%

IF ERRORLEVEL 1 (
  echo ❌ Erreur lors de l export PROD
  pause
  exit /b 1
)

echo ✅ Export PROD terminé : %DUMP_FILE%
echo.

echo ==============================
echo Recréation de la base locale
echo ==============================

%PG_BIN%\psql.exe ^
  -h %LOCAL_HOST% ^
  -p %LOCAL_PORT% ^
  -U %LOCAL_USER% ^
  -d postgres ^
  -c "DROP DATABASE IF EXISTS %LOCAL_DB%;"

IF ERRORLEVEL 1 (
  echo ❌ Erreur lors du DROP DATABASE
  pause
  exit /b 1
)

%PG_BIN%\psql.exe ^
  -h %LOCAL_HOST% ^
  -p %LOCAL_PORT% ^
  -U %LOCAL_USER% ^
  -d postgres ^
  -c "CREATE DATABASE %LOCAL_DB%;"

IF ERRORLEVEL 1 (
  echo ❌ Erreur lors du CREATE DATABASE
  pause
  exit /b 1
)

echo ✅ Base locale recréée
echo.

echo ==============================
echo Import vers PostgreSQL LOCAL
echo ==============================

%PG_BIN%\pg_restore.exe ^
  -h %LOCAL_HOST% ^
  -p %LOCAL_PORT% ^
  -U %LOCAL_USER% ^
  -d %LOCAL_DB% ^
  --no-owner ^
  --no-privileges ^
  %DUMP_FILE%

IF ERRORLEVEL 1 (
  echo ❌ Erreur lors de l import LOCAL
  pause
  exit /b 1
)

echo ✅ Import LOCAL terminé avec succès
echo.

echo ==============================
echo ✅ Base PROD copiée en LOCAL
echo ==============================
pause