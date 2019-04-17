class ASTBaseNode:
    def __init__(self, name=None, scope=None):
        self.parent = None
        self.children = []
        self.scope = scope
        self.name = name or type(self).__name__

    def generateLLVMIR(self):
        pass

    def generateMIPS(self):
        pass


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


class ASTArrayAccessNode(ASTBaseNode):
    def __init__(self):
        super(ASTArrayAccessNode, self).__init__()
        self.name = "[]"


class ASTFunctionCallNode(ASTBaseNode):
    def __init__(self):
        super(ASTFunctionCallNode, self).__init__()
        self.name = "()"


class ASTPostfixIncrementNode(ASTBaseNode):
    def __init__(self):
        super(ASTPostfixIncrementNode, self).__init__()
        self.name = "post++"


class ASTPostfixDecrementNode(ASTBaseNode):
    def __init__(self):
        super(ASTPostfixDecrementNode, self).__init__()
        self.name = "post--"


class ASTPrefixIncrementNode(ASTBaseNode):
    def __init__(self):
        super(ASTPrefixIncrementNode, self).__init__()
        self.name = "pre++"


class ASTPrefixDecrementNode(ASTBaseNode):
    def __init__(self):
        super(ASTPrefixDecrementNode, self).__init__()
        self.name = "pre--"


class ASTUnaryPlusNode(ASTBaseNode):
    def __init__(self):
        super(ASTUnaryPlusNode, self).__init__()
        self.name = "+"


class ASTUnaryMinusNode(ASTBaseNode):
    def __init__(self):
        super(ASTUnaryMinusNode, self).__init__()
        self.name = "-"


class ASTLogicalNot(ASTBaseNode):
    def __init__(self):
        super(ASTLogicalNot, self).__init__()
        self.name = "!"


class ASTIndirection(ASTBaseNode):
    def __init__(self):
        super(ASTIndirection, self).__init__()


class ASTCastNode(ASTBaseNode):
    def __init__(self):
        super(ASTCastNode, self).__init__()


class ASTAssignmentNode(ASTBaseNode):
    def __init__(self):
        super(ASTAssignmentNode, self).__init__()


class ASTMultiplicationNode(ASTBaseNode):
    def __init__(self):
        super(ASTMultiplicationNode, self).__init__()


class ASTDivisionNode(ASTBaseNode):
    def __init__(self):
        super(ASTDivisionNode, self).__init__()


class ASTModuloNode(ASTBaseNode):
    def __init__(self):
        super(ASTModuloNode, self).__init__()


class ASTAdditionNode(ASTBaseNode):
    def __init__(self):
        super(ASTAdditionNode, self).__init__()


class ASTSubtractionNode(ASTBaseNode):
    def __init__(self):
        super(ASTSubtractionNode, self).__init__()


class ASTSmallerThanNode(ASTBaseNode):
    def __init__(self):
        super(ASTSmallerThanNode, self).__init__()


class ASTLargerThanNode(ASTBaseNode):
    def __init__(self):
        super(ASTLargerThanNode, self).__init__()


class ASTSmallerThanOrEqualNode(ASTBaseNode):
    def __init__(self):
        super(ASTSmallerThanOrEqualNode, self).__init__()


class ASTBinaryOpNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTBinaryOpNode, self).__init__(name)


class ASTDeclarationNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTDeclarationNode, self).__init__(name)


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
    def __init__(self, name):
        super(ASTIfStmtNode, self).__init__(name)


class ASTSwitchStmtNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTSwitchStmtNode, self).__init__(name)


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
    def __init__(self, name):
        super(ASTCompoundStmtNode, self).__init__(name)


class ASTFunctionDefinitionNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTFunctionDefinitionNode, self).__init__(name)


class ASTTypeSpecifierNode(ASTBaseNode):
    def __init__(self, tspec):
        super(ASTTypeSpecifierNode, self).__init__()
        self.tspec = tspec
        self.name = "Type:" + str(tspec)


class ASTExprListNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTExprListNode, self).__init__(name)
