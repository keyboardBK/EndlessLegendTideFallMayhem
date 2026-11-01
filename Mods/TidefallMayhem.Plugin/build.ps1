param([string]$OutputPath)
$ErrorActionPreference = 'Stop'
$gameRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$managed = Join-Path $gameRoot 'Endless Legend 2_Data\Managed'
$core = Join-Path $gameRoot 'BepInEx\core'
$output = Join-Path $gameRoot 'BepInEx\plugins\TidefallMayhem\TidefallMayhem.dll'
if ($OutputPath) { $output = $OutputPath }
$sdk = (& dotnet --list-sdks | Select-Object -Last 1)
if ($sdk -notmatch '^(\S+)\s+\[(.+)\]$') { throw '.NET SDK is required to rebuild this plugin.' }
$compiler = Join-Path (Join-Path $Matches[2] $Matches[1]) 'Roslyn\bincore\csc.dll'
$refs = @('netstandard.dll','mscorlib.dll','System.dll','System.Core.dll','UnityEngine.dll','UnityEngine.CoreModule.dll','Amplitude.dll','Amplitude.Framework.dll','Amplitude.Core.dll','Amplitude.Mercury.Firstpass.dll') | ForEach-Object { '/reference:' + (Join-Path $managed $_) }
$refs += @('BepInEx.dll','0Harmony.dll') | ForEach-Object { '/reference:' + (Join-Path $core $_) }
& dotnet $compiler /nologo /target:library /langversion:latest /nostdlib+ /optimize+ ('/out:' + $output) $refs (Join-Path $PSScriptRoot 'Plugin.cs') (Join-Path $PSScriptRoot 'StackCounter.cs') (Join-Path $PSScriptRoot 'AugmentCatalog.cs') (Join-Path $PSScriptRoot 'TieredDrafts.cs')
if ($LASTEXITCODE -ne 0) { throw 'Plugin compilation failed.' }
Write-Host "Built $output"
