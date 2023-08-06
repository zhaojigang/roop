@echo off
echo 'activate face-roop start...'
call D:\anaconda\anaconda3\Scripts\activate.bat face-roop
echo 'activate face-roop end...'

D:
cd D:\project\roop

echo 'roop starting...'
python run.py --execution-provider cuda --frame-processor face_swapper face_enhancer
echo 'roop start success...'

pause
