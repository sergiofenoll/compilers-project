grammar c;

program:
	(statement | declaration | external_declaration)*
;

primary_expression:
	IDENTIFIER
|	CONSTANT
|	STRING_LITERAL
|	'(' expression ')'
;

postfix_expression:
	primary_expression
|	postfix_expression '[' expression ']'
|	postfix_expression '(' argument_expression_list? ')'
|	postfix_expression '.' IDENTIFIER
|	postfix_expression '->' IDENTIFIER
|	postfix_expression '++'
|	postfix_expression '--'
;

unary_expression:
	postfix_expression
|	'++' unary_expression
|	'--' unary_expression
|	unary_operator cast_expression
;

unary_operator:
	'*'
|	'+'
|	'-'
|	'!'
;

cast_expression:
	unary_expression
|	'(' type_name ')' cast_expression
;

multiplicative_expression:
	cast_expression
|	multiplicative_expression '*' cast_expression
|	multiplicative_expression '/' cast_expression
|	multiplicative_expression '%' cast_expression
;

additive_expression:
	multiplicative_expression
|	additive_expression '+' multiplicative_expression
|	additive_expression '-' multiplicative_expression
;

// Not required by project spec, ommitted
shift_expression:
	additive_expression
;

relational_expression:
	shift_expression
|	relational_expression '<' shift_expression
|	relational_expression '>' shift_expression
|	relational_expression '<=' shift_expression
|	relational_expression '>=' shift_expression
;

equality_expression:
	relational_expression
|	equality_expression '==' relational_expression
|	equality_expression '!=' relational_expression
;

logical_AND_expression:
	equality_expression
|	logical_AND_expression '&&' equality_expression
;

logical_OR_expression:
	logical_AND_expression
|	logical_OR_expression '||' logical_AND_expression
;

// Ommitted (for now)
conditional_expression:
	logical_OR_expression
|	logical_OR_expression '?' expression ':' conditional_expression
;

assignment_expression:
	conditional_expression
|	unary_expression ASSIGNMENT_OPERATOR assignment_expression
;

argument_expression_list:
	assignment_expression
|	argument_expression_list ',' assignment_expression
;

expression:
	assignment_expression
|	expression ',' assignment_expression
;

constant_expression:
	conditional_expression
;

declaration:
	declaration_specifiers init_declarator_list? ';'
;

declaration_specifiers:
	type_specifier declaration_specifiers?
;

init_declarator_list:
	init_declarator
|	init_declarator_list ',' init_declarator
;

init_declarator:
	declarator
|	declarator '=' initializer
;

type_specifier:
	KEYWORD_INT
|	KEYWORD_VOID
|	KEYWORD_DOUBLE
|	KEYWORD_FLOAT
|	KEYWORD_CHAR
;

specifier_qualifier_list:
	type_specifier specifier_qualifier_list?
;

declarator:
	pointer? direct_declarator
;

direct_declarator:
	IDENTIFIER
|	'(' declarator ')'
|	direct_declarator '[' assignment_expression? ']'
|	direct_declarator '[' '*' ']'
|	direct_declarator '(' parameter_type_list ')'
|	direct_declarator '(' identifier_list? ')'
;

pointer:
	'*' pointer
;

parameter_type_list:
	parameter_list
|	parameter_list ',' '...'
;

parameter_list:
	parameter_declaration
|	parameter_list ',' parameter_declaration
;

parameter_declaration:
	declaration_specifiers declarator
|	declaration_specifiers
;

identifier_list:
	IDENTIFIER
|	identifier_list ',' IDENTIFIER
;

type_name:
	specifier_qualifier_list
;

initializer:
	assignment_expression
|	'{' initializer_list '}'
|	'{' initializer_list ',}'
;

initializer_list:
	designation? initializer
|	initializer_list ',' designation? initializer
;

designation:
	designator_list '='
;

designator_list:
	designator
|	designator_list designator
;

designator:
	'[' constant_expression ']'
|	'.' IDENTIFIER
;

statement:
	labeled_statement
|	compound_statement
|	expression_statement
|	selection_statement
|	iteration_statement
|	jump_statement
;

labeled_statement:
	IDENTIFIER ':' statement
|	KEYWORD_CASE constant_expression ':' statement
|	KEYWORD_DEFAULT ':' statement
;

compound_statement:
	'{' block_item_list? '}'
;

block_item_list:
	block_item
|	block_item_list block_item
;

block_item:
	declaration
|	statement
;

expression_statement:
	expression? ';'
;

selection_statement:
	KEYWORD_IF '(' expression ')' statement
|	KEYWORD_IF '(' expression ')' statement KEYWORD_ELSE statement
|	KEYWORD_SWITCH '(' expression ')' statement
;

iteration_statement:
	KEYWORD_WHILE '(' expression ')' statement
|	KEYWORD_FOR '(' expression? ';' expression? ';' expression? ')' statement
|	KEYWORD_FOR '(' declaration expression? ';' expression? ')' statement
;

jump_statement:
	KEYWORD_GOTO IDENTIFIER ';'
|	KEYWORD_CONTINUE ';'
|	KEYWORD_BREAK ';'
|	KEYWORD_RETURN expression? ';'
;

external_declaration:
	function_definition
|	declaration
;

function_definition:
	declaration_specifiers declarator declaration_list? compound_statement
;

declaration_list:
	declaration
|	declaration_list declaration
;


fragment NONDIGIT: [_a-zA-Z];
fragment DIGIT: [0-9];
fragment NONZERODIGIT: [1-9];
fragment SIGN: '+' | '-';
fragment EXPONENT_PART: ('e'|'E') SIGN? DIGIT+;
fragment CONSTANT_INTEGER: SIGN? DIGIT+;
fragment CONSTANT_FLOAT:
	DIGIT* '.' DIGIT+ EXPONENT_PART?
|	DIGIT+ '.' EXPONENT_PART?;
fragment CONSTANT_CHARACTER: '\'' C_CHAR '\'';
fragment ESCAPE_SEQUENCE:
	'\\\'' | '\\"' | '\\?' | '\\\\' | '\\a' | '\\b' | '\\f' | '\\n' | '\\r' | '\\t' | '\\v'
;
fragment C_CHAR:
	~('\'' | '\n' | '\\')
|	ESCAPE_SEQUENCE
;
fragment S_CHAR:
	~('"' | '\n' | '\\')
|	ESCAPE_SEQUENCE
;

ASSIGNMENT_OPERATOR: '=' | '*=' | '/=' | '%=' | '+=' | '-=';

IDENTIFIER:
	NONDIGIT (NONDIGIT | DIGIT)*
;

CONSTANT:
	CONSTANT_INTEGER
|	CONSTANT_FLOAT
|	CONSTANT_CHARACTER
;

STRING_LITERAL:
	'"' S_CHAR*? '"'
;

KEYWORD_BREAK: 'break';
KEYWORD_CASE: 'case';
KEYWORD_CHAR: 'char';
KEYWORD_CONTINUE: 'continue';
KEYWORD_DEFAULT: 'default';
KEYWORD_DOUBLE: 'double';
KEYWORD_ELSE: 'else';
KEYWORD_FLOAT: 'float';
KEYWORD_FOR: 'for';
KEYWORD_GOTO: 'goto';
KEYWORD_IF: 'if';
KEYWORD_INT: 'int';
KEYWORD_RETURN: 'return';
KEYWORD_STRUCT: 'struct';
KEYWORD_SWITCH: 'switch';
KEYWORD_VOID: 'void';
KEYWORD_WHILE: 'while';

WS: [ \n\r\t] -> skip;
EOS: ';' ;
