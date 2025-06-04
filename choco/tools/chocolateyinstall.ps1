# IMPORTANT: Before releasing this package, copy/paste the next 2 lines into PowerShell to remove all comments from this file:
#   $f='c:\path\to\thisFile.ps1'
#   gc $f | ? {$_ -notmatch "^\s*#"} | % {$_ -replace '(^.*?)\s*?[^``]#.*','$1'} | Out-File $f+".~" -en utf8; mv -fo $f+".~" $f

# 1. See the _TODO.md that is generated top level and read through that
# 2. Follow the documentation below to learn how to create a package for the package type you are creating.
# 3. In Chocolatey scripts, ALWAYS use absolute paths - $toolsDir gets you to the package's tools directory.
$ErrorActionPreference = 'Stop' # stop on all errors
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

# Internal packages (organizations) or software that has redistribution rights (community repo)
$fileLocation = Join-Path $toolsDir 'pieces.exe'

$packageArgs = @{
  packageName   = $env:ChocolateyPackageName
  unzipLocation = $toolsDir
  fileType      = 'exe'
  file          = $fileLocation
  softwareName  = 'pieces-cli*'
}

# Install the package
Install-ChocolateyInstallPackage @packageArgs

# Add the tools directory to PATH
Install-ChocolateyPath $toolsDir 'Machine'

## Main helper functions - these have error handling tucked into them already
## see https://docs.chocolatey.org/en-us/create/functions

## Install an application, will assert administrative rights
## - https://docs.chocolatey.org/en-us/create/functions/install-chocolateypackage
## - https://docs.chocolatey.org/en-us/create/functions/install-chocolateyinstallpackage
## add additional optional arguments as necessary
##Install-ChocolateyPackage $packageName $fileType $silentArgs $url [$url64 -validExitCodes $validExitCodes -checksum $checksum -checksumType $checksumType -checksum64 $checksum64 -checksumType64 $checksumType64]

## Download and unpack a zip file - https://docs.chocolatey.org/en-us/create/functions/install-chocolateyzippackage
##Install-ChocolateyZipPackage $packageName $url $toolsDir [$url64 -checksum $checksum -checksumType $checksumType -checksum64 $checksum64 -checksumType64 $checksumType64]

## Install Visual Studio Package - https://docs.chocolatey.org/en-us/create/functions/install-chocolateyvsixpackage
#Install-ChocolateyVsixPackage $packageName $url [$vsVersion] [-checksum $checksum -checksumType $checksumType]
#Install-ChocolateyVsixPackage @packageArgs

## see the full list at https://docs.chocolatey.org/en-us/create/functions

## downloader that the main helpers use to download items
## if removing $url64, please remove from here
## - https://docs.chocolatey.org/en-us/create/functions/get-chocolateywebfile
#Get-ChocolateyWebFile $packageName 'DOWNLOAD_TO_FILE_FULL_PATH' $url $url64

## Installer, will assert administrative rights - used by Install-ChocolateyPackage
## use this for embedding installers in the package when not going to community feed or when you have distribution rights
## - https://docs.chocolatey.org/en-us/create/functions/install-chocolateyinstallpackage
#Install-ChocolateyInstallPackage $packageName $fileType $silentArgs '_FULLFILEPATH_' -validExitCodes $validExitCodes

## Unzips a file to the specified location - auto overwrites existing content
## - https://docs.chocolatey.org/en-us/create/functions/get-chocolateyunzip
#Get-ChocolateyUnzip "FULL_LOCATION_TO_ZIP.zip" $toolsDir

## Runs processes asserting UAC, will assert administrative rights - used by Install-ChocolateyInstallPackage
## - https://docs.chocolatey.org/en-us/create/functions/start-chocolateyprocessasadmin
#Start-ChocolateyProcessAsAdmin 'STATEMENTS_TO_RUN' 'Optional_Application_If_Not_PowerShell' -validExitCodes $validExitCodes

## To avoid quoting issues, you can also assemble your -Statements in another variable and pass it in
#$appPath = "$env:ProgramFiles\appname"
##Will resolve to C:\Program Files\appname
#$statementsToRun = "/C `"$appPath\bin\installservice.bat`""
#Start-ChocolateyProcessAsAdmin $statementsToRun cmd -validExitCodes $validExitCodes

## add specific folders to the path - any executables found in the chocolatey package
## folder will already be on the path. This is used in addition to that or for cases
## when a native installer doesn't add things to the path.
## - https://docs.chocolatey.org/en-us/create/functions/install-chocolateypath
#Install-ChocolateyPath 'LOCATION_TO_ADD_TO_PATH' 'User_OR_Machine' # Machine will assert administrative rights

## Add specific files as shortcuts to the desktop
## - https://docs.chocolatey.org/en-us/create/functions/install-chocolateyshortcut
#$target = Join-Path $toolsDir "$($packageName).exe"
# Install-ChocolateyShortcut -shortcutFilePath "<path>" -targetPath "<path>" [-workingDirectory "C:\" -arguments "C:\test.txt" -iconLocation "C:\test.ico" -description "This is the description"]

## Outputs the bitness of the OS (either "32" or "64")
## - https://docs.chocolatey.org/en-us/create/functions/get-osarchitecturewidth
#$osBitness = Get-ProcessorBits

## Set persistent Environment variables
## - https://docs.chocolatey.org/en-us/create/functions/install-chocolateyenvironmentvariable
#Install-ChocolateyEnvironmentVariable -variableName "SOMEVAR" -variableValue "value" [-variableType = 'Machine' #Defaults to 'User']

## Set up a file association
## - https://docs.chocolatey.org/en-us/create/functions/install-chocolateyfileassociation
#Install-ChocolateyFileAssociation

## Adding a shim when not automatically found - Chocolatey automatically shims exe files found in package directory.
## - https://docs.chocolatey.org/en-us/create/functions/install-binfile
## - https://docs.chocolatey.org/en-us/create/create-packages#how-do-i-exclude-executables-from-getting-shims
#Install-BinFile

##PORTABLE EXAMPLE
#$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
# despite the name "Install-ChocolateyZipPackage" this also works with 7z archives
#Install-ChocolateyZipPackage $packageName $url $toolsDir $url64
## END PORTABLE EXAMPLE
