grammar C;

compilationUnit:
	(functionDefinition | declaration)+? EOF
;

primaryExpression:
	Identifier
|	Constant
|	StringLiteral
|	'(' expression ')'
;

postfixExpression:
	primaryExpression
|	postfixExpression '[' expression ']'
|	postfixExpression '(' argumentExpressionList? ')'
|	postfixExpression '.' Identifier
|	postfixExpression '->' Identifier
;

argumentExpressionList:
	assignmentExpression
|	argumentExpressionList ',' assignmentExpression
;

unaryExpression:
	postfixExpression
|	unaryExpression '++'
|	unaryExpression '--'
|	'++' unaryExpression
|	'--' unaryExpression
|	('*' | '+' | '-' | '!') castExpression
;

castExpression:
	unaryExpression
|	'(' typeName ')' castExpression
;

multiplicativeExpression:
	castExpression
|	multiplicativeExpression '*' castExpression
|	multiplicativeExpression '/' castExpression
|	multiplicativeExpression '%' castExpression
;

additiveExpression:
	multiplicativeExpression
|	additiveExpression '+' multiplicativeExpression
|	additiveExpression '-' multiplicativeExpression
;

relationalExpression:
	additiveExpression
|	relationalExpression '<' additiveExpression
|	relationalExpression '>' additiveExpression
|	relationalExpression '<=' additiveExpression
|	relationalExpression '>=' additiveExpression
;

equalityExpression:
    relationalExpression
|	relationalExpression '==' additiveExpression
|	relationalExpression '!=' additiveExpression
;

logicalExpression:
	equalityExpression
|	logicalExpression '&&' relationalExpression
|	logicalExpression '||' relationalExpression
;

conditionalExpression:
	logicalExpression
|	logicalExpression '?' expression ':' conditionalExpression
;

assignmentExpression:
	conditionalExpression
|	unaryExpression ('=' | '*=' | '/=' | '%=' | '+=' | '-=') assignmentExpression
;

expression:
	assignmentExpression
|	expression ',' assignmentExpression
;

constantExpression:
	conditionalExpression
;

declaration:
	declarationSpecifiers initDeclaratorList? ';'
;

declarationSpecifiers:
	typeSpecifier declarationSpecifiers?
;

initDeclaratorList:
	initDeclarator
|	initDeclaratorList ',' initDeclarator
;

initDeclarator:
	declarator
|	declarator '=' initializer
;

typeSpecifier:
	Int
|	Void
|	Double
|	Float
|	Char
;

specifierQualifierList:
	typeSpecifier specifierQualifierList?
;

declarator:
	pointer? directDeclarator
;

directDeclarator:
	Identifier
|	'(' declarator ')'
|	directDeclarator '[' assignmentExpression? ']'
|	directDeclarator '(' parameterTypeList? ')'
// |	direct_declarator '(' identifier_list? ')' // What is this?
;

pointer:
	'*' pointer?
;

parameterTypeList:
	parameterList
|	parameterList ',' '...'
;

parameterList:
	parameterDeclaration
|	parameterList ',' parameterDeclaration
;

parameterDeclaration:
	declarationSpecifiers declarator
|	declarationSpecifiers
;

identifierList:
	Identifier
|	identifierList ',' Identifier
;

typeName:
	specifierQualifierList
;

initializer:
	assignmentExpression
|	'{' initializerList '}'
|	'{' initializerList ',}'
;

initializerList:
	initializer
|	initializerList ',' initializer
;

statement:
	labeledStatement
|	compoundStatement
|	expressionStatement
|	selectionStatement
|	iterationStatement
|	jumpStatement
;

labeledStatement:
	Identifier ':' statement
|	Case constantExpression ':' statement
|	Default ':' statement
;

compoundStatement:
	'{' blockItemList? '}'
;

blockItemList:
	blockItem
|	blockItemList blockItem
;

blockItem:
	declaration
|	statement
;

expressionStatement:
	expression? ';'
;

selectionStatement:
	If '(' expression ')' statement
|	If '(' expression ')' statement Else statement
|	Switch '(' expression ')' statement
;

iterationStatement:
	While '(' expression ')' statement
|	For '(' expression? ';' expression? ';' expression? ')' statement
|	For '(' declaration expression? ';' expression? ')' statement
;

jumpStatement:
	Goto Identifier ';'
|	Continue ';'
|	Break ';'
|	Return expression? ';'
;

functionDefinition:
	declarationSpecifiers declarator declarationList? compoundStatement
;

declarationList:
	declaration
|	declarationList declaration
;

// Types
Char: 'char';
Int: 'int';
Double: 'double';
Float: 'float';
Void: 'void';
// Struct: 'struct'; can be added later

// Control flow
If: 'if';
Else: 'else';
For: 'for';
Goto: 'goto';
While: 'while';
Switch: 'switch';

// Jumps
Break: 'break';
Default: 'default';
Continue: 'continue';
Return: 'return';

// Label
Case: 'case';

// Generic fragments
fragment NonDigit: [_a-zA-Z];
fragment Digit: [0-9];
fragment NonZeroDigit: [1-9];
fragment Sign: '+' | '-';
fragment ExponentPart: ('e'|'E') Sign? Digit+;
fragment EscapeSequence:
	'\\\'' | '\\"' | '\\?' | '\\\\' | '\\a' | '\\b' | '\\f' | '\\n' | '\\r' | '\\t' | '\\v'
;

Identifier:
	NonDigit (NonDigit | Digit)*
;

fragment CChar:
	~('\'' | '\n' | '\\')
|	EscapeSequence
;
fragment ConstantInt: Sign? Digit+;
fragment ConstantFloat:
	Digit* '.' Digit+ ExponentPart?
|	Digit+ '.' ExponentPart?;
fragment ConstantChar: '\'' CChar '\'';

Constant:
	ConstantInt
|	ConstantFloat
|	ConstantChar
;

fragment SChar:
	~('"' | '\n' | '\\')
|	EscapeSequence
;

StringLiteral:
	'"' SChar*? '"'
;

BlockComment: '/*' .*? '*/' -> skip;

LineComment: '//' ~[\r\n]* -> skip;

WS: [ \n\r\t] -> skip;
EOS: ';' ;
