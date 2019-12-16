py -m venv env
CALL env\Scripts\activate
set FLASK_APP=blog.py
python -m flask run -h 192.168.178.36
pause