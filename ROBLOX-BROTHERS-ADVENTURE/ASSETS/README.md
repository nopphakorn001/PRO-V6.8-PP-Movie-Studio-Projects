# Character Master Assets

Place the two approved master character-sheet PNG files here before building STEP5 Base64 files:

- `C-SHARP_MASTER.png`
- `ARI_MASTER.png`

These exact two PNGs are the canonical visual identity source for every episode.

Then run from the repository root in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\ROBLOX-BROTHERS-ADVENTURE\tools\BUILD_STEP5_BASE64.ps1
```

The script will create/replace `STEP5.json` inside EP01–EP10 and embed the same two PNGs in every file as Base64, including SHA-256 verification.

Do not regenerate different character images per episode. If either canonical image changes, rerun the builder so every episode receives the same updated Base64 and hashes.
