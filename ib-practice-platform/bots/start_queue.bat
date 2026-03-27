@echo off
setlocal
cd /d %~dp0\..
python bots\queue.py seed --target 80000
python bots\queue.py worker --poll 2
