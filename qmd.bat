@echo off
REM QMD Wrapper for Windows
REM Usage: qmd.bat <command> [options]

set QMD_PATH=C:\Users\Start\.openclaw\startmitworkspace\qmd-cli
set NODE_OPTIONS=--no-warnings

cd /d %QMD_PATH%
npx tsx src/cli/qmd.ts %*
