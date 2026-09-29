[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$VMName = 'openEulerDev',
    [string]$VhdxPath = 'C:\Users\daryl\OneDrive\Documents\euler_dev.vhdx',
    [string]$StorageRoot = 'E:\Hyper-V',
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

function Show-Plan {
    param([object]$Vm)
    Write-Host "VM: $($Vm.Name) [$($Vm.State)] Generation $($Vm.Generation)"
    Write-Host "Storage destination: $StorageRoot\$VMName"
    Write-Host "Processors: $ProcessorCount"
    Write-Host "Memory: $([math]::Round($MemoryStartupBytes / 1GB, 1)) GB"
    Write-Host "Network switch: $SwitchName"
    Write-Host "Nested virtualization: enabled"
    Write-Host "Secure Boot: disabled"
}

Require-Administrator

if (-not (Get-Command Get-VM -ErrorAction SilentlyContinue)) {
    throw 'Hyper-V PowerShell module is unavailable.'
}

$vm = Get-VM -Name $VMName -ErrorAction SilentlyContinue
if (-not $vm) {
    if (-not (Test-Path -LiteralPath $VhdxPath)) {
        throw "VHDX not found: $VhdxPath"
    }
    $parent = Split-Path -Parent $StorageRoot
    if (-not (Test-Path -LiteralPath $parent)) {
        throw "Storage volume/path is unavailable: $parent"
    }
    Write-Host "No VM named '$VMName' exists. A new VM would be created from: $VhdxPath"
    if (-not $Apply) {
        Write-Host 'Dry run only. Re-run with -Apply to create the VM.'
        exit 0
    }
    New-Item -ItemType Directory -Path $StorageRoot -Force | Out-Null
    New-VM -Name $VMName -Generation 2 -MemoryStartupBytes $MemoryStartupBytes -VHDPath $VhdxPath -Path (Join-Path $StorageRoot $VMName) | Out-Null
    $vm = Get-VM -Name $VMName
}

Show-Plan $vm

if (-not $Apply) {
    Write-Host 'Dry run only. No VM changes were made. Re-run with -Apply to configure the VM.' -ForegroundColor Yellow
    exit 0
}

if ($vm.State -ne 'Off') {
    throw "VM must be Off before configuration. Current state: $($vm.State)"
}

if (-not (Get-VMSwitch -Name $SwitchName -ErrorAction SilentlyContinue)) {
    throw "Hyper-V switch not found: $SwitchName"
}

$targetStorage = Join-Path $StorageRoot $VMName
New-Item -ItemType Directory -Path $StorageRoot -Force | Out-Null

Set-VMProcessor -VMName $VMName -Count $ProcessorCount -ExposeVirtualizationExtensions $true
Set-VMMemory -VMName $VMName -StartupBytes $MemoryStartupBytes
Set-VMFirmware -VMName $VMName -EnableSecureBoot Off
Connect-VMNetworkAdapter -VMName $VMName -SwitchName $SwitchName

$currentPath = (Get-VM -Name $VMName).Path
if ($currentPath -ne $targetStorage) {
    Write-Host "Moving VM storage to $targetStorage..."
    Move-VMStorage -VMName $VMName -DestinationStoragePath $targetStorage
}

Write-Host 'Final VM configuration:'
Get-VM -Name $VMName | Select-Object Name, State, Generation, Path, ProcessorCount, MemoryStartup | Format-List
Get-VMProcessor -VMName $VMName | Select-Object Count, ExposeVirtualizationExtensions | Format-List
Get-VMNetworkAdapter -VMName $VMName | Select-Object SwitchName, Status | Format-List
