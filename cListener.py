# Generated from c.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .cParser import cParser
else:
    from cParser import cParser

# This class defines a complete listener for a parse tree produced by cParser.
class cListener(ParseTreeListener):

    # Enter a parse tree produced by cParser#program.
    def enterProgram(self, ctx:cParser.ProgramContext):
        print("entered program")
        pass

    # Exit a parse tree produced by cParser#program.
    def exitProgram(self, ctx:cParser.ProgramContext):
        pass


    # Enter a parse tree produced by cParser#primary_expression.
    def enterPrimary_expression(self, ctx:cParser.Primary_expressionContext):
        pass

    # Exit a parse tree produced by cParser#primary_expression.
    def exitPrimary_expression(self, ctx:cParser.Primary_expressionContext):
        pass


    # Enter a parse tree produced by cParser#postfix_expression.
    def enterPostfix_expression(self, ctx:cParser.Postfix_expressionContext):
        pass

    # Exit a parse tree produced by cParser#postfix_expression.
    def exitPostfix_expression(self, ctx:cParser.Postfix_expressionContext):
        pass


    # Enter a parse tree produced by cParser#unary_expression.
    def enterUnary_expression(self, ctx:cParser.Unary_expressionContext):
        pass

    # Exit a parse tree produced by cParser#unary_expression.
    def exitUnary_expression(self, ctx:cParser.Unary_expressionContext):
        pass


    # Enter a parse tree produced by cParser#unary_operator.
    def enterUnary_operator(self, ctx:cParser.Unary_operatorContext):
        pass

    # Exit a parse tree produced by cParser#unary_operator.
    def exitUnary_operator(self, ctx:cParser.Unary_operatorContext):
        pass


    # Enter a parse tree produced by cParser#cast_expression.
    def enterCast_expression(self, ctx:cParser.Cast_expressionContext):
        pass

    # Exit a parse tree produced by cParser#cast_expression.
    def exitCast_expression(self, ctx:cParser.Cast_expressionContext):
        pass


    # Enter a parse tree produced by cParser#multiplicative_expression.
    def enterMultiplicative_expression(self, ctx:cParser.Multiplicative_expressionContext):
        pass

    # Exit a parse tree produced by cParser#multiplicative_expression.
    def exitMultiplicative_expression(self, ctx:cParser.Multiplicative_expressionContext):
        pass


    # Enter a parse tree produced by cParser#additive_expression.
    def enterAdditive_expression(self, ctx:cParser.Additive_expressionContext):
        pass

    # Exit a parse tree produced by cParser#additive_expression.
    def exitAdditive_expression(self, ctx:cParser.Additive_expressionContext):
        pass


    # Enter a parse tree produced by cParser#shift_expression.
    def enterShift_expression(self, ctx:cParser.Shift_expressionContext):
        pass

    # Exit a parse tree produced by cParser#shift_expression.
    def exitShift_expression(self, ctx:cParser.Shift_expressionContext):
        pass


    # Enter a parse tree produced by cParser#relational_expression.
    def enterRelational_expression(self, ctx:cParser.Relational_expressionContext):
        pass

    # Exit a parse tree produced by cParser#relational_expression.
    def exitRelational_expression(self, ctx:cParser.Relational_expressionContext):
        pass


    # Enter a parse tree produced by cParser#equality_expression.
    def enterEquality_expression(self, ctx:cParser.Equality_expressionContext):
        pass

    # Exit a parse tree produced by cParser#equality_expression.
    def exitEquality_expression(self, ctx:cParser.Equality_expressionContext):
        pass


    # Enter a parse tree produced by cParser#logical_AND_expression.
    def enterLogical_AND_expression(self, ctx:cParser.Logical_AND_expressionContext):
        pass

    # Exit a parse tree produced by cParser#logical_AND_expression.
    def exitLogical_AND_expression(self, ctx:cParser.Logical_AND_expressionContext):
        pass


    # Enter a parse tree produced by cParser#logical_OR_expression.
    def enterLogical_OR_expression(self, ctx:cParser.Logical_OR_expressionContext):
        pass

    # Exit a parse tree produced by cParser#logical_OR_expression.
    def exitLogical_OR_expression(self, ctx:cParser.Logical_OR_expressionContext):
        pass


    # Enter a parse tree produced by cParser#conditional_expression.
    def enterConditional_expression(self, ctx:cParser.Conditional_expressionContext):
        pass

    # Exit a parse tree produced by cParser#conditional_expression.
    def exitConditional_expression(self, ctx:cParser.Conditional_expressionContext):
        pass


    # Enter a parse tree produced by cParser#assignment_expression.
    def enterAssignment_expression(self, ctx:cParser.Assignment_expressionContext):
        pass

    # Exit a parse tree produced by cParser#assignment_expression.
    def exitAssignment_expression(self, ctx:cParser.Assignment_expressionContext):
        pass


    # Enter a parse tree produced by cParser#argument_expression_list.
    def enterArgument_expression_list(self, ctx:cParser.Argument_expression_listContext):
        pass

    # Exit a parse tree produced by cParser#argument_expression_list.
    def exitArgument_expression_list(self, ctx:cParser.Argument_expression_listContext):
        pass


    # Enter a parse tree produced by cParser#expression.
    def enterExpression(self, ctx:cParser.ExpressionContext):
        pass

    # Exit a parse tree produced by cParser#expression.
    def exitExpression(self, ctx:cParser.ExpressionContext):
        pass


    # Enter a parse tree produced by cParser#constant_expression.
    def enterConstant_expression(self, ctx:cParser.Constant_expressionContext):
        pass

    # Exit a parse tree produced by cParser#constant_expression.
    def exitConstant_expression(self, ctx:cParser.Constant_expressionContext):
        pass


    # Enter a parse tree produced by cParser#declaration.
    def enterDeclaration(self, ctx:cParser.DeclarationContext):
        pass

    # Exit a parse tree produced by cParser#declaration.
    def exitDeclaration(self, ctx:cParser.DeclarationContext):
        pass


    # Enter a parse tree produced by cParser#declaration_specifiers.
    def enterDeclaration_specifiers(self, ctx:cParser.Declaration_specifiersContext):
        pass

    # Exit a parse tree produced by cParser#declaration_specifiers.
    def exitDeclaration_specifiers(self, ctx:cParser.Declaration_specifiersContext):
        pass


    # Enter a parse tree produced by cParser#init_declarator_list.
    def enterInit_declarator_list(self, ctx:cParser.Init_declarator_listContext):
        pass

    # Exit a parse tree produced by cParser#init_declarator_list.
    def exitInit_declarator_list(self, ctx:cParser.Init_declarator_listContext):
        pass


    # Enter a parse tree produced by cParser#init_declarator.
    def enterInit_declarator(self, ctx:cParser.Init_declaratorContext):
        pass

    # Exit a parse tree produced by cParser#init_declarator.
    def exitInit_declarator(self, ctx:cParser.Init_declaratorContext):
        pass


    # Enter a parse tree produced by cParser#type_specifier.
    def enterType_specifier(self, ctx:cParser.Type_specifierContext):
        pass

    # Exit a parse tree produced by cParser#type_specifier.
    def exitType_specifier(self, ctx:cParser.Type_specifierContext):
        pass


    # Enter a parse tree produced by cParser#specifier_qualifier_list.
    def enterSpecifier_qualifier_list(self, ctx:cParser.Specifier_qualifier_listContext):
        pass

    # Exit a parse tree produced by cParser#specifier_qualifier_list.
    def exitSpecifier_qualifier_list(self, ctx:cParser.Specifier_qualifier_listContext):
        pass


    # Enter a parse tree produced by cParser#declarator.
    def enterDeclarator(self, ctx:cParser.DeclaratorContext):
        pass

    # Exit a parse tree produced by cParser#declarator.
    def exitDeclarator(self, ctx:cParser.DeclaratorContext):
        pass


    # Enter a parse tree produced by cParser#direct_declarator.
    def enterDirect_declarator(self, ctx:cParser.Direct_declaratorContext):
        pass

    # Exit a parse tree produced by cParser#direct_declarator.
    def exitDirect_declarator(self, ctx:cParser.Direct_declaratorContext):
        pass


    # Enter a parse tree produced by cParser#pointer.
    def enterPointer(self, ctx:cParser.PointerContext):
        pass

    # Exit a parse tree produced by cParser#pointer.
    def exitPointer(self, ctx:cParser.PointerContext):
        pass


    # Enter a parse tree produced by cParser#parameter_type_list.
    def enterParameter_type_list(self, ctx:cParser.Parameter_type_listContext):
        pass

    # Exit a parse tree produced by cParser#parameter_type_list.
    def exitParameter_type_list(self, ctx:cParser.Parameter_type_listContext):
        pass


    # Enter a parse tree produced by cParser#parameter_list.
    def enterParameter_list(self, ctx:cParser.Parameter_listContext):
        pass

    # Exit a parse tree produced by cParser#parameter_list.
    def exitParameter_list(self, ctx:cParser.Parameter_listContext):
        pass


    # Enter a parse tree produced by cParser#parameter_declaration.
    def enterParameter_declaration(self, ctx:cParser.Parameter_declarationContext):
        pass

    # Exit a parse tree produced by cParser#parameter_declaration.
    def exitParameter_declaration(self, ctx:cParser.Parameter_declarationContext):
        pass


    # Enter a parse tree produced by cParser#identifier_list.
    def enterIdentifier_list(self, ctx:cParser.Identifier_listContext):
        pass

    # Exit a parse tree produced by cParser#identifier_list.
    def exitIdentifier_list(self, ctx:cParser.Identifier_listContext):
        pass


    # Enter a parse tree produced by cParser#type_name.
    def enterType_name(self, ctx:cParser.Type_nameContext):
        pass

    # Exit a parse tree produced by cParser#type_name.
    def exitType_name(self, ctx:cParser.Type_nameContext):
        pass


    # Enter a parse tree produced by cParser#initializer.
    def enterInitializer(self, ctx:cParser.InitializerContext):
        pass

    # Exit a parse tree produced by cParser#initializer.
    def exitInitializer(self, ctx:cParser.InitializerContext):
        pass


    # Enter a parse tree produced by cParser#initializer_list.
    def enterInitializer_list(self, ctx:cParser.Initializer_listContext):
        pass

    # Exit a parse tree produced by cParser#initializer_list.
    def exitInitializer_list(self, ctx:cParser.Initializer_listContext):
        pass


    # Enter a parse tree produced by cParser#designation.
    def enterDesignation(self, ctx:cParser.DesignationContext):
        pass

    # Exit a parse tree produced by cParser#designation.
    def exitDesignation(self, ctx:cParser.DesignationContext):
        pass


    # Enter a parse tree produced by cParser#designator_list.
    def enterDesignator_list(self, ctx:cParser.Designator_listContext):
        pass

    # Exit a parse tree produced by cParser#designator_list.
    def exitDesignator_list(self, ctx:cParser.Designator_listContext):
        pass


    # Enter a parse tree produced by cParser#designator.
    def enterDesignator(self, ctx:cParser.DesignatorContext):
        pass

    # Exit a parse tree produced by cParser#designator.
    def exitDesignator(self, ctx:cParser.DesignatorContext):
        pass


    # Enter a parse tree produced by cParser#statement.
    def enterStatement(self, ctx:cParser.StatementContext):
        pass

    # Exit a parse tree produced by cParser#statement.
    def exitStatement(self, ctx:cParser.StatementContext):
        pass


    # Enter a parse tree produced by cParser#labeled_statement.
    def enterLabeled_statement(self, ctx:cParser.Labeled_statementContext):
        pass

    # Exit a parse tree produced by cParser#labeled_statement.
    def exitLabeled_statement(self, ctx:cParser.Labeled_statementContext):
        pass


    # Enter a parse tree produced by cParser#compound_statement.
    def enterCompound_statement(self, ctx:cParser.Compound_statementContext):
        pass

    # Exit a parse tree produced by cParser#compound_statement.
    def exitCompound_statement(self, ctx:cParser.Compound_statementContext):
        pass


    # Enter a parse tree produced by cParser#block_item_list.
    def enterBlock_item_list(self, ctx:cParser.Block_item_listContext):
        pass

    # Exit a parse tree produced by cParser#block_item_list.
    def exitBlock_item_list(self, ctx:cParser.Block_item_listContext):
        pass


    # Enter a parse tree produced by cParser#block_item.
    def enterBlock_item(self, ctx:cParser.Block_itemContext):
        pass

    # Exit a parse tree produced by cParser#block_item.
    def exitBlock_item(self, ctx:cParser.Block_itemContext):
        pass


    # Enter a parse tree produced by cParser#expression_statement.
    def enterExpression_statement(self, ctx:cParser.Expression_statementContext):
        pass

    # Exit a parse tree produced by cParser#expression_statement.
    def exitExpression_statement(self, ctx:cParser.Expression_statementContext):
        pass


    # Enter a parse tree produced by cParser#selection_statement.
    def enterSelection_statement(self, ctx:cParser.Selection_statementContext):
        pass

    # Exit a parse tree produced by cParser#selection_statement.
    def exitSelection_statement(self, ctx:cParser.Selection_statementContext):
        pass


    # Enter a parse tree produced by cParser#iteration_statement.
    def enterIteration_statement(self, ctx:cParser.Iteration_statementContext):
        pass

    # Exit a parse tree produced by cParser#iteration_statement.
    def exitIteration_statement(self, ctx:cParser.Iteration_statementContext):
        pass


    # Enter a parse tree produced by cParser#jump_statement.
    def enterJump_statement(self, ctx:cParser.Jump_statementContext):
        pass

    # Exit a parse tree produced by cParser#jump_statement.
    def exitJump_statement(self, ctx:cParser.Jump_statementContext):
        pass


    # Enter a parse tree produced by cParser#external_declaration.
    def enterExternal_declaration(self, ctx:cParser.External_declarationContext):
        pass

    # Exit a parse tree produced by cParser#external_declaration.
    def exitExternal_declaration(self, ctx:cParser.External_declarationContext):
        pass


    # Enter a parse tree produced by cParser#function_definition.
    def enterFunction_definition(self, ctx:cParser.Function_definitionContext):
        pass

    # Exit a parse tree produced by cParser#function_definition.
    def exitFunction_definition(self, ctx:cParser.Function_definitionContext):
        pass


    # Enter a parse tree produced by cParser#declaration_list.
    def enterDeclaration_list(self, ctx:cParser.Declaration_listContext):
        pass

    # Exit a parse tree produced by cParser#declaration_list.
    def exitDeclaration_list(self, ctx:cParser.Declaration_listContext):
        pass


