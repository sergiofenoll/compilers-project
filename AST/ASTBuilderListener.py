import AST.AST as AST
import AST.STT as STT
from parser.CParser import CParser
from parser.CListener import CListener


def enter_decorate_no_scope(method):
    def decorated_enter(self, ctx):
        ast_node_name = method.__name__.replace("enter", "AST").replace("exit", "AST") + "Node"
        ast_node_type = getattr(AST, ast_node_name)
        node = ast_node_type(ctx)
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
    return decorated_enter


def enter_decorate_scope(method):
    def decorated_enter(self, ctx):
        ast_node_name = method.__name__.replace("enter", "AST").replace("exit", "AST") + "Node"
        ast_node_type = getattr(AST, ast_node_name)
        node = ast_node_type(ctx)
        node.parent = self.current_node

        scope = STT.STTNode()
        scope.parent = self.current_node.scope
        scope.depth = scope.parent.depth + 1
        self.current_node.scope.children.append(scope)

        node.scope = scope
        self.current_node.children.append(node)
    return decorated_enter


class ASTBuilder(CListener):
    def __init__(self, ast):
        self.current_node = ast

    def enterIdentifier(self, ctx:CParser.IdentifierContext):
        identifier = str(ctx.Identifier())
        node = AST.ASTIdentifierNode(identifier)
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)

        STEntry = self.current_node.scope.lookup(identifier)

        if STEntry:
            STEntry.used = True
        else:
            print(f"Using undeclared variable {identifier}")
            exit()

    def enterConstant(self, ctx:CParser.ConstantContext):
        if ctx.ConstantChar():
            constant = str(ctx.ConstantChar())
            type_specifier = "char"
        elif ctx.ConstantFloat():
            constant = float(str(ctx.ConstantFloat()))
            type_specifier = "float"
        else:
            constant = int(str(ctx.ConstantInt()))
            type_specifier = "int"
        node = AST.ASTConstantNode(constant, type_specifier)
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)

    def enterStringLiteral(self, ctx:CParser.StringLiteralContext):
        node = AST.ASTStringLiteralNode(str(ctx.StringLiteral()))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)

    def enterArrayAccess(self, ctx:CParser.ArrayAccessContext):
        node = AST.ASTArrayAccessNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitArrayAccess(self, ctx:CParser.ArrayAccessContext):
        self.current_node = self.current_node.parent

    def enterFunctionCall(self, ctx:CParser.FunctionCallContext):
        node = AST.ASTFunctionCallNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitFunctionCall(self, ctx:CParser.FunctionCallContext):
        self.current_node = self.current_node.parent

    def enterPostfixIncrement(self, ctx:CParser.PostfixIncrementContext):
        node = AST.ASTPostfixIncrementNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitPostfixIncrement(self, ctx:CParser.PostfixIncrementContext):
        self.current_node = self.current_node.parent

    def enterPostfixDecrement(self, ctx:CParser.PostfixDecrementContext):
        node = AST.ASTPostfixDecrementNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitPostfixDecrement(self, ctx:CParser.PostfixDecrementContext):
        self.current_node = self.current_node.parent

    def enterPrefixIncrement(self, ctx:CParser.PrefixIncrementContext):
        node = AST.ASTPrefixIncrementNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitPrefixIncrement(self, ctx:CParser.PrefixIncrementContext):
        self.current_node = self.current_node.parent

    def enterPrefixDecrement(self, ctx:CParser.PrefixDecrementContext):
        node = AST.ASTPrefixDecrementNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitPrefixDecrement(self, ctx:CParser.PrefixDecrementContext):
        self.current_node = self.current_node.parent

    def enterUnaryPlus(self, ctx:CParser.UnaryPlusContext):
        node = AST.ASTUnaryPlusNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitUnaryPlus(self, ctx:CParser.UnaryPlusContext):
        self.current_node = self.current_node.parent

    def enterUnaryMinus(self, ctx:CParser.UnaryMinusContext):
        node = AST.ASTUnaryMinusNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitUnaryMinus(self, ctx:CParser.UnaryMinusContext):
        self.current_node = self.current_node.parent

    def enterLogicalNot(self, ctx:CParser.LogicalNotContext):
        node = AST.ASTLogicalNotNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitLogicalNot(self, ctx:CParser.LogicalNotContext):
        self.current_node = self.current_node.parent

    def enterIndirection(self, ctx:CParser.IndirectionContext):
        node = AST.ASTIndirection()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitIndirection(self, ctx:CParser.IndirectionContext):
        self.current_node = self.current_node.parent

    def enterCast(self, ctx:CParser.CastContext):
        node = AST.ASTCastNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitCast(self, ctx:CParser.CastContext):
        print(self.current_node.identifier().identifier)
        self.current_node = self.current_node.parent

    def enterAssignment(self, ctx:CParser.AssignmentContext):
        node = AST.ASTAssignmentNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitAssignment(self, ctx:CParser.AssignmentContext):
        self.current_node = self.current_node.parent

    def enterMultiplication(self, ctx:CParser.MultiplicationContext):
        node = AST.ASTMultiplicationNode(c_idx = len(self.current_node.children))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitMultiplication(self, ctx:CParser.MultiplicationContext):
        self.current_node = self.current_node.parent

    def enterDivision(self, ctx:CParser.DivisionContext):
        node = AST.ASTDivisionNode(c_idx = len(self.current_node.children))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitDivision(self, ctx:CParser.DivisionContext):
        self.current_node = self.current_node.parent

    def enterModulo(self, ctx:CParser.ModuloContext):
        node = AST.ASTModuloNode(c_idx = len(self.current_node.children))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitModulo(self, ctx:CParser.ModuloContext):
        self.current_node = self.current_node.parent

    def enterAddition(self, ctx:CParser.AdditionContext):
        node = AST.ASTAdditionNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitAddition(self, ctx:CParser.AdditionContext):
        self.current_node = self.current_node.parent

    def enterSubtraction(self, ctx:CParser.SubtractionContext):
        node = AST.ASTSubtractionNode()
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitSubtraction(self, ctx:CParser.SubtractionContext):
        self.current_node = self.current_node.parent

    def enterSmallerThan(self, ctx:CParser.SmallerThanContext):
        node = AST.ASTSmallerThanNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitSmallerThan(self, ctx:CParser.SmallerThanContext):
        self.current_node = self.current_node.parent

    def enterLargerThan(self, ctx:CParser.LargerThanContext):
        node = AST.ASTLargerThanNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitLargerThan(self, ctx:CParser.LargerThanContext):
        self.current_node = self.current_node.parent

    def enterSmallerThanOrEqual(self, ctx:CParser.SmallerThanOrEqualContext):
        node = AST.ASTSmallerThanOrEqualNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitSmallerThanOrEqual(self, ctx:CParser.SmallerThanOrEqualContext):
        self.current_node = self.current_node.parent

    def enterLargerThanOrEqual(self, ctx:CParser.LargerThanOrEqualContext):
        node = AST.ASTLargerThanOrEqualNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitLargerThanOrEqual(self, ctx:CParser.LargerThanOrEqualContext):
        self.current_node = self.current_node.parent

    def enterEquals(self, ctx:CParser.EqualsContext):
        node = AST.ASTEqualsNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitEquals(self, ctx:CParser.EqualsContext):
        self.current_node = self.current_node.parent

    def enterNotEquals(self, ctx:CParser.NotEqualsContext):
        node = AST.ASTNotEqualsNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitNotEquals(self, ctx:CParser.NotEqualsContext):
        self.current_node = self.current_node.parent

    def enterLogicalAnd(self, ctx:CParser.LogicalAndContext):
        node = AST.ASTLogicalAndNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitLogicalAnd(self, ctx:CParser.LogicalAndContext):
        self.current_node = self.current_node.parent

    def enterLogicalOr(self, ctx:CParser.LogicalOrContext):
        node = AST.ASTLogicalOrNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitLogicalOr(self, ctx:CParser.LogicalOrContext):
        self.current_node = self.current_node.parent

    def enterConditional(self, ctx:CParser.ConditionalContext):
        node = AST.ASTIfStmtNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitConditional(self, ctx:CParser.ConditionalContext):
        self.current_node = self.current_node.parent

    def enterExpressionList(self, ctx:CParser.ExpressionListContext):
        node = AST.ASTExprListNode("ExpressionList")
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitExpressionList(self, ctx:CParser.ExpressionListContext):
        self.current_node = self.current_node.parent

    def enterTypeSpecifier(self, ctx:CParser.TypeSpecifierContext):
        tspec = str(ctx.children[0])
        node = AST.ASTTypeSpecifierNode(tspec)
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)

    def enterDirectDeclarator(self, ctx:CParser.DirectDeclaratorContext):
        if ctx.Identifier():
            node = AST.ASTIdentifierNode(str(ctx.Identifier()))
            node.parent = self.current_node
            node.scope = self.current_node.scope
            self.current_node.children.append(node)

    def enterPointer(self, ctx:CParser.PointerContext):
        pass

    def exitPointer(self, ctx:CParser.PointerContext):
        pass

    def enterLabeledStatement(self, ctx:CParser.LabeledStatementContext):
        label = ctx.Identifier()
        node = AST.ASTLabelStmtNode(label)
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitLabeledStatement(self, ctx:CParser.LabeledStatementContext):
        self.current_node = self.current_node.parent

    def enterSelectionStatement(self, ctx:CParser.SelectionStatementContext):
        node = AST.ASTIfStmtNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitSelectionStatement(self, ctx:CParser.SelectionStatementContext):
        self.current_node = self.current_node.parent

    def enterParameterTypeList(self, ctx:CParser.ParameterTypeListContext):
        node = AST.ASTParameterTypeList()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitParameterTypeList(self, ctx:CParser.ParameterTypeListContext):
        if isinstance(self.current_node.parent, AST.ASTFunctionDefinitionNode):
            for type_node, identifier_node in zip(self.current_node.children[0::2], self.current_node.children[1::2]):
                if identifier_node.identifier not in self.current_node.scope.table:
                    self.current_node.scope.table[identifier_node.identifier] = STT.STTEntry(identifier_node.identifier, type_node.type())

        self.current_node = self.current_node.parent

    def enterIterationStatement(self, ctx:CParser.IterationStatementContext):
        if ctx.For():
            node = AST.ASTForStmtNode("For")
            node.parent = self.current_node
            scope = STT.STTNode()
            scope.parent = self.current_node.scope
            scope.depth = scope.parent.depth + 1
            node.scope = scope
            self.current_node.scope.children.append(scope)
            self.current_node.children.append(node)
            self.current_node = node
        elif ctx.While():
            pass

    def exitIterationStatement(self, ctx:CParser.IterationStatementContext):
        self.current_node = self.current_node.parent

    def enterGoto(self, ctx:CParser.GotoContext):
        node = AST.ASTGotoNode()
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitGoto(self, ctx:CParser.GotoContext):
        self.current_node = self.current_node.parent

    def enterContinue(self, ctx:CParser.ContinueContext):
        node = AST.ASTContinueNode(c_idx = len(self.current_node.children))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitContinue(self, ctx:CParser.GotoContext):
        self.current_node = self.current_node.parent

    def enterBreak(self, ctx:CParser.BreakContext):
        node = AST.ASTBreakNode(c_idx = len(self.current_node.children))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitBreak(self, ctx:CParser.GotoContext):
        self.current_node = self.current_node.parent

    def enterReturn(self, ctx:CParser.ReturnContext):
        node = AST.ASTReturnNode(c_idx = len(self.current_node.children))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node
    
    def exitReturn(self, ctx:CParser.GotoContext):
        self.current_node = self.current_node.parent

    def enterCompoundStatement(self, ctx:CParser.CompoundStatementContext):
        node = AST.ASTCompoundStmtNode()
        node.parent = self.current_node
        if isinstance(ctx.parentCtx, CParser.FunctionDefinitionContext):
            node.scope = self.current_node.scope
        else:
            scope = STT.STTNode()
            scope.parent = self.current_node.scope
            scope.depth = scope.parent.depth + 1
            node.scope = scope
            self.current_node.scope.children.append(scope)
        self.current_node.children.append(node)
        self.current_node = node

    def exitCompoundStatement(self, ctx:CParser.CompoundStatementContext):
        self.current_node = self.current_node.parent

    def enterDeclaration(self, ctx:CParser.DeclarationContext):
        node = AST.ASTDeclarationNode(c_idx=len(self.current_node.children))
        node.parent = self.current_node
        node.scope = self.current_node.scope
        self.current_node.children.append(node)
        self.current_node = node

    def exitDeclaration(self, ctx:CParser.DeclarationContext):
        # Add identifier to symbol table
        type_spec = self.current_node.type()
        identifier = self.current_node.identifier().identifier

        if identifier not in self.current_node.scope.table:
            self.current_node.scope.table[identifier] = STT.STTEntry(identifier, type_spec)
        else:
            # TODO: Error about double declaration
            print("OI CUNT, YOU DECLARED THIS VARIABLE ALREADY")
            exit()

        self.current_node = self.current_node.parent

    def enterFunctionDefinition(self, ctx:CParser.FunctionDefinitionContext):
        node = AST.ASTFunctionDefinitionNode()
        node.parent = self.current_node
        scope = STT.STTNode()
        scope.parent = self.current_node.scope
        scope.depth = scope.parent.depth + 1
        node.scope = scope
        self.current_node.scope.children.append(scope)
        self.current_node.children.append(node)
        self.current_node = node

    def exitFunctionDefinition(self, ctx:CParser.FunctionDefinitionContext):
        # Add identifier to symbol table
        type_spec = self.current_node.returnType().tspec
        identifier = self.current_node.identifier().identifier
        args = []
        for arg in self.current_node.arguments():
            try:
                args.append(arg.tspec)
            except AttributeError:
                # Skip identifiers
                pass

        self.current_node = self.current_node.parent

        if identifier not in self.current_node.scope.table:
            self.current_node.scope.table[identifier] = STT.STTEntry(identifier, type_spec, args)
        else:
            # TODO: Error about double declaration
            print("OI CUNT, YOU DECLARED THIS FUNCTION ALREADY")
            exit()
