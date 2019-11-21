py -m venv env
CALL env\Scripts\activate
set FLASK_APP=app.py
python -m flask run