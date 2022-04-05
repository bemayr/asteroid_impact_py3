@echo off
set /p id="Proband:innen ID: "
python .\game.py --script-json .\experiment.json --display-mode fullscreen --subject-number %id% --log-filename .\logs\%id%.csv --log-overwrite false
