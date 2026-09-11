param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path,
  [string]$CSharpImage = '',
  [string]$AriImage = ''
)

$ErrorActionPreference = 'Stop'
$seriesRoot = Join-Path $RepoRoot 'ROBLOX-BROTHERS-ADVENTURE'

if ([string]::IsNullOrWhiteSpace($CSharpImage)) {
  $CSharpImage = Join-Path $seriesRoot 'ASSETS\C-SHARP_MASTER.png'
}
if ([string]::IsNullOrWhiteSpace($AriImage)) {
  $AriImage = Join-Path $seriesRoot 'ASSETS\ARI_MASTER.png'
}

if (!(Test-Path $CSharpImage)) { throw "Missing C-SHARP master image: $CSharpImage" }
if (!(Test-Path $AriImage)) { throw "Missing ARI master image: $AriImage" }

function Get-ImagePayload([string]$Path) {
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  $b64 = [Convert]::ToBase64String($bytes)
  $sha = (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
  return [ordered]@{
    mimeType = 'image/png'
    encoding = 'base64'
    sha256 = $sha
    byteLength = $bytes.Length
    dataUri = "data:image/png;base64,$b64"
    imageBase64 = $b64
  }
}

$csharpPayload = Get-ImagePayload $CSharpImage
$ariPayload = Get-ImagePayload $AriImage

$episodes = @(
  @{ episode=1; folder='EP01-Beginner-Obby-Portal'; title='ประตูสู่ Beginner Obby' },
  @{ episode=2; folder='EP02-Minecart-Adventure'; title='รถรางเหมืองสุดป่วน' },
  @{ episode=3; folder='EP03-Sky-Islands'; title='เกาะลอยฟ้า' },
  @{ episode=4; folder='EP04-Flood-Escape'; title='เมืองน้ำท่วม' },
  @{ episode=5; folder='EP05-Puzzle-Castle'; title='ปราสาทปริศนา' },
  @{ episode=6; folder='EP06-Racing-World'; title='แข่งรถสุดป่วน' },
  @{ episode=7; folder='EP07-Animal-Rescue'; title='สวนสัตว์หลุดกรง' },
  @{ episode=8; folder='EP08-Robot-Factory'; title='โรงงานหุ่นยนต์วุ่นวาย' },
  @{ episode=9; folder='EP09-Pirate-Island'; title='โจรสลัดแห่งเกาะสมบัติ' },
  @{ episode=10; folder='EP10-Mega-Obby-Final'; title='Mega Obby Final' }
)

$older = [ordered]@{
  id = 'big_brother_csharp'
  name = 'C-SHARP'
  thaiName = 'ซีชาร์ป'
  characterReferenceId = 'RBA-CSHARP-MASTER-V4'
  identityLocked = $true
  role = 'พี่ชาย นักวางแผน กล้าลุย และคอยปกป้องน้อง'
  ageStyle = 'stylized child game avatar, older sibling proportions'
  description = 'Original stylized 3D older brother; slightly taller, rounded-square child face, warm tan skin, dark brown/black short tidy slightly-spiky hair, large brown eyes, friendly confident smile.'
  mainOutfit = 'cream hoodie, light green utility vest, tan knee-length shorts, white sneakers, simple backpack, green wristband, explorer pouch'
  immutableFields = @('face','skinTone','hair','bodyProportions','relativeHeight','outfit','shoes','backpack','wristband','voiceIdentity')
  referenceImage = $csharpPayload
}

$younger = [ordered]@{
  id = 'little_brother_ari'
  name = 'ARI'
  thaiName = 'อาริ'
  characterReferenceId = 'RBA-ARI-MASTER-V4'
  identityLocked = $true
  role = 'น้องชาย ช่างสังเกต คล่องตัว และเก่งแก้ปริศนา'
  ageStyle = 'stylized child game avatar, younger sibling proportions'
  description = 'Original stylized 3D younger brother; visibly shorter and smaller, rounder face, warm tan skin, black short fluffy-front hair, large curious eyes, bright innocent smile.'
  mainOutfit = 'white T-shirt, blue hoodie, navy shorts, blue-and-white sneakers, small blue sling pouch'
  immutableFields = @('face','skinTone','hair','bodyProportions','relativeHeight','outfit','shoes','slingPouch','voiceIdentity')
  referenceImage = $ariPayload
}

foreach ($ep in $episodes) {
  $episodeDir = Join-Path $seriesRoot $ep.folder
  if (!(Test-Path $episodeDir)) { throw "Episode folder not found: $episodeDir" }

  $step5 = [ordered]@{
    schemaVersion = '4.0'
    projectId = ('roblox-brothers-adventure-ep{0:d2}-step5' -f $ep.episode)
    seriesId = 'roblox-brothers-adventure'
    episode = $ep.episode
    episodeTitle = $ep.title
    currentStep = 5
    sharedCharacterMaster = [ordered]@{
      id = 'RBA-CHARACTER-MASTER'
      version = '4.0'
      immutable = $true
      sourcePolicy = 'The two embedded Base64 character images in this STEP5 are canonical and must be reused unchanged in every episode.'
      identityReferencePriority = @('embedded STEP5 master image','immediately previous generated scene image','scene prompt/state')
      olderBrotherAlwaysTaller = $true
      youngerBrotherAlwaysShorter = $true
      noFaceSwap = $true
      noOutfitSwap = $true
      noCharacterRedesign = $true
    }
    settings = [ordered]@{
      aspectRatio = '9:16'
      characterStyleCategory = 'stylized game avatars'
      castingMode = 'custom'
      customCastingCount = 2
      productionDesignStep = 5
    }
    movie = [ordered]@{
      characters = @($older, $younger)
      atmosphereAssets = @()
      productAssets = @()
      productionDesignAnalyzed = $true
    }
    generationContract = [ordered]@{
      scene1References = @('C-SHARP embedded master image','ARI embedded master image')
      scene2PlusReferences = @('C-SHARP embedded master image','ARI embedded master image','immediately previous generated scene image')
      rejectIfCharacterDiffersFromMaster = $true
      rejectIfHeightRelationshipChanges = $true
      rejectIfOutfitOrHairChanges = $true
      rejectIfThirdBrotherAppears = $true
    }
    updatedAt = (Get-Date).ToString('o')
  }

  $json = $step5 | ConvertTo-Json -Depth 30
  $outPath = Join-Path $episodeDir 'STEP5.json'
  [System.IO.File]::WriteAllText($outPath, $json, [System.Text.UTF8Encoding]::new($false))
  Write-Host "Wrote $outPath"
}

# Verify all 10 STEP5 files contain the exact same embedded image hashes.
$expectedC = $csharpPayload.sha256
$expectedA = $ariPayload.sha256
foreach ($ep in $episodes) {
  $p = Join-Path (Join-Path $seriesRoot $ep.folder) 'STEP5.json'
  $obj = Get-Content -Raw -Encoding UTF8 $p | ConvertFrom-Json
  if ($obj.movie.characters[0].referenceImage.sha256 -ne $expectedC) { throw "C-SHARP hash mismatch in $p" }
  if ($obj.movie.characters[1].referenceImage.sha256 -ne $expectedA) { throw "ARI hash mismatch in $p" }
}

Write-Host 'STEP5 Base64 embedding complete for EP01-EP10.'
Write-Host "C-SHARP SHA256: $expectedC"
Write-Host "ARI SHA256: $expectedA"
