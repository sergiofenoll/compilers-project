# Generated from C.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CParser import CParser
else:
    from CParser import CParser

# This class defines a complete listener for a parse tree produced by CParser.
class CListener(ParseTreeListener):

    # Enter a parse tree produced by CParser#compilationUnit.
    def enterCompilationUnit(self, ctx:CParser.CompilationUnitContext):
        pass

    # Exit a parse tree produced by CParser#compilationUnit.
    def exitCompilationUnit(self, ctx:CParser.CompilationUnitContext):
        pass


    # Enter a parse tree produced by CParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:CParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by CParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:CParser.PrimaryExpressionContext):
        pass


    # Enter a parse tree produced by CParser#postfixExpression.
    def enterPostfixExpression(self, ctx:CParser.PostfixExpressionContext):
        pass

    # Exit a parse tree produced by CParser#postfixExpression.
    def exitPostfixExpression(self, ctx:CParser.PostfixExpressionContext):
        pass


    # Enter a parse tree produced by CParser#argumentExpressionList.
    def enterArgumentExpressionList(self, ctx:CParser.ArgumentExpressionListContext):
        pass

    # Exit a parse tree produced by CParser#argumentExpressionList.
    def exitArgumentExpressionList(self, ctx:CParser.ArgumentExpressionListContext):
        pass


    # Enter a parse tree produced by CParser#unaryExpression.
    def enterUnaryExpression(self, ctx:CParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by CParser#unaryExpression.
    def exitUnaryExpression(self, ctx:CParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by CParser#castExpression.
    def enterCastExpression(self, ctx:CParser.CastExpressionContext):
        pass

    # Exit a parse tree produced by CParser#castExpression.
    def exitCastExpression(self, ctx:CParser.CastExpressionContext):
        pass


    # Enter a parse tree produced by CParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:CParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by CParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:CParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by CParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:CParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by CParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:CParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by CParser#relationalExpression.
    def enterRelationalExpression(self, ctx:CParser.RelationalExpressionContext):
        pass

    # Exit a parse tree produced by CParser#relationalExpression.
    def exitRelationalExpression(self, ctx:CParser.RelationalExpressionContext):
        pass


    # Enter a parse tree produced by CParser#equalityExpression.
    def enterEqualityExpression(self, ctx:CParser.EqualityExpressionContext):
        pass

    # Exit a parse tree produced by CParser#equalityExpression.
    def exitEqualityExpression(self, ctx:CParser.EqualityExpressionContext):
        pass


    # Enter a parse tree produced by CParser#logicalExpression.
    def enterLogicalExpression(self, ctx:CParser.LogicalExpressionContext):
        pass

    # Exit a parse tree produced by CParser#logicalExpression.
    def exitLogicalExpression(self, ctx:CParser.LogicalExpressionContext):
        pass


    # Enter a parse tree produced by CParser#conditionalExpression.
    def enterConditionalExpression(self, ctx:CParser.ConditionalExpressionContext):
        pass

    # Exit a parse tree produced by CParser#conditionalExpression.
    def exitConditionalExpression(self, ctx:CParser.ConditionalExpressionContext):
        pass


    # Enter a parse tree produced by CParser#assignmentExpression.
    def enterAssignmentExpression(self, ctx:CParser.AssignmentExpressionContext):
        pass

    # Exit a parse tree produced by CParser#assignmentExpression.
    def exitAssignmentExpression(self, ctx:CParser.AssignmentExpressionContext):
        pass


    # Enter a parse tree produced by CParser#expression.
    def enterExpression(self, ctx:CParser.ExpressionContext):
        pass

    # Exit a parse tree produced by CParser#expression.
    def exitExpression(self, ctx:CParser.ExpressionContext):
        pass


    # Enter a parse tree produced by CParser#constantExpression.
    def enterConstantExpression(self, ctx:CParser.ConstantExpressionContext):
        pass

    # Exit a parse tree produced by CParser#constantExpression.
    def exitConstantExpression(self, ctx:CParser.ConstantExpressionContext):
        pass


    # Enter a parse tree produced by CParser#declaration.
    def enterDeclaration(self, ctx:CParser.DeclarationContext):
        pass

    # Exit a parse tree produced by CParser#declaration.
    def exitDeclaration(self, ctx:CParser.DeclarationContext):
        pass


    # Enter a parse tree produced by CParser#declarationSpecifiers.
    def enterDeclarationSpecifiers(self, ctx:CParser.DeclarationSpecifiersContext):
        pass

    # Exit a parse tree produced by CParser#declarationSpecifiers.
    def exitDeclarationSpecifiers(self, ctx:CParser.DeclarationSpecifiersContext):
        pass


    # Enter a parse tree produced by CParser#initDeclaratorList.
    def enterInitDeclaratorList(self, ctx:CParser.InitDeclaratorListContext):
        pass

    # Exit a parse tree produced by CParser#initDeclaratorList.
    def exitInitDeclaratorList(self, ctx:CParser.InitDeclaratorListContext):
        pass


    # Enter a parse tree produced by CParser#initDeclarator.
    def enterInitDeclarator(self, ctx:CParser.InitDeclaratorContext):
        pass

    # Exit a parse tree produced by CParser#initDeclarator.
    def exitInitDeclarator(self, ctx:CParser.InitDeclaratorContext):
        pass


    # Enter a parse tree produced by CParser#typeSpecifier.
    def enterTypeSpecifier(self, ctx:CParser.TypeSpecifierContext):
        pass

    # Exit a parse tree produced by CParser#typeSpecifier.
    def exitTypeSpecifier(self, ctx:CParser.TypeSpecifierContext):
        pass


    # Enter a parse tree produced by CParser#specifierQualifierList.
    def enterSpecifierQualifierList(self, ctx:CParser.SpecifierQualifierListContext):
        pass

    # Exit a parse tree produced by CParser#specifierQualifierList.
    def exitSpecifierQualifierList(self, ctx:CParser.SpecifierQualifierListContext):
        pass


    # Enter a parse tree produced by CParser#declarator.
    def enterDeclarator(self, ctx:CParser.DeclaratorContext):
        pass

    # Exit a parse tree produced by CParser#declarator.
    def exitDeclarator(self, ctx:CParser.DeclaratorContext):
        pass


    # Enter a parse tree produced by CParser#directDeclarator.
    def enterDirectDeclarator(self, ctx:CParser.DirectDeclaratorContext):
        pass

    # Exit a parse tree produced by CParser#directDeclarator.
    def exitDirectDeclarator(self, ctx:CParser.DirectDeclaratorContext):
        pass


    # Enter a parse tree produced by CParser#pointer.
    def enterPointer(self, ctx:CParser.PointerContext):
        pass

    # Exit a parse tree produced by CParser#pointer.
    def exitPointer(self, ctx:CParser.PointerContext):
        pass


    # Enter a parse tree produced by CParser#parameterTypeList.
    def enterParameterTypeList(self, ctx:CParser.ParameterTypeListContext):
        pass

    # Exit a parse tree produced by CParser#parameterTypeList.
    def exitParameterTypeList(self, ctx:CParser.ParameterTypeListContext):
        pass


    # Enter a parse tree produced by CParser#parameterList.
    def enterParameterList(self, ctx:CParser.ParameterListContext):
        pass

    # Exit a parse tree produced by CParser#parameterList.
    def exitParameterList(self, ctx:CParser.ParameterListContext):
        pass


    # Enter a parse tree produced by CParser#parameterDeclaration.
    def enterParameterDeclaration(self, ctx:CParser.ParameterDeclarationContext):
        pass

    # Exit a parse tree produced by CParser#parameterDeclaration.
    def exitParameterDeclaration(self, ctx:CParser.ParameterDeclarationContext):
        pass


    # Enter a parse tree produced by CParser#identifierList.
    def enterIdentifierList(self, ctx:CParser.IdentifierListContext):
        pass

    # Exit a parse tree produced by CParser#identifierList.
    def exitIdentifierList(self, ctx:CParser.IdentifierListContext):
        pass


    # Enter a parse tree produced by CParser#typeName.
    def enterTypeName(self, ctx:CParser.TypeNameContext):
        pass

    # Exit a parse tree produced by CParser#typeName.
    def exitTypeName(self, ctx:CParser.TypeNameContext):
        pass


    # Enter a parse tree produced by CParser#initializer.
    def enterInitializer(self, ctx:CParser.InitializerContext):
        pass

    # Exit a parse tree produced by CParser#initializer.
    def exitInitializer(self, ctx:CParser.InitializerContext):
        pass


    # Enter a parse tree produced by CParser#initializerList.
    def enterInitializerList(self, ctx:CParser.InitializerListContext):
        pass

    # Exit a parse tree produced by CParser#initializerList.
    def exitInitializerList(self, ctx:CParser.InitializerListContext):
        pass


    # Enter a parse tree produced by CParser#statement.
    def enterStatement(self, ctx:CParser.StatementContext):
        pass

    # Exit a parse tree produced by CParser#statement.
    def exitStatement(self, ctx:CParser.StatementContext):
        pass


    # Enter a parse tree produced by CParser#labeledStatement.
    def enterLabeledStatement(self, ctx:CParser.LabeledStatementContext):
        pass

    # Exit a parse tree produced by CParser#labeledStatement.
    def exitLabeledStatement(self, ctx:CParser.LabeledStatementContext):
        pass


    # Enter a parse tree produced by CParser#compoundStatement.
    def enterCompoundStatement(self, ctx:CParser.CompoundStatementContext):
        pass

    # Exit a parse tree produced by CParser#compoundStatement.
    def exitCompoundStatement(self, ctx:CParser.CompoundStatementContext):
        pass


    # Enter a parse tree produced by CParser#blockItemList.
    def enterBlockItemList(self, ctx:CParser.BlockItemListContext):
        pass

    # Exit a parse tree produced by CParser#blockItemList.
    def exitBlockItemList(self, ctx:CParser.BlockItemListContext):
        pass


    # Enter a parse tree produced by CParser#blockItem.
    def enterBlockItem(self, ctx:CParser.BlockItemContext):
        pass

    # Exit a parse tree produced by CParser#blockItem.
    def exitBlockItem(self, ctx:CParser.BlockItemContext):
        pass


    # Enter a parse tree produced by CParser#expressionStatement.
    def enterExpressionStatement(self, ctx:CParser.ExpressionStatementContext):
        pass

    # Exit a parse tree produced by CParser#expressionStatement.
    def exitExpressionStatement(self, ctx:CParser.ExpressionStatementContext):
        pass


    # Enter a parse tree produced by CParser#selectionStatement.
    def enterSelectionStatement(self, ctx:CParser.SelectionStatementContext):
        pass

    # Exit a parse tree produced by CParser#selectionStatement.
    def exitSelectionStatement(self, ctx:CParser.SelectionStatementContext):
        pass


    # Enter a parse tree produced by CParser#iterationStatement.
    def enterIterationStatement(self, ctx:CParser.IterationStatementContext):
        pass

    # Exit a parse tree produced by CParser#iterationStatement.
    def exitIterationStatement(self, ctx:CParser.IterationStatementContext):
        pass


    # Enter a parse tree produced by CParser#jumpStatement.
    def enterJumpStatement(self, ctx:CParser.JumpStatementContext):
        pass

    # Exit a parse tree produced by CParser#jumpStatement.
    def exitJumpStatement(self, ctx:CParser.JumpStatementContext):
        pass


    # Enter a parse tree produced by CParser#functionDefinition.
    def enterFunctionDefinition(self, ctx:CParser.FunctionDefinitionContext):
        pass

    # Exit a parse tree produced by CParser#functionDefinition.
    def exitFunctionDefinition(self, ctx:CParser.FunctionDefinitionContext):
        pass


    # Enter a parse tree produced by CParser#declarationList.
    def enterDeclarationList(self, ctx:CParser.DeclarationListContext):
        pass

    # Exit a parse tree produced by CParser#declarationList.
    def exitDeclarationList(self, ctx:CParser.DeclarationListContext):
        pass


