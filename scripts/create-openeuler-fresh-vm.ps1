[CmdletBinding()]
param(
    [string]$VMName = 'openEulerLocalDev',
    [string]$VhdxPath = 'C:\Users\daryl\source\local-dev\openeuler-dev.vhdx',
    [string]$StorageRoot = 'C:\Users\daryl\source\local-dev\Hyper-V',
    [Parameter(Mandatory = $true)]
    [string]$IsoPath,
    [string]$SwitchName = 'Default Switch',
    [int]$ProcessorCount = 4,
    [UInt64]$MemoryStartupBytes = 8GB,
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]$identity
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Run this script from an elevated PowerShell window.'
    }
}

Require-Administrator

if (-not (Test-Path -LiteralPath $VhdxPath)) {
    throw "Target VHDX not found: $VhdxPath"
}
if (-not (Test-Path -LiteralPath $IsoPath)) {
    throw "openEuler ISO not found: $IsoPath"
}
if (-not (Get-VMSwitch -Name $SwitchName -ErrorAction SilentlyContinue)) {
    throw "Hyper-V switch not found: $SwitchName"
}

$existing = Get-VM -Name $VMName -ErrorAction SilentlyContinue
if ($existing) {
    throw "VM already exists: $VMName"
}

Write-Host "Fresh openEuler VM plan:"
Write-Host "  Name:       $VMName"
Write-Host "  VHDX:       $VhdxPath"
Write-Host "  VM path:    $StorageRoot\$VMName"
Write-Host "  ISO:        $IsoPath"
Write-Host "  CPU/RAM:    $ProcessorCount CPU / $([math]::Round($MemoryStartupBytes / 1GB, 1)) GB"
Write-Host "  Network:    $SwitchName"
Write-Host "  SecureBoot: disabled"

if (-not $Apply) {
    Write-Host 'Dry run only. Re-run with -Apply to create the VM.' -ForegroundColor Yellow
    exit 0
}

$attached = Get-VHD -Path $VhdxPath | Select-Object -ExpandProperty Attached
if ($attached) {
    Write-Host "Dismounting target VHDX from the host..."
    Dismount-VHD -Path $VhdxPath
}

New-Item -ItemType Directory -Path $StorageRoot -Force | Out-Null
New-VM -Name $VMName -Generation 2 -MemoryStartupBytes $MemoryStartupBytes -Path (Join-Path $StorageRoot $VMName) -VHDPath $VhdxPath | Out-Null

Set-VMProcessor -VMName $VMName -Count $ProcessorCount -ExposeVirtualizationExtensions $true
Set-VMFirmware -VMName $VMName -EnableSecureBoot Off
Connect-VMNetworkAdapter -VMName $VMName -SwitchName $SwitchName

$dvd = Add-VMDvdDrive -VMName $VMName -Path $IsoPath -Passthru
Set-VMFirmware -VMName $VMName -FirstBootDevice $dvd

Write-Host 'Fresh VM created. Start it and install openEuler from the attached ISO:'
Write-Host "  Start-VM -Name '$VMName'"
Write-Host "  vmconnect.exe localhost '$VMName'"
Get-VM -Name $VMName | Select-Object Name,State,Generation,Path,ProcessorCount,MemoryStartup | Format-List
Get-VMFirmware -VMName $VMName | Select-Object SecureBoot,FirstBootDevice | Format-List
