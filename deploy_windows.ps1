# ============================================================================
# Rogue Detection System - Windows Deployment Script
# Supports: Windows 10/11, Windows Server 2016/2019/2022
# ============================================================================

#Requires -RunAsAdministrator

# Configuration
$AppName = "RogueDetection"
$AppDir = "C:\RogueDetection"
$PythonVersion = "3.9"
$NSSMVersion = "2.24"

# Colors
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Header { 
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "  $args" -ForegroundColor Blue
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
}

# ============================================================================
# Helper Functions
# ============================================================================

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Install-Python {
    Write-Header "Installing Python"
    
    $pythonUrl = "https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
    
    Write-Info "Downloading Python..."
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
    
    Write-Info "Installing Python..."
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    
    Remove-Item $installerPath
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Success "Python installed"
}

# ============================================================================
# Installation Steps
# ============================================================================

function Step1-CheckPrerequisites {
    Write-Header "Step 1: Checking Prerequisites"
    
    if (-not (Test-Administrator)) {
        Write-Error "This script must be run as Administrator"
        exit 1
    }
    Write-Success "Running as Administrator"
    
    if (-not (Test-PythonInstalled)) {
        Write-Warning "Python not found"
        $install = Read-Host "Do you want to install Python? (Y/N)"
        if ($install -eq "Y" -or $install -eq "y") {
            Install-Python
        } else {
            Write-Error "Python is required. Please install Python 3.8+ and run this script again."
            exit 1
        }
    } else {
        Write-Success "Python is installed"
    }
}

function Step2-CreateDirectory {
    Write-Header "Step 2: Creating Application Directory"
    
    if (Test-Path $AppDir) {
        Write-Warning "Directory $AppDir already exists"
        $overwrite = Read-Host "Do you want to overwrite? (Y/N)"
        if ($overwrite -ne "Y" -and $overwrite -ne "y") {
            Write-Info "Installation cancelled"
            exit 0
        }
    }
    
    New-Item -ItemType Directory -Path $AppDir -Force | Out-Null
    New-Item -ItemType Directory -Path "$AppDir\logs" -Force | Out-Null
    New-Item -ItemType Directory -Path "$AppDir\backups" -Force | Out-Null
    
    Write-Success "Directories created"
}

function Step3-CopyFiles {
    Write-Header "Step 3: Copying Application Files"
    
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    
    Write-Info "Copying files from $scriptDir to $AppDir..."
    
    # Copy all files except venv and __pycache__
    Get-ChildItem -Path $scriptDir -Exclude venv,__pycache__,*.db | Copy-Item -Destination $AppDir -Recurse -Force
    
    Write-Success "Files copied"
}

function Step4-SetupVirtualEnvironment {
    Write-Header "Step 4: Setting Up Virtual Environment"
    
    Write-Info "Creating virtual environment..."
    python -m venv "$AppDir\venv"
    
    Write-Info "Activating virtual environment..."
    & "$AppDir\venv\Scripts\Activate.ps1"
    
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    Write-Info "Installing dependencies..."
    pip install -r "$AppDir\requirements.txt"
    
    Write-Success "Virtual environment setup complete"
}

function Step5-Configure {
    Write-Header "Step 5: Configuration"
    
    if (-not (Test-Path "$AppDir\config.json")) {
        if (Test-Path "$AppDir\config.json.example") {
            Copy-Item "$AppDir\config.json.example" "$AppDir\config.json"
            Write-Warning "Created config.json from example"
            Write-Warning "IMPORTANT: Edit $AppDir\config.json with your settings!"
        } else {
            Write-Error "No config.json.example found"
            exit 1
        }
    } else {
        Write-Info "config.json already exists"
    }
    
    Write-Success "Configuration complete"
}

function Step6-InstallNSSM {
    Write-Header "Step 6: Installing NSSM (Service Manager)"
    
    $nssmPath = "C:\nssm"
    $nssmUrl = "https://nssm.cc/release/nssm-$NSSMVersion.zip"
    $zipPath = "$env:TEMP\nssm.zip"
    
    if (Test-Path "$nssmPath\win64\nssm.exe") {
        Write-Info "NSSM already installed"
        return
    }
    
    Write-Info "Downloading NSSM..."
    Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath
    
    Write-Info "Extracting NSSM..."
    Expand-Archive -Path $zipPath -DestinationPath "C:\" -Force
    Rename-Item "C:\nssm-$NSSMVersion" $nssmPath -Force
    
    Remove-Item $zipPath
    
    Write-Success "NSSM installed"
}

function Step7-CreateService {
    Write-Header "Step 7: Creating Windows Service"
    
    $nssmExe = "C:\nssm\win64\nssm.exe"
    
    # Check if service exists
    $service = Get-Service -Name $AppName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Warning "Service $AppName already exists"
        & $nssmExe stop $AppName
        & $nssmExe remove $AppName confirm
    }
    
    Write-Info "Installing service..."
    & $nssmExe install $AppName "$AppDir\venv\Scripts\python.exe" "$AppDir\app.py"
    
    Write-Info "Configuring service..."
    & $nssmExe set $AppName AppDirectory $AppDir
    & $nssmExe set $AppName DisplayName "Rogue Detection System"
    & $nssmExe set $AppName Description "Network security monitoring and rogue device detection"
    & $nssmExe set $AppName Start SERVICE_AUTO_START
    & $nssmExe set $AppName AppStdout "$AppDir\logs\stdout.log"
    & $nssmExe set $AppName AppStderr "$AppDir\logs\stderr.log"
    & $nssmExe set $AppName AppRotateFiles 1
    & $nssmExe set $AppName AppRotateBytes 1048576
    
    Write-Success "Service created"
}

function Step8-ConfigureFirewall {
    Write-Header "Step 8: Configuring Windows Firewall"
    
    Write-Info "Adding firewall rules..."
    
    # Remove existing rules
    Remove-NetFirewallRule -DisplayName "Rogue Detection - Web" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "Rogue Detection - HTTP" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "Rogue Detection - HTTPS" -ErrorAction SilentlyContinue
    
    # Add new rules
    New-NetFirewallRule -DisplayName "Rogue Detection - Web" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow | Out-Null
    New-NetFirewallRule -DisplayName "Rogue Detection - HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow | Out-Null
    New-NetFirewallRule -DisplayName "Rogue Detection - HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow | Out-Null
    
    Write-Success "Firewall configured"
}

function Step9-SetupBackup {
    Write-Header "Step 9: Setting Up Automated Backup"
    
    # Create backup script
    $backupScript = @'
$Date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BackupDir = "C:\RogueDetection\backups\$Date"
$RetentionDays = 30

New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

# Backup database
if (Test-Path "C:\RogueDetection\rogue_monitor.db") {
    Copy-Item "C:\RogueDetection\rogue_monitor.db" "$BackupDir\rogue_monitor.db"
}

# Backup configuration
if (Test-Path "C:\RogueDetection\config.json") {
    Copy-Item "C:\RogueDetection\config.json" "$BackupDir\config.json"
}

# Create archive
Compress-Archive -Path $BackupDir -DestinationPath "$BackupDir.zip"
Remove-Item -Path $BackupDir -Recurse

# Delete old backups
Get-ChildItem "C:\RogueDetection\backups" -Filter "*.zip" | 
    Where-Object {$_.CreationTime -lt (Get-Date).AddDays(-$RetentionDays)} | 
    Remove-Item

Write-Output "Backup completed: $Date.zip"
'@
    
    $backupScript | Out-File "$AppDir\backup.ps1" -Encoding UTF8
    
    # Create scheduled task
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File $AppDir\backup.ps1"
    $trigger = New-ScheduledTaskTrigger -Daily -At 2am
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    Unregister-ScheduledTask -TaskName "RogueDetection-Backup" -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName "RogueDetection-Backup" -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
    
    Write-Success "Automated backup configured (daily at 2 AM)"
}

function Step10-StartService {
    Write-Header "Step 10: Starting Service"
    
    Write-Info "Starting service..."
    Start-Service -Name $AppName
    
    Start-Sleep -Seconds 3
    
    $service = Get-Service -Name $AppName
    if ($service.Status -eq "Running") {
        Write-Success "Service started successfully"
    } else {
        Write-Error "Service failed to start"
        Write-Info "Check logs at: $AppDir\logs\stderr.log"
        exit 1
    }
}

function Step11-Verify {
    Write-Header "Step 11: Verification"
    
    # Check service status
    $service = Get-Service -Name $AppName
    if ($service.Status -eq "Running") {
        Write-Success "Service is running"
    } else {
        Write-Error "Service is not running"
    }
    
    # Check if port is listening
    Start-Sleep -Seconds 2
    $listening = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
    if ($listening) {
        Write-Success "Application is listening on port 5000"
    } else {
        Write-Warning "Port 5000 is not listening"
    }
    
    # Test web interface
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Web interface is responding"
        }
    } catch {
        Write-Warning "Web interface is not responding yet (may need more time to start)"
    }
}

# ============================================================================
# Main Installation
# ============================================================================

function Main {
    Clear-Host
    Write-Header "Rogue Detection System - Windows Deployment"
    Write-Info "This script will install and configure the Rogue Detection System"
    Write-Warning "This script must be run as Administrator"
    Write-Host ""
    
    $continue = Read-Host "Do you want to continue? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        Write-Info "Installation cancelled"
        exit 0
    }
    
    try {
        Step1-CheckPrerequisites
        Step2-CreateDirectory
        Step3-CopyFiles
        Step4-SetupVirtualEnvironment
        Step5-Configure
        Step6-InstallNSSM
        Step7-CreateService
        Step8-ConfigureFirewall
        Step9-SetupBackup
        Step10-StartService
        Step11-Verify
        
        Write-Header "Installation Complete!"
        Write-Host ""
        Write-Success "Rogue Detection System has been installed successfully!"
        Write-Host ""
        Write-Info "Next steps:"
        Write-Host "  1. Edit configuration: notepad $AppDir\config.json"
        Write-Host "  2. Restart service: Restart-Service -Name $AppName"
        Write-Host "  3. Check status: Get-Service -Name $AppName"
        Write-Host "  4. View logs: Get-Content $AppDir\logs\stderr.log -Tail 50"
        Write-Host "  5. Access web interface: http://localhost:5000"
        Write-Host "  6. Default login: admin / admin123"
        Write-Host ""
        Write-Warning "IMPORTANT: Change the default admin password!"
        Write-Warning "IMPORTANT: Edit $AppDir\config.json with your switch credentials!"
        Write-Host ""
        
        # Open browser
        $openBrowser = Read-Host "Do you want to open the web interface now? (Y/N)"
        if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
            Start-Process "http://localhost:5000"
        }
        
    } catch {
        Write-Error "Installation failed: $_"
        Write-Host $_.ScriptStackTrace
        exit 1
    }
}

# Run main function
Main

