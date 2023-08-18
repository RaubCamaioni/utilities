# Display all network interfaces
$networkInterfaces = Get-NetAdapter | Where-Object { $_.PhysicalMediaType -ne 'Wireless' }

Write-Host "Available Network Interfaces:"
foreach ($interface in $networkInterfaces) {
    Write-Host "  [$($interface.InterfaceIndex)] $($interface.Name)"
}
Write-Host

# Prompt for interface selection
$interfaceIndex = Read-Host "Enter the interface index for which you want to set a static IP address"

# Validate input
$selectedInterface = $networkInterfaces | Where-Object { $_.InterfaceIndex -eq $interfaceIndex }
if (!$selectedInterface) {
    Write-Host "Invalid interface index. Please run the script again."
    exit
}

# Prompt for IP address and subnet mask
$ipAddress = Read-Host "Enter the new IPv4 address"
$subnetMask = Read-Host "Enter the subnet mask"
$defaultGateway = Read-Host "Enter the default gateway"

# Set the interface to static IP using Netsh
$interfaceAlias = $selectedInterface.Name

$netshCommand = "netsh interface ipv4 set address name='$interfaceAlias' static $ipAddress $subnetMask"
if (![string]::IsNullOrWhiteSpace($defaultGateway)) {
    $netshCommand += " $defaultGateway 1"
}
Invoke-Expression $netshCommand

Write-Host "Static IP address, subnet mask, and default gateway set successfully for $($selectedInterface.Name)."