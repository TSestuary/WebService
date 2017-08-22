pyinstaller:
	pyinstaller -F main.py

test:
	./dist/main

clean:
	rm -rf build/ main.spec dist/

python:
	python main.py

clean2:
	rm *.pyc 

