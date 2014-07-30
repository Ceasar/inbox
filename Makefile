

server: | env
	. env/bin/activate && pip install --requirement requirements.txt && python app.py

env: 
	virtualenv env


test:
	. env/bin/activate && py.test test_imaplib2.py
