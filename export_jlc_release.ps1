[CmdletBinding()]
param(
    [Parameter()]
    [string]$OutputDirectory,

    [Parameter()]
    [switch]$IncludeHoldBoards,

    [Parameter()]
    [string]$KiCadCli
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-KiCadCli {
    param([string]$RequestedPath)

    $candidates = @()
    if ($RequestedPath) {
        $candidates += $RequestedPath
    }
    $candidates += 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'

    $fromPath = Get-Command 'kicad-cli.exe' -ErrorAction SilentlyContinue
    if ($fromPath) {
        $candidates += $fromPath.Source
    }

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            $resolved = (Resolve-Path -LiteralPath $candidate).Path
            $version = (& $resolved --version 2>&1 | Out-String).Trim()
            if ($LASTEXITCODE -ne 0) {
                continue
            }
            if ($version -notmatch '(^|\s)10\.') {
                throw "KiCad 10 CLI is required; found '$version' at '$resolved'."
            }
            return [pscustomobject]@{
                Path = $resolved
                Version = $version
            }
        }
    }

    throw 'KiCad 10 kicad-cli.exe was not found. Pass -KiCadCli with its full path.'
}

function Invoke-KiCad {
    param(
        [Parameter(Mandatory)]
        [string]$Executable,

        [Parameter(Mandatory)]
        [string[]]$ArgumentList,

        [Parameter(Mandatory)]
        [string]$Description
    )

    Write-Host "  $Description"
    & $Executable @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE."
    }
}

function Get-SourceHashes {
    param([string[]]$Paths)

    $result = @{}
    foreach ($path in $Paths) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $fullPath = (Resolve-Path -LiteralPath $path).Path
            $result[$fullPath] = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash
        }
    }
    return $result
}

function Assert-SourceHashesUnchanged {
    param([hashtable]$Before)

    foreach ($entry in $Before.GetEnumerator()) {
        if (-not (Test-Path -LiteralPath $entry.Key -PathType Leaf)) {
            throw "Live source file disappeared during export: $($entry.Key)"
        }
        $after = (Get-FileHash -LiteralPath $entry.Key -Algorithm SHA256).Hash
        if ($after -ne $entry.Value) {
            throw "Live source file changed during export: $($entry.Key)"
        }
    }
}

function Get-RelativePathForManifest {
    param(
        [string]$BasePath,
        [string]$FilePath
    )

    return [IO.Path]::GetRelativePath($BasePath, $FilePath).Replace('\', '/')
}

$repositoryRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$kicad = Resolve-KiCadCli -RequestedPath $KiCadCli

if (-not $OutputDirectory) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $OutputDirectory = Join-Path $repositoryRoot "release_jlc\$stamp"
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)

if (Test-Path -LiteralPath $OutputDirectory) {
    $existing = @(Get-ChildItem -LiteralPath $OutputDirectory -Force)
    if ($existing.Count -gt 0) {
        throw "Output directory already exists and is not empty: $OutputDirectory"
    }
} else {
    New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
}

$boards = @(
    [pscustomobject]@{
        Name = 'balun_eth_rj45'
        ProjectDirectory = 'balun_eth_rj45'
        BoardFile = 'balun_eth_rj45.kicad_pcb'
        SchematicFile = 'balun_eth_rj45.kicad_sch'
        Status = 'RELEASE_CANDIDATE'
        Hold = $false
    },
    [pscustomobject]@{
        Name = 'balun_slipring_molex'
        ProjectDirectory = 'balun_slipring\molex_end'
        BoardFile = 'balun_slipring_molex.kicad_pcb'
        SchematicFile = 'balun_slipring_molex.kicad_sch'
        Status = 'HOLD_DO_NOT_ORDER'
        Hold = $true
    },
    [pscustomobject]@{
        Name = 'balun_slipring_m12'
        ProjectDirectory = 'balun_slipring\m12_end'
        BoardFile = 'balun_slipring_m12.kicad_pcb'
        SchematicFile = 'balun_slipring_m12.kicad_sch'
        Status = 'HOLD_DO_NOT_ORDER'
        Hold = $true
    }
)

$liveSourcePaths = @()
foreach ($board in $boards) {
    $sourceProject = Join-Path $repositoryRoot $board.ProjectDirectory
    $baseName = [IO.Path]::GetFileNameWithoutExtension($board.BoardFile)
    $liveSourcePaths += Join-Path $sourceProject $board.BoardFile
    $liveSourcePaths += Join-Path $sourceProject $board.SchematicFile
    $liveSourcePaths += Join-Path $sourceProject "$baseName.kicad_pro"
    $liveSourcePaths += Join-Path $sourceProject "$baseName.kicad_dru"
}
$sourceHashesBefore = Get-SourceHashes -Paths $liveSourcePaths

$tempBase = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$stageRoot = Join-Path $tempBase ("balun-jlc-release-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stageRoot | Out-Null

$results = @()
$generatedAt = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss K')

try {
    Write-Host "KiCad CLI: $($kicad.Path)"
    Write-Host "KiCad version: $($kicad.Version)"
    Write-Host "Release output: $OutputDirectory"
    if (-not $IncludeHoldBoards) {
        Write-Warning 'Slip-ring boards are HOLD. They will be validated, but no Gerber ZIP will be created without -IncludeHoldBoards.'
    }

    foreach ($board in $boards) {
        Write-Host ''
        Write-Host "[$($board.Name)] $($board.Status)"

        $sourceProject = Join-Path $repositoryRoot $board.ProjectDirectory
        if (-not (Test-Path -LiteralPath $sourceProject -PathType Container)) {
            throw "Project directory not found: $sourceProject"
        }

        $boardStageRoot = Join-Path $stageRoot $board.Name
        $stageRepository = Join-Path $boardStageRoot 'repository'
        $stageProject = Join-Path $stageRepository $board.ProjectDirectory
        New-Item -ItemType Directory -Path (Split-Path -Parent $stageProject) -Force | Out-Null
        Copy-Item -LiteralPath $sourceProject -Destination $stageProject -Recurse

        if ($board.Hold) {
            $commonFootprints = Join-Path $repositoryRoot 'balun_slipring\common.pretty'
            $stageCommonParent = Join-Path $stageRepository 'balun_slipring'
            New-Item -ItemType Directory -Path $stageCommonParent -Force | Out-Null
            Copy-Item -LiteralPath $commonFootprints -Destination (Join-Path $stageCommonParent 'common.pretty') -Recurse
        }

        $stagePcb = Join-Path $stageProject $board.BoardFile
        $stageSch = Join-Path $stageProject $board.SchematicFile
        if (-not (Test-Path -LiteralPath $stagePcb -PathType Leaf)) {
            throw "Staged PCB not found: $stagePcb"
        }
        if (-not (Test-Path -LiteralPath $stageSch -PathType Leaf)) {
            throw "Staged schematic not found: $stageSch"
        }

        $boardOutput = Join-Path $OutputDirectory $board.Name
        $reportsOutput = Join-Path $boardOutput 'reports'
        New-Item -ItemType Directory -Path $reportsOutput -Force | Out-Null

        $drcReport = Join-Path $reportsOutput "$($board.Name)-drc.rpt"
        $ercReport = Join-Path $reportsOutput "$($board.Name)-erc.rpt"

        Invoke-KiCad -Executable $kicad.Path -Description 'Refill staged zones, save staged PCB, run DRC and schematic parity' -ArgumentList @(
            'pcb', 'drc',
            '--refill-zones', '--save-board', '--schematic-parity',
            '--severity-error', '--severity-warning', '--exit-code-violations',
            '--units', 'mm',
            '-o', $drcReport,
            $stagePcb
        )

        Invoke-KiCad -Executable $kicad.Path -Description 'Run ERC on staged schematic' -ArgumentList @(
            'sch', 'erc',
            '--severity-error', '--severity-warning', '--exit-code-violations',
            '--units', 'mm',
            '-o', $ercReport,
            $stageSch
        )

        $willExport = (-not $board.Hold) -or $IncludeHoldBoards
        $zipPath = $null
        $bomPath = $null
        $positionPath = $null

        if ($willExport) {
            $fabricationOutput = Join-Path $boardOutput 'fabrication'
            $assemblyOutput = Join-Path $boardOutput 'assembly'
            New-Item -ItemType Directory -Path $fabricationOutput -Force | Out-Null
            New-Item -ItemType Directory -Path $assemblyOutput -Force | Out-Null

            Invoke-KiCad -Executable $kicad.Path -Description 'Export RS-274X Gerbers with zone checking' -ArgumentList @(
                'pcb', 'export', 'gerbers',
                '--layers', 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts',
                '--no-x2', '--no-netlist', '--subtract-soldermask', '--check-zones',
                '--precision', '6',
                '-o', $fabricationOutput,
                $stagePcb
            )

            $drillReport = Join-Path $reportsOutput "$($board.Name)-drill.rpt"
            Invoke-KiCad -Executable $kicad.Path -Description 'Export separate PTH/NPTH Excellon drills and Gerber drill maps' -ArgumentList @(
                'pcb', 'export', 'drill',
                '--format', 'excellon',
                '--drill-origin', 'absolute',
                '--excellon-units', 'mm',
                '--excellon-zeros-format', 'decimal',
                '--excellon-oval-format', 'route',
                '--excellon-separate-th',
                '--generate-map', '--map-format', 'gerberx2',
                '--generate-report', '--report-path', $drillReport,
                '-o', $fabricationOutput,
                $stagePcb
            )

            $ipc356Path = Join-Path $fabricationOutput "$($board.Name).d356"
            Invoke-KiCad -Executable $kicad.Path -Description 'Export IPC-D-356 electrical netlist' -ArgumentList @(
                'pcb', 'export', 'ipcd356',
                '-o', $ipc356Path,
                $stagePcb
            )

            $positionPath = Join-Path $assemblyOutput "$($board.Name)-positions.csv"
            $rawPositionPath = Join-Path $reportsOutput "$($board.Name)-kicad-positions.csv"
            Invoke-KiCad -Executable $kicad.Path -Description 'Export DNP-excluded KiCad component position CSV' -ArgumentList @(
                'pcb', 'export', 'pos',
                '--format', 'csv', '--units', 'mm', '--side', 'both', '--exclude-dnp',
                '-o', $rawPositionPath,
                $stagePcb
            )

            $jlcPositions = Import-Csv -LiteralPath $rawPositionPath | ForEach-Object {
                $layer = switch ($_.Side.ToLowerInvariant()) {
                    'top' { 'Top' }
                    'bottom' { 'Bottom' }
                    default { throw "Unexpected KiCad placement side '$($_.Side)' for $($_.Ref)." }
                }
                [pscustomobject][ordered]@{
                    Designator = $_.Ref
                    'Mid X' = $_.PosX
                    'Mid Y' = $_.PosY
                    Rotation = $_.Rot
                    Layer = $layer
                }
            }
            $jlcPositions | Export-Csv -LiteralPath $positionPath -NoTypeInformation -Encoding utf8

            $bomPath = Join-Path $assemblyOutput "$($board.Name)-bom.csv"
            Invoke-KiCad -Executable $kicad.Path -Description 'Export DNP-excluded JLCPCB assembly BOM' -ArgumentList @(
                'sch', 'export', 'bom',
                '--exclude-dnp',
                '--fields', 'Value,Reference,Footprint,LCSC Part #',
                '--labels', 'Comment,Designator,Footprint,LCSC Part #',
                '--group-by', 'Value,Footprint,LCSC Part #',
                '--sort-field', 'Reference',
                '-o', $bomPath,
                $stageSch
            )

            $zipLabel = if ($board.Hold) { "$($board.Name)-HOLD_DO_NOT_ORDER-JLCPCB_GERBER.zip" } else { "$($board.Name)-JLCPCB_GERBER.zip" }
            $zipPath = Join-Path $boardOutput $zipLabel
            $fabricationFiles = @(Get-ChildItem -LiteralPath $fabricationOutput -File)
            if ($fabricationFiles.Count -eq 0) {
                throw "No fabrication files were generated for $($board.Name)."
            }
            Compress-Archive -Path (Join-Path $fabricationOutput '*') -DestinationPath $zipPath -CompressionLevel Optimal
        } else {
            $holdNotice = @(
                'HOLD_DO_NOT_ORDER',
                '',
                'Validation reports were generated, but fabrication files and ZIP were intentionally not exported.',
                'Resolve the connector, pin-map, mechanical, and impedance release blockers first.',
                'Run export_jlc_release.ps1 -IncludeHoldBoards only for engineering review output; that switch does not release this board for ordering.'
            )
            Set-Content -LiteralPath (Join-Path $boardOutput 'HOLD_DO_NOT_ORDER.txt') -Value $holdNotice -Encoding utf8
        }

        $boardReadme = @(
            "Project: $($board.Name)",
            "Status: $($board.Status)",
            "Generated: $generatedAt",
            "KiCad: $($kicad.Version)",
            '',
            'The PCB was copied to an isolated staging directory. Zone refill/save, DRC, schematic parity, and ERC were run only on that staged copy.',
            'The live KiCad source was not modified.',
            '',
            'ASSEMBLY WARNING:',
            'A project-specific, DNP-excluded JLCPCB-format BOM and CPL are generated for review.',
            'Before PCBA ordering, manually verify every LCSC number, FIT/DNP state, side, rotation, and placement against the JLCPCB preview.',
            'Do not upload the repository-wide combined BOM as a project BOM.',
            '',
            $(if ($board.Hold) { 'HOLD: This slip-ring endpoint remains DO NOT ORDER even when engineering Gerbers were explicitly exported.' } else { 'RELEASE CANDIDATE: JLC stack-up, controlled-impedance solver result, Gerber CAM, BOM/CPL, and placement must still be approved before payment.' })
        )
        Set-Content -LiteralPath (Join-Path $boardOutput 'README.txt') -Value $boardReadme -Encoding utf8

        $results += [pscustomobject]@{
            Project = $board.Name
            Status = $board.Status
            Validated = $true
            FabricationZip = if ($zipPath) { Get-RelativePathForManifest -BasePath $OutputDirectory -FilePath $zipPath } else { 'NOT_CREATED' }
            AssemblyBom = if ($bomPath) { Get-RelativePathForManifest -BasePath $OutputDirectory -FilePath $bomPath } else { 'NOT_CREATED' }
            PositionCsv = if ($positionPath) { Get-RelativePathForManifest -BasePath $OutputDirectory -FilePath $positionPath } else { 'NOT_CREATED' }
        }
    }

    Assert-SourceHashesUnchanged -Before $sourceHashesBefore

    $summaryLines = @(
        'BALUN JLCPCB RELEASE EXPORT',
        "Generated: $generatedAt",
        "KiCad: $($kicad.Version)",
        '',
        'IMPORTANT:',
        '- balun_eth_rj45 is a RELEASE CANDIDATE, not an automatic approval to order.',
        '- Both slip-ring endpoint boards are HOLD / DO NOT ORDER.',
        '- A HOLD Gerber ZIP, if explicitly generated, is for engineering review only.',
        '- The generated project BOM/CPL exclude DNP parts but still require manual JLC part, side, rotation, and placement approval.',
        '- Verify DNP population, JLC placement preview, stack-up, and current impedance-solver result before payment.',
        '',
        'PROJECT RESULTS:'
    )
    foreach ($result in $results) {
        $summaryLines += "- $($result.Project): $($result.Status); ZIP=$($result.FabricationZip); BOM=$($result.AssemblyBom); CPL=$($result.PositionCsv)"
    }
    Set-Content -LiteralPath (Join-Path $OutputDirectory 'RELEASE_README.txt') -Value $summaryLines -Encoding utf8

    $manifestPath = Join-Path $OutputDirectory 'SHA256SUMS.txt'
    $manifestLines = @(
        "# SHA256 manifest generated $generatedAt",
        "# KiCad $($kicad.Version)"
    )
    $manifestFiles = Get-ChildItem -LiteralPath $OutputDirectory -Recurse -File |
        Where-Object { $_.FullName -ne $manifestPath } |
        Sort-Object FullName
    foreach ($file in $manifestFiles) {
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        $relative = Get-RelativePathForManifest -BasePath $OutputDirectory -FilePath $file.FullName
        $manifestLines += "$hash  $relative"
    }
    Set-Content -LiteralPath $manifestPath -Value $manifestLines -Encoding ascii

    Assert-SourceHashesUnchanged -Before $sourceHashesBefore

    Write-Host ''
    Write-Host 'Release export completed.'
    $results | Format-Table -AutoSize
    Write-Host "SHA256 manifest: $manifestPath"
} finally {
    if (Test-Path -LiteralPath $stageRoot) {
        $resolvedStage = [IO.Path]::GetFullPath($stageRoot)
        $stageLeaf = Split-Path -Leaf $resolvedStage
        $isInsideTemp = $resolvedStage.StartsWith($tempBase, [StringComparison]::OrdinalIgnoreCase)
        if ($isInsideTemp -and $stageLeaf.StartsWith('balun-jlc-release-', [StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolvedStage -Recurse -Force
        } else {
            Write-Warning "Temporary staging directory was not removed because its path failed the safety check: $resolvedStage"
        }
    }
}
