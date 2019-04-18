class ASTBaseNode:
    def __init__(self, name=None, scope=None):
        self.parent = None
        self.children = []
        self.scope = scope
        self.name = name or type(self).__name__

        # Maintenance variable for dotfile generation
        self.__num = 0

    def generateLLVMIR(self):
        pass

    def generateMIPS(self):
        pass

    def generateDot(self, output):
        output.write("""\
        digraph astgraph {
          node [shape=none, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]
        """)
        ncount = 1
        queue = list()
        queue.append(self)
        output.write('  node{} [label="{}"]\n'.format(ncount, self.name))
        self.__num = ncount
        ncount += 1
        while queue:
            node = queue.pop(0)
            for child in node.children:
                output.write('  node{} [label="{}"]\n'.format(ncount, child.name))
                child.__num = ncount
                ncount += 1
                output.write('  node{} -> node{}\n'.format(node.__num, child.__num))
                queue.append(child)

        output.write("}")


class ASTIdentifierNode(ASTBaseNode):
    def __init__(self, value):
        super(ASTIdentifierNode, self).__init__()
        self.value = value
        self.name = "Identifier:" + str(value)


class ASTConstantNode(ASTBaseNode):
    def __init__(self, value):
        super(ASTConstantNode, self).__init__()
        self.value = value
        self.name = "Constant:" + str(value)


class ASTStringLiteralNode(ASTBaseNode):
    def __init__(self, value):
        super(ASTStringLiteralNode, self).__init__()
        self.value = value
        self.name = "String literal:" + str(value)


class ASTUnaryExpressionNode(ASTBaseNode):
    def __init__(self):
        super(ASTUnaryExpressionNode, self).__init__()

    def identifier(self):
        return self.children[0]


class ASTArrayAccessNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTArrayAccessNode, self).__init__()
        self.name = "[]"

    def indexer(self):
        return self.children[1]


class ASTFunctionCallNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTFunctionCallNode, self).__init__()
        self.name = "()"

    def arguments(self):
        return self.children[1]


class ASTPostfixIncrementNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTPostfixIncrementNode, self).__init__()
        self.name = "post++"


class ASTPostfixDecrementNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTPostfixDecrementNode, self).__init__()
        self.name = "post--"


class ASTPrefixIncrementNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTPrefixIncrementNode, self).__init__()
        self.name = "pre++"


class ASTPrefixDecrementNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTPrefixDecrementNode, self).__init__()
        self.name = "pre--"


class ASTUnaryPlusNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTUnaryPlusNode, self).__init__()
        self.name = "+"


class ASTUnaryMinusNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTUnaryMinusNode, self).__init__()
        self.name = "-"


class ASTLogicalNotNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTLogicalNotNode, self).__init__()
        self.name = "!"


class ASTIndirection(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTIndirection, self).__init__()


class ASTCastNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTCastNode, self).__init__()


class ASTBinaryExpressionNode(ASTBaseNode):
    def __init__(self):
        super(ASTBinaryExpressionNode, self).__init__()

    def left(self):
        return self.children[0]

    def right(self):
        return self.children[1]


class ASTAssignmentNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAssignmentNode, self).__init__()
        self.name = "="


class ASTMultiplicationNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTMultiplicationNode, self).__init__()
        self.name = "*"


class ASTDivisionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTDivisionNode, self).__init__()
        self.name = "/"


class ASTModuloNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTModuloNode, self).__init__()
        self.name = "%"


class ASTAdditionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAdditionNode, self).__init__()
        self.name = "+"


class ASTSubtractionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSubtractionNode, self).__init__()
        self.name = "-"


class ASTSmallerThanNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSmallerThanNode, self).__init__()
        self.name = "<"


class ASTLargerThanNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLargerThanNode, self).__init__()
        self.name = ">"


class ASTSmallerThanOrEqualNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSmallerThanOrEqualNode, self).__init__()
        self.name = "<="


class ASTLargerThanOrEqualNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLargerThanOrEqualNode, self).__init__()
        self.name = ">="


class ASTEqualsNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTEqualsNode, self).__init__()
        self.name = "=="


class ASTNotEqualsNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTNotEqualsNode, self).__init__()
        self.name = "!="


class ASTLogicalAndNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLogicalAndNode, self).__init__()
        self.name = "&&"


class ASTLogicalOrNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLogicalOrNode, self).__init__()
        self.name = "||"


class ASTDeclarationNode(ASTBaseNode):
    def __init__(self):
        super(ASTDeclarationNode, self).__init__()
        self.name = "Decl"

    def type(self):
        return self.children[0]

    def identifier(self):
        return self.children[1]

    def initializer(self):
        try:
            return self.children[2]
        except IndexError:
            return None


class ASTLabelStmtNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTLabelStmtNode, self).__init__(name)


class ASTCaseStmtNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTCaseStmtNode, self).__init__(name)


class ASTDefaultStmtNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTDefaultStmtNode, self).__init__(name)


class ASTIfStmtNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfStmtNode, self).__init__()
        self.name = "If"


class ASTSwitchStmtNode(ASTBaseNode):
    def __init__(self):
        super(ASTSwitchStmtNode, self).__init__()
        self.name = "Switch"


class ASTWhileStmtNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTWhileStmtNode, self).__init__(name)


class ASTForStmtNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTForStmtNode, self).__init__(name)


class ASTJumpStmtNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTJumpStmtNode, self).__init__(name)


class ASTCompoundStmtNode(ASTBaseNode):
    def __init__(self):
        super(ASTCompoundStmtNode, self).__init__()
        self.name = "{}"


class ASTFunctionDefinitionNode(ASTBaseNode):
    def __init__(self):
        super(ASTFunctionDefinitionNode, self).__init__()
        self.name = "FuncDef"

    def returnType(self):
        return self.children[0]

    def identifier(self):
        return self.children[1]

    def arguments(self):
        if isinstance(self.children[2], ASTCompoundStmtNode):
            return []
        else:
            return self.children[2].children


class ASTTypeSpecifierNode(ASTBaseNode):
    def __init__(self, tspec):
        super(ASTTypeSpecifierNode, self).__init__()
        self.tspec = tspec
        self.name = "Type:" + str(tspec)


class ASTExprListNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTExprListNode, self).__init__(name)
