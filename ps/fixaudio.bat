
@echo off

:: Сет переменную для сохранения имени файла
for %%i in (%*) do set "filename=%%~ni"

:: Выполняем ffmpeg с соответствующими оп션ами
ffmpeg -hwaccel cuda -i %1 -af "equalizer=f=100:t=q:w=200,compand=attacks=5:decAYS=400:soft-knee=5:gain=-6,loudnorm=I=-16:TP=-1.5:LRA=11,afftdn=nf=-25" -vf "scale=1920:1080" -c:v libx264 -crf 1 -c:a aac -map 0 %filename.avi