# Zipper + LocalName

| Asset | Description |
|-------|-------------|
| `Zipper.apk` | Android ZIP extractor + addon injector |
| `LocalName.mcaddon` | Bedrock addon extension |
| `LocalName.exe` | Windows control center |
|

## Release workflow

Push a tag to trigger APK + addon build:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions builds everything and publishes to Releases.

## Local dev

```powershell
# Decode addon source (hidden from git)
.\decode_addon.ps1

# Build addon .mcaddon
python addon/build_addon.py

# Build Windows EXE (control center)
.\app\build.ps1

# Build Android APK (requires Android SDK)
cd android
.\gradlew assembleRelease

# Encode addon for commit
.\encode_addon.ps1
```

## Site

Drop `site/` folder into Netlify for the landing page.
Edit `netlify.toml` to set your GitHub repo URL.
