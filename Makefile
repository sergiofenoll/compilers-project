antlr:
	java -jar antlr-4.7.2-complete.jar C.g4 -Dlanguage=Python3 -o parser/

ast-dot:
	dot -Tpng -o ast.png ast.dot

stt-dot:
	dot -Tpng -o stt.png stt.dot
