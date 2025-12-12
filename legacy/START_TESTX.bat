@echo off
REM Start OpenCode autonomous agent for testx project
REM Using FREE OpenCode big-pickle model

echo ======================================================================
echo   Starting OpenCode Autonomous Agent
echo ======================================================================
echo.
echo Project: testx
echo Model: opencode/big-pickle (FREE)
echo.
echo This window will show the agent's progress in real-time.
echo.
echo TIPS:
echo - Watch for [Tool: ...] messages showing agent activity
echo - Initial setup takes 10-20+ minutes (creating feature_list.json)
echo - Press Ctrl+C to stop the agent
echo.
echo To monitor progress from another window, run:
echo   python check_progress.py testx
echo.
echo ======================================================================
echo.

python autonomous_agent_demo.py --project-dir testx --model opencode/big-pickle

echo.
echo ======================================================================
echo Agent stopped.
echo ======================================================================
pause
