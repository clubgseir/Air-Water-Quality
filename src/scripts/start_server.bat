@echo off
REM Démarrage rapide - Air & Water Quality Monitor
REM Pour Windows uniquement

echo.
echo ========================================
echo  Air & Water Quality Monitor
echo  Serveur HTTP Démarrage
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé!
    echo Installer Python depuis: https://www.python.org/downloads/
    echo N'oubliez pas de cocher "Add Python to PATH"
    pause
    exit /b 1
)

echo ✓ Python détecté
echo.

REM Créer l'environnement virtuel s'il n'existe pas
if not exist ".venv" (
    echo Création de l'environnement virtuel...
    python -m venv .venv
    echo ✓ Environnement virtuel créé
)

echo.
echo Activation de l'environnement virtuel...
call .venv\Scripts\Activate.ps1

echo Lancement du serveur HTTP sur le port 8000...
echo.
echo ========================================
echo ✓ Serveur démarré!
echo.
echo Ouvrir dans votre navigateur:
echo http://localhost:8000/monitoring_dashboard.html
echo.
echo Pour arrêter: Appuyer sur Ctrl + C
echo ========================================
echo.

python -m http.server 8000 --directory frontend
