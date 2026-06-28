# Démarrage rapide - Air & Water Quality Monitor
# Pour Windows PowerShell

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Air & Water Quality Monitor" -ForegroundColor Cyan
Write-Host " Serveur HTTP Démarrage" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Python n'est pas installé!" -ForegroundColor Red
    Write-Host "Installer depuis: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "N'oubliez pas de cocher 'Add Python to PATH'" -ForegroundColor Yellow
    Read-Host "Appuyer sur Entrée pour fermer"
    exit 1
}

Write-Host ""

# Créer l'environnement virtuel s'il n'existe pas
if (-not (Test-Path ".venv")) {
    Write-Host "Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Environnement virtuel créé" -ForegroundColor Green
}

Write-Host ""
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow

# Activer l'environnement virtuel
& .\.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "Lancement du serveur HTTP sur le port 8000..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Serveur démarré!" -ForegroundColor Green
Write-Host ""
Write-Host "Ouvrir dans votre navigateur:" -ForegroundColor Cyan
Write-Host "http://localhost:8000/monitoring_dashboard.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour arrêter: Appuyer sur Ctrl + C" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Lancer le serveur HTTP
python -m http.server 8000 --directory frontend
