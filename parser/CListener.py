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


    # Enter a parse tree produced by CParser#identifier.
    def enterIdentifier(self, ctx:CParser.IdentifierContext):
        pass

    # Exit a parse tree produced by CParser#identifier.
    def exitIdentifier(self, ctx:CParser.IdentifierContext):
        pass


    # Enter a parse tree produced by CParser#constant.
    def enterConstant(self, ctx:CParser.ConstantContext):
        pass

    # Exit a parse tree produced by CParser#constant.
    def exitConstant(self, ctx:CParser.ConstantContext):
        pass


    # Enter a parse tree produced by CParser#stringLiteral.
    def enterStringLiteral(self, ctx:CParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by CParser#stringLiteral.
    def exitStringLiteral(self, ctx:CParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by CParser#parenExpression.
    def enterParenExpression(self, ctx:CParser.ParenExpressionContext):
        pass

    # Exit a parse tree produced by CParser#parenExpression.
    def exitParenExpression(self, ctx:CParser.ParenExpressionContext):
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


    # Enter a parse tree produced by CParser#postfixDecrement.
    def enterPostfixDecrement(self, ctx:CParser.PostfixDecrementContext):
        pass

    # Exit a parse tree produced by CParser#postfixDecrement.
    def exitPostfixDecrement(self, ctx:CParser.PostfixDecrementContext):
        pass


    # Enter a parse tree produced by CParser#prefixIncrement.
    def enterPrefixIncrement(self, ctx:CParser.PrefixIncrementContext):
        pass

    # Exit a parse tree produced by CParser#prefixIncrement.
    def exitPrefixIncrement(self, ctx:CParser.PrefixIncrementContext):
        pass


    # Enter a parse tree produced by CParser#unaryPassthrough.
    def enterUnaryPassthrough(self, ctx:CParser.UnaryPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#unaryPassthrough.
    def exitUnaryPassthrough(self, ctx:CParser.UnaryPassthroughContext):
        pass


    # Enter a parse tree produced by CParser#postfixIncrement.
    def enterPostfixIncrement(self, ctx:CParser.PostfixIncrementContext):
        pass

    # Exit a parse tree produced by CParser#postfixIncrement.
    def exitPostfixIncrement(self, ctx:CParser.PostfixIncrementContext):
        pass


    # Enter a parse tree produced by CParser#unary.
    def enterUnary(self, ctx:CParser.UnaryContext):
        pass

    # Exit a parse tree produced by CParser#unary.
    def exitUnary(self, ctx:CParser.UnaryContext):
        pass


    # Enter a parse tree produced by CParser#prefixDecrement.
    def enterPrefixDecrement(self, ctx:CParser.PrefixDecrementContext):
        pass

    # Exit a parse tree produced by CParser#prefixDecrement.
    def exitPrefixDecrement(self, ctx:CParser.PrefixDecrementContext):
        pass


    # Enter a parse tree produced by CParser#castPassthrough.
    def enterCastPassthrough(self, ctx:CParser.CastPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#castPassthrough.
    def exitCastPassthrough(self, ctx:CParser.CastPassthroughContext):
        pass


    # Enter a parse tree produced by CParser#cast.
    def enterCast(self, ctx:CParser.CastContext):
        pass

    # Exit a parse tree produced by CParser#cast.
    def exitCast(self, ctx:CParser.CastContext):
        pass


    # Enter a parse tree produced by CParser#division.
    def enterDivision(self, ctx:CParser.DivisionContext):
        pass

    # Exit a parse tree produced by CParser#division.
    def exitDivision(self, ctx:CParser.DivisionContext):
        pass


    # Enter a parse tree produced by CParser#multiplicativePassthrough.
    def enterMultiplicativePassthrough(self, ctx:CParser.MultiplicativePassthroughContext):
        pass

    # Exit a parse tree produced by CParser#multiplicativePassthrough.
    def exitMultiplicativePassthrough(self, ctx:CParser.MultiplicativePassthroughContext):
        pass


    # Enter a parse tree produced by CParser#multiplication.
    def enterMultiplication(self, ctx:CParser.MultiplicationContext):
        pass

    # Exit a parse tree produced by CParser#multiplication.
    def exitMultiplication(self, ctx:CParser.MultiplicationContext):
        pass


    # Enter a parse tree produced by CParser#modulo.
    def enterModulo(self, ctx:CParser.ModuloContext):
        pass

    # Exit a parse tree produced by CParser#modulo.
    def exitModulo(self, ctx:CParser.ModuloContext):
        pass


    # Enter a parse tree produced by CParser#additivePassthrough.
    def enterAdditivePassthrough(self, ctx:CParser.AdditivePassthroughContext):
        pass

    # Exit a parse tree produced by CParser#additivePassthrough.
    def exitAdditivePassthrough(self, ctx:CParser.AdditivePassthroughContext):
        pass


    # Enter a parse tree produced by CParser#subtraction.
    def enterSubtraction(self, ctx:CParser.SubtractionContext):
        pass

    # Exit a parse tree produced by CParser#subtraction.
    def exitSubtraction(self, ctx:CParser.SubtractionContext):
        pass


    # Enter a parse tree produced by CParser#addition.
    def enterAddition(self, ctx:CParser.AdditionContext):
        pass

    # Exit a parse tree produced by CParser#addition.
    def exitAddition(self, ctx:CParser.AdditionContext):
        pass


    # Enter a parse tree produced by CParser#largerThan.
    def enterLargerThan(self, ctx:CParser.LargerThanContext):
        pass

    # Exit a parse tree produced by CParser#largerThan.
    def exitLargerThan(self, ctx:CParser.LargerThanContext):
        pass


    # Enter a parse tree produced by CParser#smallerThan.
    def enterSmallerThan(self, ctx:CParser.SmallerThanContext):
        pass

    # Exit a parse tree produced by CParser#smallerThan.
    def exitSmallerThan(self, ctx:CParser.SmallerThanContext):
        pass


    # Enter a parse tree produced by CParser#relationalPassthrough.
    def enterRelationalPassthrough(self, ctx:CParser.RelationalPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#relationalPassthrough.
    def exitRelationalPassthrough(self, ctx:CParser.RelationalPassthroughContext):
        pass


    # Enter a parse tree produced by CParser#smallerThanOrEqual.
    def enterSmallerThanOrEqual(self, ctx:CParser.SmallerThanOrEqualContext):
        pass

    # Exit a parse tree produced by CParser#smallerThanOrEqual.
    def exitSmallerThanOrEqual(self, ctx:CParser.SmallerThanOrEqualContext):
        pass


    # Enter a parse tree produced by CParser#largerThanOrEqual.
    def enterLargerThanOrEqual(self, ctx:CParser.LargerThanOrEqualContext):
        pass

    # Exit a parse tree produced by CParser#largerThanOrEqual.
    def exitLargerThanOrEqual(self, ctx:CParser.LargerThanOrEqualContext):
        pass


    # Enter a parse tree produced by CParser#equalityPassthrough.
    def enterEqualityPassthrough(self, ctx:CParser.EqualityPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#equalityPassthrough.
    def exitEqualityPassthrough(self, ctx:CParser.EqualityPassthroughContext):
        pass


    # Enter a parse tree produced by CParser#equals.
    def enterEquals(self, ctx:CParser.EqualsContext):
        pass

    # Exit a parse tree produced by CParser#equals.
    def exitEquals(self, ctx:CParser.EqualsContext):
        pass


    # Enter a parse tree produced by CParser#notEquals.
    def enterNotEquals(self, ctx:CParser.NotEqualsContext):
        pass

    # Exit a parse tree produced by CParser#notEquals.
    def exitNotEquals(self, ctx:CParser.NotEqualsContext):
        pass


    # Enter a parse tree produced by CParser#logicalPassthrough.
    def enterLogicalPassthrough(self, ctx:CParser.LogicalPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#logicalPassthrough.
    def exitLogicalPassthrough(self, ctx:CParser.LogicalPassthroughContext):
        pass


    # Enter a parse tree produced by CParser#logicalAnd.
    def enterLogicalAnd(self, ctx:CParser.LogicalAndContext):
        pass

    # Exit a parse tree produced by CParser#logicalAnd.
    def exitLogicalAnd(self, ctx:CParser.LogicalAndContext):
        pass


    # Enter a parse tree produced by CParser#logicalOr.
    def enterLogicalOr(self, ctx:CParser.LogicalOrContext):
        pass

    # Exit a parse tree produced by CParser#logicalOr.
    def exitLogicalOr(self, ctx:CParser.LogicalOrContext):
        pass


    # Enter a parse tree produced by CParser#conditionalPassthrough.
    def enterConditionalPassthrough(self, ctx:CParser.ConditionalPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#conditionalPassthrough.
    def exitConditionalPassthrough(self, ctx:CParser.ConditionalPassthroughContext):
        pass


    # Enter a parse tree produced by CParser#conditional.
    def enterConditional(self, ctx:CParser.ConditionalContext):
        pass

    # Exit a parse tree produced by CParser#conditional.
    def exitConditional(self, ctx:CParser.ConditionalContext):
        pass


    # Enter a parse tree produced by CParser#assignmentPassthrough.
    def enterAssignmentPassthrough(self, ctx:CParser.AssignmentPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#assignmentPassthrough.
    def exitAssignmentPassthrough(self, ctx:CParser.AssignmentPassthroughContext):
        pass


    # Enter a parse tree produced by CParser#assignment.
    def enterAssignment(self, ctx:CParser.AssignmentContext):
        pass

    # Exit a parse tree produced by CParser#assignment.
    def exitAssignment(self, ctx:CParser.AssignmentContext):
        pass


    # Enter a parse tree produced by CParser#expressionList.
    def enterExpressionList(self, ctx:CParser.ExpressionListContext):
        pass

    # Exit a parse tree produced by CParser#expressionList.
    def exitExpressionList(self, ctx:CParser.ExpressionListContext):
        pass


    # Enter a parse tree produced by CParser#expressionPassthrough.
    def enterExpressionPassthrough(self, ctx:CParser.ExpressionPassthroughContext):
        pass

    # Exit a parse tree produced by CParser#expressionPassthrough.
    def exitExpressionPassthrough(self, ctx:CParser.ExpressionPassthroughContext):
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


