def ASTFactory(parseTree):
    pass

class ASTBase:
    def __init__(self):
        self.children = []

    def createAST(self, parseTree):
        for child in parseTree.children:
            pass

class ASTPrimaryExpression(ASTBase):
    def __init__(self):
        super(ASTPrimaryExpression, self).__init__()
