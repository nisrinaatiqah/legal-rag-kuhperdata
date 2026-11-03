@echo off
echo ========================================================
echo  Menjalankan Backend FastAPI: CiviLex AI
echo  Sistem Legal Question Answering Hukum Perdata & HIR
echo  Port: http://localhost:8000
echo ========================================================
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
pause
