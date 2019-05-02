# Generated from C.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CParser import CParser
else:
    from CParser import CParser

# This class defines a complete generic visitor for a parse tree produced by CParser.

class CVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CParser#compilationUnit.
    def visitCompilationUnit(self, ctx:CParser.CompilationUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#identifier.
    def visitIdentifier(self, ctx:CParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#constant.
    def visitConstant(self, ctx:CParser.ConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#stringLiteral.
    def visitStringLiteral(self, ctx:CParser.StringLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#parenExpression.
    def visitParenExpression(self, ctx:CParser.ParenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#functionCall.
    def visitFunctionCall(self, ctx:CParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#postfixPassthrough.
    def visitPostfixPassthrough(self, ctx:CParser.PostfixPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#arrayAccess.
    def visitArrayAccess(self, ctx:CParser.ArrayAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#postfixDecrement.
    def visitPostfixDecrement(self, ctx:CParser.PostfixDecrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#indirection.
    def visitIndirection(self, ctx:CParser.IndirectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#logicalNot.
    def visitLogicalNot(self, ctx:CParser.LogicalNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#prefixIncrement.
    def visitPrefixIncrement(self, ctx:CParser.PrefixIncrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#unaryPassthrough.
    def visitUnaryPassthrough(self, ctx:CParser.UnaryPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#unaryPlus.
    def visitUnaryPlus(self, ctx:CParser.UnaryPlusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#postfixIncrement.
    def visitPostfixIncrement(self, ctx:CParser.PostfixIncrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#unaryMinus.
    def visitUnaryMinus(self, ctx:CParser.UnaryMinusContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#prefixDecrement.
    def visitPrefixDecrement(self, ctx:CParser.PrefixDecrementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#castPassthrough.
    def visitCastPassthrough(self, ctx:CParser.CastPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#cast.
    def visitCast(self, ctx:CParser.CastContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#division.
    def visitDivision(self, ctx:CParser.DivisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#multiplicativePassthrough.
    def visitMultiplicativePassthrough(self, ctx:CParser.MultiplicativePassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#multiplication.
    def visitMultiplication(self, ctx:CParser.MultiplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#modulo.
    def visitModulo(self, ctx:CParser.ModuloContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#additivePassthrough.
    def visitAdditivePassthrough(self, ctx:CParser.AdditivePassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#subtraction.
    def visitSubtraction(self, ctx:CParser.SubtractionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#addition.
    def visitAddition(self, ctx:CParser.AdditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#largerThan.
    def visitLargerThan(self, ctx:CParser.LargerThanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#smallerThan.
    def visitSmallerThan(self, ctx:CParser.SmallerThanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#relationalPassthrough.
    def visitRelationalPassthrough(self, ctx:CParser.RelationalPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#smallerThanOrEqual.
    def visitSmallerThanOrEqual(self, ctx:CParser.SmallerThanOrEqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#largerThanOrEqual.
    def visitLargerThanOrEqual(self, ctx:CParser.LargerThanOrEqualContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#equalityPassthrough.
    def visitEqualityPassthrough(self, ctx:CParser.EqualityPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#equals.
    def visitEquals(self, ctx:CParser.EqualsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#notEquals.
    def visitNotEquals(self, ctx:CParser.NotEqualsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#logicalPassthrough.
    def visitLogicalPassthrough(self, ctx:CParser.LogicalPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#logicalAnd.
    def visitLogicalAnd(self, ctx:CParser.LogicalAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#logicalOr.
    def visitLogicalOr(self, ctx:CParser.LogicalOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#conditionalPassthrough.
    def visitConditionalPassthrough(self, ctx:CParser.ConditionalPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#conditional.
    def visitConditional(self, ctx:CParser.ConditionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#assignmentPassthrough.
    def visitAssignmentPassthrough(self, ctx:CParser.AssignmentPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#assignment.
    def visitAssignment(self, ctx:CParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#expressionList.
    def visitExpressionList(self, ctx:CParser.ExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#expressionPassthrough.
    def visitExpressionPassthrough(self, ctx:CParser.ExpressionPassthroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#constantExpression.
    def visitConstantExpression(self, ctx:CParser.ConstantExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#declaration.
    def visitDeclaration(self, ctx:CParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#declarationSpecifiers.
    def visitDeclarationSpecifiers(self, ctx:CParser.DeclarationSpecifiersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#initDeclaratorList.
    def visitInitDeclaratorList(self, ctx:CParser.InitDeclaratorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#initDeclarator.
    def visitInitDeclarator(self, ctx:CParser.InitDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#typeSpecifier.
    def visitTypeSpecifier(self, ctx:CParser.TypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#specifierQualifierList.
    def visitSpecifierQualifierList(self, ctx:CParser.SpecifierQualifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#declarator.
    def visitDeclarator(self, ctx:CParser.DeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#arrayDeclarator.
    def visitArrayDeclarator(self, ctx:CParser.ArrayDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#parenDeclarator.
    def visitParenDeclarator(self, ctx:CParser.ParenDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#identifierDeclarator.
    def visitIdentifierDeclarator(self, ctx:CParser.IdentifierDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#functionDeclarator.
    def visitFunctionDeclarator(self, ctx:CParser.FunctionDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#pointer.
    def visitPointer(self, ctx:CParser.PointerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#parameterTypeList.
    def visitParameterTypeList(self, ctx:CParser.ParameterTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#parameterList.
    def visitParameterList(self, ctx:CParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#parameterDeclaration.
    def visitParameterDeclaration(self, ctx:CParser.ParameterDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#typeName.
    def visitTypeName(self, ctx:CParser.TypeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#initializer.
    def visitInitializer(self, ctx:CParser.InitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#initializerList.
    def visitInitializerList(self, ctx:CParser.InitializerListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#statement.
    def visitStatement(self, ctx:CParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#labeledStatement.
    def visitLabeledStatement(self, ctx:CParser.LabeledStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#compoundStatement.
    def visitCompoundStatement(self, ctx:CParser.CompoundStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#blockItemList.
    def visitBlockItemList(self, ctx:CParser.BlockItemListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#blockItem.
    def visitBlockItem(self, ctx:CParser.BlockItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#expressionStatement.
    def visitExpressionStatement(self, ctx:CParser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#selectionStatement.
    def visitSelectionStatement(self, ctx:CParser.SelectionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#iterationStatement.
    def visitIterationStatement(self, ctx:CParser.IterationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#goto.
    def visitGoto(self, ctx:CParser.GotoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#continue.
    def visitContinue(self, ctx:CParser.ContinueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#break.
    def visitBreak(self, ctx:CParser.BreakContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#return.
    def visitReturn(self, ctx:CParser.ReturnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#functionDefinition.
    def visitFunctionDefinition(self, ctx:CParser.FunctionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CParser#declarationList.
    def visitDeclarationList(self, ctx:CParser.DeclarationListContext):
        return self.visitChildren(ctx)



del CParser