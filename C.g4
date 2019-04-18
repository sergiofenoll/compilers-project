grammar C;

compilationUnit:
	(functionDefinition | declaration)+? EOF
;

primaryExpression:
	Identifier #identifier
|	Constant #constant
|	StringLiteral #stringLiteral
|	'(' expression ')' #parenExpression
;

postfixExpression:
	primaryExpression #postfixPassthrough
|	postfixExpression '[' expression ']' #arrayAccess
|	postfixExpression '(' assignmentExpression? (',' assignmentExpression)* ')' #functionCall
// |	postfixExpression '.' Identifier
// |	postfixExpression '->' Identifier
;

// argumentExpressionList:
//	assignmentExpression
//|	argumentExpressionList ',' assignmentExpression
//;

unaryExpression:
	postfixExpression #unaryPassthrough
|	unaryExpression '++' #postfixIncrement
|	unaryExpression '--' #postfixDecrement
|	'++' unaryExpression #prefixIncrement
|	'--' unaryExpression #prefixDecrement
|	'*' castExpression #indirection
|   '+' castExpression #unaryPlus
|   '-' castExpression #unaryMinus
|   '!' castExpression #logicalNot
;

castExpression:
	unaryExpression #castPassthrough
|	'(' typeName ')' castExpression #cast
;

multiplicativeExpression:
	castExpression #multiplicativePassthrough
|	multiplicativeExpression '*' castExpression #multiplication
|	multiplicativeExpression '/' castExpression #division
|	multiplicativeExpression '%' castExpression #modulo
;

additiveExpression:
	multiplicativeExpression #additivePassthrough
|	additiveExpression '+' multiplicativeExpression #addition
|	additiveExpression '-' multiplicativeExpression #subtraction
;

relationalExpression:
	additiveExpression #relationalPassthrough
|	relationalExpression '<' additiveExpression #smallerThan
|	relationalExpression '>' additiveExpression #largerThan
|	relationalExpression '<=' additiveExpression #smallerThanOrEqual
|	relationalExpression '>=' additiveExpression #largerThanOrEqual
;

equalityExpression:
    relationalExpression #equalityPassthrough
|	relationalExpression '==' additiveExpression #equals
|	relationalExpression '!=' additiveExpression #notEquals
;

logicalExpression:
	equalityExpression #logicalPassthrough
|	logicalExpression '&&' relationalExpression #logicalAnd
|	logicalExpression '||' relationalExpression #logicalOr
;

conditionalExpression:
	logicalExpression #conditionalPassthrough
|	logicalExpression '?' expression ':' conditionalExpression #conditional
;

assignmentExpression:
	conditionalExpression #assignmentPassthrough
|	unaryExpression ('=' | '*=' | '/=' | '%=' | '+=' | '-=') assignmentExpression #assignment
;

expression:
	assignmentExpression #expressionPassthrough
|	expression ',' assignmentExpression #expressionList
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
// |	directDeclarator '(' identifierList? ')' // What is this?
;

pointer:
	'*' pointer?
;

parameterTypeList:
	parameterList
|	parameterList ',' '...'
;

parameterList:
	parameterDeclaration (',' parameterDeclaration)*
;

parameterDeclaration:
	declarationSpecifiers declarator
|	declarationSpecifiers
;

// Rule is used by spec in directDeclarator, but we're not sure what it's actually for
// Left out until its use can be determined
//identifierList:
//	Identifier
//|	identifierList ',' Identifier
//;

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
//|	Case constantExpression ':' statement
//|	Default ':' statement
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
//|	Switch '(' expression ')' statement
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
