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
echo Import vers PostgreSQL LOCAL
echo ==============================

%PG_BIN%\pg_restore.exe ^
  -h localhost ^
  -p 5432 ^
  -U postgres ^
  --dbname=%LOCAL_DB% ^
  --clean ^
  --no-owner ^
  %DUMP_FILE%

IF ERRORLEVEL 1 (
  echo ❌ Erreur lors de l import LOCAL
  pause
  exit /b 1
)

echo ✅ Import LOCAL terminé avec succès
echo.

echo ==============================
echo✅ Base PROD copiée en LOCAL
echo ==============================
pause