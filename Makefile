

server: | env
	. env/bin/activate && pip install --requirement requirements.txt && python app.py

env: 
	virtualenv env
