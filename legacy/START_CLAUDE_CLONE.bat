@echo off
REM Start OpenCode autonomous agent for Claude Clone project
REM Using FREE OpenCode big-pickle model in SEPARATE directory

echo ======================================================================
echo   Starting OpenCode Autonomous Agent - Claude Clone
echo ======================================================================
echo.
echo Project: C:\Users\t.wilms\Documents\claude_clone_testx
echo Model: opencode/big-pickle (FREE)
echo.
echo This is a SEPARATE directory outside the Git repo
echo to avoid conflicts with the main project.
echo.
echo TIPS:
echo - Watch for [Tool: ...] messages showing agent activity
echo - Initial setup takes 10-20+ minutes (creating feature_list.json)
echo - Press Ctrl+C to stop the agent
echo.
echo To monitor progress from another window, run:
echo   python check_progress.py C:\Users\t.wilms\Documents\claude_clone_testx
echo.
echo ======================================================================
echo.

cd C:\Users\t.wilms\Documents\opencode_harness_autonomous_coding
python autonomous_agent_demo.py --project-dir C:\Users\t.wilms\Documents\claude_clone_testx --model opencode/big-pickle

echo.
echo ======================================================================
echo Agent stopped.
echo ======================================================================
pause
