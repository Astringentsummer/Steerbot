# Automated Ubuntu 22.04 + ROS 2 Humble Installation
# Run this in PowerShell as Administrator

Write-Host "=========================================="
Write-Host "Ubuntu 22.04 + ROS 2 Humble Setup"
Write-Host "=========================================="
Write-Host ""

# Step 1: Download Ubuntu 22.04
Write-Host "Step 1: Downloading Ubuntu 22.04 image..."
$downloadUrl = "https://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-cloudimg-amd64-wsl.rootfs.tar.gz"
$downloadPath = "$env:USERPROFILE\Downloads\ubuntu-22.04.tar.gz"

if (Test-Path $downloadPath) {
    Write-Host "[OK] Ubuntu 22.04 image already downloaded"
} else {
    Write-Host "Downloading... (this may take 5-10 minutes)"
    Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath
    Write-Host "[OK] Download complete"
}

# Step 2: Create installation directory
Write-Host ""
Write-Host "Step 2: Creating installation directory..."
$installDir = "C:\WSL\Ubuntu-22.04-Humble"
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
    Write-Host "[OK] Directory created: $installDir"
} else {
    Write-Host "[OK] Directory already exists"
}

# Step 3: Import Ubuntu 22.04
Write-Host ""
Write-Host "Step 3: Importing Ubuntu 22.04 into WSL..."
wsl --import Ubuntu-22.04-Humble $installDir $downloadPath
Write-Host "[OK] Ubuntu 22.04 imported"

# Step 4: Set up user
Write-Host ""
Write-Host "Step 4: Setting up user account..."
Write-Host "You will be prompted to create a password for user 'rohit'"
Write-Host ""

wsl -d Ubuntu-22.04-Humble bash -c @"
useradd -m -s /bin/bash rohit
usermod -aG sudo rohit
echo 'Please enter password for user rohit:'
passwd rohit
"@

# Step 5: Configure default user
Write-Host ""
Write-Host "Step 5: Configuring default user..."
$wslConf = @"
[user]
default=rohit
"@
$wslConf | Out-File -FilePath "$installDir\rootfs\etc\wsl.conf" -Encoding ASCII
Write-Host "[OK] Default user configured"

# Step 6: Restart WSL
Write-Host ""
Write-Host "Step 6: Restarting WSL..."
wsl --terminate Ubuntu-22.04-Humble
Start-Sleep -Seconds 2
Write-Host "[OK] WSL restarted"

# Step 7: Verify installation
Write-Host ""
Write-Host "Step 7: Verifying Ubuntu version..."
wsl -d Ubuntu-22.04-Humble lsb_release -a

# Step 8: Run ROS 2 Humble setup
Write-Host ""
Write-Host "=========================================="
Write-Host "Ubuntu 22.04 Installation Complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Next step: Install ROS 2 Humble"
Write-Host ""
Write-Host "Run this command:"
Write-Host "wsl -d Ubuntu-22.04-Humble bash /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper/setup_wsl_humble.sh"
Write-Host ""
