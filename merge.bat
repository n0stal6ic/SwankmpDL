@echo off
setlocal enabledelayedexpansion
title Decrypt and Merge
echo ========================================
echo  Paste decryption keys (KID:KEY)
echo  Then press Ctrl+Z and Enter
echo ========================================
set "KEYFILE=keys.txt"
> "%KEYFILE%" (
    more
)
echo.
echo Keys saved to %KEYFILE%
echo.
set "KEYARGS="
for /f "usebackq tokens=*" %%A in ("%KEYFILE%") do (
    if not "%%A"=="" (
        set "KEYARGS=!KEYARGS! --key %%A"
    )
)
if exist "video.mp4" (
    echo Decrypting video...
    mp4decrypt %KEYARGS% video.mp4 video_decrypted.mp4
) else (
    echo video.mp4 not found.
)
if exist "audio.mp4" (
    echo Decrypting audio...
    mp4decrypt %KEYARGS% audio.mp4 audio_decrypted.mp4
) else (
    echo audio.mp4 not found.
)
echo Merging files...
if exist "subtitles.vtt" (
    ffmpeg -i video_decrypted.mp4 -i audio_decrypted.mp4 -i subtitles.vtt -c copy output.mkv
) else if exist "*.vtt" (
    for %%f in (*.vtt) do (
        echo Found subtitle: %%f
        ffmpeg -i video_decrypted.mp4 -i audio_decrypted.mp4 -i "%%f" -c copy output.mkv
        goto mergedone
    )
) else (
    ffmpeg -i video_decrypted.mp4 -i audio_decrypted.mp4 -c copy output.mkv
)
:mergedone
cls
echo Done!
timeout 10 >nul
exit