<#
.SYNOPSIS
  Resize, re-encode and strip metadata from photos, then drop them into the
  right gallery folder.

.DESCRIPTION
  Phone photos are typically 3-8 MB and carry EXIF metadata including GPS
  coordinates. Publishing one unmodified is slow AND can leak a home
  address. This resizes to a sane web size and re-encodes, which discards
  EXIF as a side effect.

  Uses System.Drawing, which ships with Windows. Nothing to install.

.EXAMPLE
  # one file
  .\tools\optimize-images.ps1 -Source "$env:USERPROFILE\Downloads\IMG_1941.JPG" -Gallery frida

.EXAMPLE
  # a whole folder, in one go
  .\tools\optimize-images.ps1 -Source "$env:USERPROFILE\Downloads\album" -Gallery frida

.NOTES
  Afterwards run:  python tools/build-gallery.py
#>
[CmdletBinding()]
param(
    # File or folder to read from. Originals are never modified.
    [Parameter(Mandatory)][string]$Source,

    # Gallery name - becomes public/assets/images/<Gallery>/
    [Parameter(Mandatory)]
    [ValidateSet('frida','reptiles','garden','family','motorcycle','tesla','military','physique')]
    [string]$Gallery,

    # Longest edge in pixels. 1600 is plenty for a web gallery.
    [int]$MaxEdge = 1600,

    # JPEG quality, 1-100. 82 is visually clean at this size.
    [int]$Quality = 82,

    # Prefix for output names, e.g. -Prefix 01 gives 01-<name>.jpg
    [string]$Prefix = ''
)

Add-Type -AssemblyName System.Drawing

$repo = Split-Path $PSScriptRoot -Parent
$dest = Join-Path $repo "public\assets\images\$Gallery"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$files = if (Test-Path $Source -PathType Container) {
    Get-ChildItem $Source -File | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png|heic|webp)$' }
} else {
    Get-Item $Source
}

if (-not $files) { Write-Warning "No images found at $Source"; return }

# JPEG encoder, so Quality can actually be set.
$codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
         Where-Object { $_.MimeType -eq 'image/jpeg' }
$params = New-Object System.Drawing.Imaging.EncoderParameters(1)
$params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
    [System.Drawing.Imaging.Encoder]::Quality, [long]$Quality)

$n = 0
foreach ($file in $files) {
    try {
        $img = [System.Drawing.Image]::FromFile($file.FullName)
    } catch {
        Write-Warning "Skipped (unreadable, HEIC is not supported): $($file.Name)"
        continue
    }

    # Scale down only. Never upscale a small original.
    $scale = [Math]::Min(1.0, $MaxEdge / [Math]::Max($img.Width, $img.Height))
    $w = [int][Math]::Round($img.Width * $scale)
    $h = [int][Math]::Round($img.Height * $scale)

    $canvas = New-Object System.Drawing.Bitmap($w, $h)
    $g = [System.Drawing.Graphics]::FromImage($canvas)
    $g.InterpolationMode  = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.PixelOffsetMode    = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.SmoothingMode      = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.DrawImage($img, 0, 0, $w, $h)
    $g.Dispose()

    $base = [IO.Path]::GetFileNameWithoutExtension($file.Name).ToLower() -replace '[^a-z0-9]+','-'
    $base = $base.Trim('-')
    if ($Prefix) { $base = "$Prefix-$base" }
    $out = Join-Path $dest "$base.jpg"

    $canvas.Save($out, $codec, $params)
    $canvas.Dispose()
    $img.Dispose()

    $before = [math]::Round($file.Length / 1KB)
    $after  = [math]::Round((Get-Item $out).Length / 1KB)
    "{0,-28} {1}x{2}  {3} KB -> {4} KB" -f $base, $w, $h, $before, $after
    $n++
}

""
"$n image(s) written to public/assets/images/$Gallery/"
"EXIF (including any GPS coordinates) discarded by re-encoding."
"Next:  python tools/build-gallery.py"
