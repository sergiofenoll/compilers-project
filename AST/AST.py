def CTypeToLLVMType(CType):

    if CType == "int":
        return "i32"
    elif CType == "char":
        return "i8"
    else:
        return CType


def generate_llvm_expr(node, op):
    llvmir = ""
    llvm_type = CTypeToLLVMType(node.type())

    if isinstance(node.left(), ASTExpressionNode) and not isinstance(node.right(), ASTExpressionNode):
        lhs = f"%{node.scope.temp_register}"
    elif not isinstance(node.left(), ASTExpressionNode) and isinstance(node.right(), ASTExpressionNode):
        rhs = f"%{node.scope.temp_register}"
    elif isinstance(node.left(), ASTExpressionNode) and isinstance(node.right(), ASTExpressionNode):
        lhs = f"%{node.scope.temp_register - 2}"
        rhs = f"%{node.scope.temp_register}"

    if isinstance(node.left(), ASTConstantNode):
        lhs = node.left().value()
    elif isinstance(node.left(), ASTIdentifierNode):
        # LHS should contain dereferenced value of the variable
        node.scope.temp_register += 1
        ID_register = node.scope.lookup(node.left().identifier).register
        lhs = f"%{node.scope.temp_register}"
        llvmir += f"{lhs} = load {llvm_type}, {llvm_type}* {ID_register}\n"

    if isinstance(node.right(), ASTConstantNode):
        rhs = node.right().value()
    elif isinstance(node.right(), ASTIdentifierNode):
        # RHS should contain dereferenced value of the variable
        node.scope.temp_register += 1
        ID_register = node.scope.lookup(node.left().identifier).register
        rhs = f"%{node.scope.temp_register}"
        llvmir += f"{rhs} = load {llvm_type}, {llvm_type}* {ID_register}\n"

    node.scope.temp_register += 1
    llvmir += f"%{node.scope.temp_register} = {op} {llvm_type} {lhs}, {rhs}\n"
    return llvmir


class ASTBaseNode:
    def __init__(self, name=None, scope=None):
        self.parent = None
        self.children = []
        self.scope = scope
        self.name = name or type(self).__name__

        # Maintenance variable for dotfile generation
        self.__num = 0

    def generateLLVMIRPrefix(self):
        return ""

    def generateLLVMIRPostfix(self):
        return ""

    def _generateLLVMIR(self):
        return ""

    def generateMIPS(self):
        return ""

    def optimise(self):
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

    def type(self):
        return None

    def value(self):
        return None


class ASTIdentifierNode(ASTBaseNode):
    def __init__(self, value):
        super(ASTIdentifierNode, self).__init__()
        self.identifier = value
        self.name = "Identifier:" + str(value)

    def _generateLLVMIR(self):
        if not isinstance(self.parent, ASTParameterTypeList):
            symbol_table_entry = self.scope.lookup(self.identifier)
            scope = self.scope.scope_level(self.identifier)
            register = symbol_table_entry.register
            if not register:
                if scope == 0:
                    register = f"@{self.identifier}"
                    symbol_table_entry.register = register
                else:
                    register = f"%{self.identifier}.scope{scope}"
                    symbol_table_entry.register = register
            return register

    def optimise(self):
        # If value known from Symbol Table, remove declaration & swap uses with constant value

        # Lookup identifier in accessible scopes
        STEntry = self.scope.lookup(self.identifier)
        if STEntry and STEntry.value:
            if isinstance(self.parent, ASTAssignmentNode) and self.parent.left() == self:
                return
            if isinstance(self.parent, ASTDeclarationNode):
                # Delete declaration
                pass
            else:
                # Replace with constant node
                new_node = ASTConstantNode(STEntry.value, STEntry.type_desc)
                new_node.parent = self.parent
                new_node.scope = self.scope

                current_idx = self.parent.children.index(self)
                self.parent.children.pop(current_idx)
                self.parent.children.insert(current_idx, new_node)
                self = new_node

    def type(self):
        try:
            return self.scope.lookup(self.identifier).type_desc
        except AttributeError:
            return None

    def value(self):
        try:
            return self.scope.lookup(self.identifier).value
        except AttributeError:
            return None


class ASTConstantNode(ASTBaseNode):
    def __init__(self, value, type_specifier):
        super(ASTConstantNode, self).__init__()
        self.__value = value
        self.type_specifier = type_specifier
        self.name = "Constant:" + str(value)

    def type(self):
        return self.type_specifier

    def value(self):
        return self.__value


class ASTStringLiteralNode(ASTBaseNode):
    def __init__(self, value):
        super(ASTStringLiteralNode, self).__init__()
        self.__value = value
        self.name = "String literal:" + str(value.replace('"', '\\"'))

    def type(self):
        return "char*"

    def value(self):
        return self.__value


class ASTExpressionNode(ASTBaseNode):
    def __init__(self):
        super(ASTExpressionNode, self).__init__()


class ASTUnaryExpressionNode(ASTExpressionNode):
    def __init__(self):
        super(ASTUnaryExpressionNode, self).__init__()
        self.value = None

    def identifier(self):
        return self.children[0]

    def type(self):
        return self.identifier().type()


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

    def value(self):
        return self.identifier().value()


class ASTUnaryMinusNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTUnaryMinusNode, self).__init__()
        self.name = "-"

    def type(self):
        if "*" in self.identifier().type():
            # TODO: Error, cannot apply unary minus operator to pointer
            print("Error: cannot apply unary minus operator to pointer")
            exit()
        else:
            return self.identifier().type()

    def value(self):
        id_value = self.identifier().value()
        if id_value:
            type_desc = self.type()
            if type_desc == "char":
                return chr(-ord(id_value) % 256)
            else:
                return -id_value
        return None


class ASTLogicalNotNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTLogicalNotNode, self).__init__()
        self.name = "!"

    def value(self):
        id_value = self.identifier().value()
        if id_value:
            type_desc = self.type()
            if type_desc == "char":
                return chr(0) if ord(id_value) != 0 else chr(1)
            elif type_desc == "float":
                return 0.0 if id_value != 0.0 else 1
            else:
                return 0 if id_value != 0 else 1
        return None


class ASTIndirection(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTIndirection, self).__init__()

    def type(self):
        if "*" not in self.identifier().type():
            # TODO: Error, cannot apply indirection operator to not pointer
            print("Error: cannot apply indirection operator to not pointer")
            exit()
        else:
            return self.identifier().type()[:-1]


class ASTCastNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTCastNode, self).__init__()

    def identifier(self):
        return self.children[1]

    def type(self):
        if "*" in self.children[0].type():
            # TODO: Error, cannot cast to pointer type
            print("ERROR: cannot cast to pointer type")
            exit()
        else:
            return self.children[0].type()

    def value(self):
        id_value = self.identifier().value()
        if id_value:
            type_desc = self.type()
            if type_desc == "char":
                return chr(ord(id_value) % 256)
            elif type_desc == "float":
                return float(id_value)
            else:
                return int(id_value)
        return None


class ASTBinaryExpressionNode(ASTExpressionNode):
    def __init__(self, c_idx = None):
        super(ASTBinaryExpressionNode, self).__init__()
        self.c_idx = c_idx

    def left(self):
        return self.children[0]

    def right(self):
        return self.children[1]

    def type(self):
        lhs_type = self.left().type()
        rhs_type = self.right().type()
        if lhs_type == rhs_type:
            return lhs_type
        elif lhs_type == 'float' or rhs_type == 'float':
            return 'float'
        elif lhs_type == 'int' or rhs_type == 'int':
            return 'int'


class ASTAssignmentNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAssignmentNode, self).__init__()
        self.name = "="

    def type(self):
        return self.left().type()

    def value(self):
        return self.right().value()

    def generateLLVMIRPostfix(self):
        identifier_name = self.left()._generateLLVMIR()
        llvm_type = CTypeToLLVMType(self.type())
        if isinstance(self.right(), ASTConstantNode):
            return f"store {llvm_type} {self.right().value()}, {llvm_type}* {identifier_name}\n"
        else:
            last_temp_register = self.scope.temp_register
            return f"store {llvm_type} %{last_temp_register}, {llvm_type}* {identifier_name}\n"


class ASTMultiplicationNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx):
        super(ASTMultiplicationNode, self).__init__(c_idx)
        self.name = "*"

    def value(self):
        if self.left().value() and self.right().value():
            return self.left().value() * self.right().value()

    def optimise(self):
        # Handles multiplication by 1 and 0

        rhs = int(self.right().value()) if isinstance(self.right(), ASTConstantNode) else None
        lhs = int(self.left().value()) if isinstance(self.left(), ASTConstantNode) else None

        if rhs == 0 or lhs == 0:
            # Evaluates to 0
            new_node = ASTConstantNode(0, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            self.parent.children.pop(self.c_idx)
            self.parent.children.insert(self.c_idx, new_node)
            self = new_node

        elif rhs == 1:
            # Evaluates to lhs
            self.parent.children.pop(self.c_idx)
            self.parent.children.insert(self.c_idx, self.left())
            self = None
        
        elif lhs == 1:
            # Evaluaties to rhs
            self.parent.children.pop(self.c_idx)
            self.parent.children.insert(self.c_idx, self.right())
            self = None

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fmul" if self.type() == "float" else "mul")


class ASTDivisionNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx):
        super(ASTDivisionNode, self).__init__(c_idx)
        self.name = "/"

    def optimise(self):
        # Handles division by 1 and, if possible, division by 0

        value = self.right().value()
        if value and int(value) == 1:
            # This entire division will evaluate to the lhs
            self.parent.children.pop(self.c_idx)
            self.parent.children.insert(self.c_idx, self.left())
            self = None
        elif value and int(value) == 0:
            # Division by 0: warn user
            print("[WARNING] Division by 0.")

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fdiv" if self.type() == "float" else "sdiv")


class ASTModuloNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx):
        super(ASTModuloNode, self).__init__(c_idx)
        self.name = "%"

    def optimise(self):

        value = self.right().value()
        if value and int(value) == 1:
            # Always returns 0, so replace with constant
            new_node = ASTConstantNode(0)
            new_node.parent = self.parent
            new_node.scope = self.scope
            self.parent.children.pop(self.c_idx)
            self.parent.children.insert(self.c_idx, new_node)
            self = new_node

    def type(self):
        if self.left().type() == "float" or self.right().type() == "float":
            print("Can't do modulo on floating types")
            exit()

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "srem")


class ASTAdditionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAdditionNode, self).__init__()
        self.name = "+"

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fadd" if self.type() == "float" else "add")


class ASTSubtractionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSubtractionNode, self).__init__()
        self.name = "-"

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fsub" if self.type() == "float" else "sub")


class ASTSmallerThanNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSmallerThanNode, self).__init__()
        self.name = "<"

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fcmp olt" if self.type() == "float" else "icmp slt")


class ASTLargerThanNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLargerThanNode, self).__init__()
        self.name = ">"

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fcmp ogt" if self.type() == "float" else "icmp sgt")


class ASTSmallerThanOrEqualNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSmallerThanOrEqualNode, self).__init__()
        self.name = "<="

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fcmp ole" if self.type() == "float" else "icmp sle")


class ASTLargerThanOrEqualNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLargerThanOrEqualNode, self).__init__()
        self.name = ">="

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fcmp oge" if self.type() == "float" else "icmp sge")


class ASTEqualsNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTEqualsNode, self).__init__()
        self.name = "=="

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fcmp oeq" if self.type() == "float" else "icmp eq")


class ASTNotEqualsNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTNotEqualsNode, self).__init__()
        self.name = "!="

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "fcmp one" if self.type() == "float" else "icmp ne")


class ASTLogicalAndNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLogicalAndNode, self).__init__()
        self.name = "&&"

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "and")


class ASTLogicalOrNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLogicalOrNode, self).__init__()
        self.name = "||"

    def generateLLVMIRPostfix(self):
        return generate_llvm_expr(self, "or")


class ASTDeclarationNode(ASTBaseNode):
    def __init__(self, c_idx = None):
        super(ASTDeclarationNode, self).__init__()
        self.name = "Decl"
        self.c_idx = c_idx

    def generateLLVMIRPrefix(self):

        # Allocate new register
        register = self.children[1]._generateLLVMIR()
        return f"{register} = alloca {self.children[0]._generateLLVMIR()}\n"  # Identifier

    def generateLLVMIRPostfix(self):
        last_temp_register = self.scope.temp_register
        llvm_ir = ""
        identifier_name = self.identifier()._generateLLVMIR()
        llvm_type = CTypeToLLVMType(self.type())
        if len(self.children) > 2:
            value_node = self.children[2]
            if isinstance(value_node, ASTConstantNode):
                value = value_node.value()
            else:
                value = "%" + str(last_temp_register)
        else:
            # Initialise this to 0 by default
            if llvm_type == "i32" or llvm_type == "i8":
                value = "0"
            elif llvm_type == "float":
                value = "0.000000e+00"
        # Store value (expression or constant) in register
        llvm_ir += f"store {llvm_type} {value}, {llvm_type}* {identifier_name}\n"
                

        return llvm_ir

    def optimise(self):
        # Prune declarations for unused variables
        STEntry = self.scope.lookup(self.identifier().value)
        if STEntry and not STEntry.used:
            # self.parent.children.pop(self.c_idx)
            # NOTE: Above doesn't work when previous children have been popped because c_idx is no longer correct
            self.parent.children.pop(self.parent.children.index(self))
            self = None

    def type(self):
        return self.children[0].type()

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
        self.cond_register = None
        self.true_label = None
        self.false_label = None
        self.finish_label = None

    def generateLLVMIRPostfix(self):

        llvmir = f"\n{self.finish_label}:\n"
        return llvmir


class ASTIfConditionNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfConditionNode, self).__init__()
        self.name = "IfCond"

    def generateLLVMIRPostfix(self):
        cond_register = self.scope.temp_register
        self.parent.cond_register = f"%{cond_register}"
        self.parent.true_label = f"IfTrue{cond_register}"
        self.parent.false_label = f"IfFalse{cond_register}" 
        self.parent.finish_label = f"IfEnd{cond_register}"

        llvmir = f"br i1 {self.parent.cond_register}, label %{self.parent.true_label}, label %{self.parent.false_label}\n"
        return llvmir


class ASTIfTrueNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfTrueNode, self).__init__()
        self.name = "IfTrue"

    def generateLLVMIRPrefix(self):

        llvmir = f"\n{self.parent.true_label}:\n"
        return llvmir

    def generateLLVMIRPostfix(self):

        llvmir = f"br label %{self.parent.finish_label}\n"
        return llvmir


class ASTIfFalseNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfFalseNode, self).__init__()
        self.name = "IfFalse"

    def generateLLVMIRPrefix(self):

        llvmir = f"\n{self.parent.false_label}:\n"
        return llvmir

    def generateLLVMIRPostfix(self):

        llvmir = f"br label %{self.parent.finish_label}\n"
        return llvmir


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


class ASTGotoNode(ASTBaseNode):
    def __init__(self):
        super(ASTGotoNode, self).__init__()


class ASTContinueNode(ASTBaseNode):
    def __init__(self, c_idx = None):
        super(ASTContinueNode, self).__init__()
        self.c_idx = c_idx
    
    def optimise(self):
        # Prune siblings that come after this continue
        if self.c_idx is not None:
            self.parent.children = self.parent.children[:self.c_idx+1]


class ASTBreakNode(ASTBaseNode):
    def __init__(self, c_idx = None):
        super(ASTBreakNode, self).__init__()
        self.c_idx = c_idx
    
    def optimise(self):
        # Prune siblings that come after this break
        if self.c_idx is not None:
            self.parent.children = self.parent.children[:self.c_idx+1]


class ASTReturnNode(ASTBaseNode):
    def __init__(self, c_idx):
        super(ASTReturnNode, self).__init__()
        self.c_idx = c_idx

    def generateLLVMIRPostfix(self):

        llvmir = ""
        return_value = ""
        return_type = CTypeToLLVMType(self.children[0].type())
        if isinstance(self.children[0], ASTConstantNode):
            return_value = self.children[0].value()
        elif isinstance(self.children[0], ASTIdentifierNode):
            ID_node = self.children[0]
            # Load dereferenced value into temp register
            self.scope.temp_register += 1
            id_register = ID_node.scope.lookup(ID_node.identifier).register
            llvmir += f"%{self.scope.temp_register} = load {return_type}, {return_type}* {id_register}\n"
            return_value = f"%{self.scope.temp_register}"
        else:
            return_value = self.children[0].scope.temp_register
        
        llvmir += f"ret {return_type} {return_value}\n"
        return llvmir

    def optimise(self):
        # Prune siblings that come after this return
        if self.c_idx is not None:
            self.parent.children = self.parent.children[:self.c_idx+1]


class ASTCompoundStmtNode(ASTBaseNode):
    def __init__(self):
        super(ASTCompoundStmtNode, self).__init__()
        self.name = "CompoundStmt"


class ASTFunctionDefinitionNode(ASTBaseNode):
    def __init__(self):
        super(ASTFunctionDefinitionNode, self).__init__()
        self.name = "FuncDef"

    def generateLLVMIRPrefix(self):
        type_specifier = self.returnType()._generateLLVMIR()
        identifier_name = self.identifier()._generateLLVMIR()
        has_params = isinstance(self.children[2], ASTParameterTypeList)
        if has_params:
            args = self.children[2]
            arg_list = args._generateLLVMIR()
            arg_decl = ""
            argc = len(args.children) // 2
            self.scope.temp_register = argc + 1
            for i, (type_node, identifier_node) in enumerate(zip(args.children[0::2], args.children[1::2])):
                type_spec = CTypeToLLVMType(type_node.type())
                arg_decl += f"%{self.scope.temp_register} = alloca {type_spec}\n"
                arg_decl += f"store {type_spec} %{i}, {type_spec}* %{self.scope.temp_register}\n"
                self.scope.lookup(identifier_node.identifier).register = f"%{self.scope.temp_register}"
                self.scope.temp_register += 1
        else:
            arg_list = "()"
            arg_decl = ""

        return f"define {type_specifier} {identifier_name} {arg_list} {{\n{arg_decl}"

    def generateLLVMIRPostfix(self):
        return "}\n"

    def returnType(self):
        return self.children[0]

    def identifier(self):
        return self.children[1]

    def arguments(self):
        if isinstance(self.children[2], ASTCompoundStmtNode):
            return []
        else:
            return self.children[2].children


class ASTParameterTypeList(ASTBaseNode):
    def __init__(self):
        super(ASTParameterTypeList, self).__init__()
        self.name = "ParamList"

    def _generateLLVMIR(self):

        llvmir = "("

        for type_child in self.children[::2]:
            llvmir += type_child._generateLLVMIR() + ", "
        
        llvmir = llvmir[:-2]
        llvmir += ")"
        return llvmir


class ASTTypeSpecifierNode(ASTBaseNode):
    def __init__(self, tspec):
        super(ASTTypeSpecifierNode, self).__init__()
        self.tspec = tspec
        self.name = "Type:" + str(tspec)

    def _generateLLVMIR(self):

        llvmir = CTypeToLLVMType(self.tspec)
        return llvmir

    def type(self):
        return self.tspec


class ASTExprListNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTExprListNode, self).__init__(name)
