antlr:
	java -jar antlr-4.7.2-complete.jar C.g4 -Dlanguage=Python3 -visitor -o parser/

ast-dot:
	venv/bin/python main.py example-C-code/simple.c > ast.dot && dot -Tpng -o ast.png ast.dot

stt-dot:
	venv/bin/python main.py example-C-code/simple.c > stt.dot && dot -Tpng -o stt.png stt.dot
