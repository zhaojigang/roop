@echo off
echo 'activate face-roop start...'
call D:\anaconda\anaconda3\Scripts\activate.bat face-roop
echo 'activate face-roop end...'

D:
cd D:\project\roop

echo 'roop starting...'
:: python run.py --execution-provider cuda --frame-processor face_swapper face_enhancer  --similar-face-distance 1.5
python run.py --execution-provider cuda --frame-processor face_swapper --similar-face-distance 1.5

pause
