@echo off
REM Lesson Generator Starter for IvyStudy
REM Usage: start_lesson_generator.bat [--queue] [--generate N] [--all] [--subject NAME] [--status]

cd /d "%~dp0\ib-practice-platform"
python lesson_generator.py %*
pause
