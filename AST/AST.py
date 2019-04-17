class ASTBaseNode:
    def __init__(self, name=""):
        self.parent = None
        self.children = []
        self.name = name
        self.scope = None

    def generateLLVMIR(self):
        pass

    def generateMIPS(self):
        pass


class ASTScopedNode(ASTBaseNode):
    def __init__(self):
        super(ASTScopedNode, self).__init__()
        # Make new scope


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


class ASTUnaryOpNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTUnaryOpNode, self).__init__(name)


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
