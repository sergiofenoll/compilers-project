import struct


def c2llvm_type(c_type):
    if "int" in c_type:
        ir_type = "i32" + "*" * c_type.count("*")
    elif "char" in c_type:
        ir_type ="i8" + "*" * c_type.count("*")
    elif "bool" in c_type:
        ir_type = "i1"
    else:
        ir_type = c_type + "*" * c_type.count("*")
    return ir_type


def hexify_float(f):
    # Truncate float to single precision, then convert to a double precision hexstring
    # #JustLLVMIRThings
    single_prec = struct.unpack('f', struct.pack('f', f))[0]
    double_prec = struct.unpack('<Q', struct.pack('<d', single_prec))[0]
    return hex(double_prec)


def get_expression_type(node):
    # Gets a node's type given its left & right child
    l_type = node.left().type()
    r_type = node.right().type()

    if l_type == "float" or r_type == "float":
        return "float"
    elif l_type == "int" or r_type == "int":
        return "int"
    elif l_type == "char" or r_type == "char":
        return "char"
    elif l_type == "bool" or r_type == "bool":
        return "bool"

def generate_llvm_expr(node, op):
    llvmir = ""
    expr_type = get_expression_type(node)
    llvm_type = c2llvm_type(expr_type)

    # Determine lhs and rhs in the operation
    l_child = node.left()
    l_type = l_child.type()
    r_child = node.right()
    r_type = r_child.type()

    # Set up 'naive' lhs & rhs using NodeType
    if isinstance(node.left(), ASTExpressionNode) and not isinstance(node.right(), ASTExpressionNode):
        lhs = f"%{node.scope.temp_register}"
    elif not isinstance(node.left(), ASTExpressionNode) and isinstance(node.right(), ASTExpressionNode):
        rhs = f"%{node.scope.temp_register}"
    elif isinstance(node.left(), ASTExpressionNode) and isinstance(node.right(), ASTExpressionNode):
        lhs = f"%{node.scope.temp_register - 2}"
        rhs = f"%{node.scope.temp_register}"

    if isinstance(node.left(), ASTConstantNode):
        lhs = node.left().llvm_value()
    elif isinstance(node.left(), ASTIdentifierNode):
        # LHS should contain dereferenced value of the variable
        ID_register = node.scope.lookup(node.left().identifier).register
        lhs = f"%{node.scope.temp_register}"
        lhs_type = c2llvm_type(l_type)
        llvmir += f"{lhs} = load {lhs_type}, {lhs_type}* {ID_register}\n"
        node.scope.temp_register += 1

    if isinstance(node.right(), ASTConstantNode):
        rhs = node.right().llvm_value()
    elif isinstance(node.right(), ASTIdentifierNode):
        # RHS should contain dereferenced value of the variable
        ID_register = node.scope.lookup(node.left().identifier).register
        rhs = f"%{node.scope.temp_register}"
        rhs_type = c2llvm_type(r_type)
        llvmir += f"{rhs} = load {rhs_type}, {rhs_type}* {ID_register}\n"
        node.scope.temp_register += 1

    # Account for implicit conversions
    if l_type != expr_type:
        # Cast & update lhs
        llvmir += generate_llvm_impl_cast(l_child, lhs, llvm_type)
        lhs = f"%{l_child.scope.temp_register-1}"
    elif r_type != expr_type:
        # Cast & update rhs
        llvmir += generate_llvm_impl_cast(r_child, rhs, llvm_type)
        rhs = f"%{r_child.scope.temp_register-1}"

    llvmir += f"%{node.scope.temp_register} = {op} {llvm_type} {lhs}, {rhs}\n"
    node.scope.temp_register += 1
    return llvmir

def generate_llvm_impl_cast(origin_node, origin_register, dest_type):
    # Handles implicit cast to destination type

    llvmir = ""
    origin_type = c2llvm_type(origin_node.type())
    cast_instruction = ""

    if not (origin_type == "float" or dest_type == "float"):
        cast_instruction = "zext"
    elif origin_type == "float" and dest_type == "i32":
        cast_instruction = "fptosi"
    elif origin_type == "i32" and dest_type == "float":
        cast_instruction = "sitofp"
    elif origin_type == "i8" and dest_type == "float":
        # First convert to i32
        llvmir += f"%{origin_node.scope.temp_register} = sext i8 {origin_register} to i32\n"
        origin_register = f"%{origin_node.scope.temp_register}"
        origin_node.scope.temp_register += 1
        cast_instruction = "sitofp"

    dest_register = f"%{origin_node.scope.temp_register}"   
    llvmir += f"{dest_register} = {cast_instruction} {origin_type} {origin_register} to {dest_type}\n"
    origin_node.scope.temp_register += 1
    return llvmir


class ASTBaseNode:
    def __init__(self, name=None, scope=None):
        self.parent = None
        self.children = []
        self.scope = scope
        self.name = name or type(self).__name__

        # Maintenance variable for dotfile generation
        self.__num = 0

    def enter_llvm_data(self):
        return ""

    def exit_llvm_data(self):
        return ""

    def enter_llvm_text(self):
        return ""

    def exit_llvm_text(self):
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


class ASTCompilationUnitNode(ASTBaseNode):
    def __init__(self, includes_stdio=False):
        super(ASTCompilationUnitNode, self).__init__()
        self.name = "Root"
        self.includes_stdio = includes_stdio

    def enter_llvm_text(self):
        if self.includes_stdio:
            return "declare i32 @printf(i8*, ...)\ndeclare i32 @scanf(i8*, ...)\n"
        else:
            return ""


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

    def llvm_value(self):
        if self.type_specifier == "float":
            return hexify_float(self.__value)
        else:
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

    def enter_llvm_data(self):
        def clean_string(s):
            def escape_seq_to_hex(char):
                hexed_char = hex(ord(char))
                hexed_char = hexed_char.replace("0x", "")
                if len(hexed_char) == 1:
                    hexed_char = "0" + hexed_char
                return "\\" + hexed_char
            mapper = {
                "\\a": escape_seq_to_hex("\a"),
                "\\b": escape_seq_to_hex("\b"),
                "\\f": escape_seq_to_hex("\f"),
                "\\n": escape_seq_to_hex("\n"),
                "\\r": escape_seq_to_hex("\r"),
                "\\t": escape_seq_to_hex("\t"),
                "\\v": escape_seq_to_hex("\v"),
                "\\'": escape_seq_to_hex("\'"),
                "\\\"": escape_seq_to_hex("\""),
            }
            s = s.replace("\"", "")
            s_len = len(s)
            slash_indices = [i for i, c in enumerate(s) if c == "\\"]
            for slash in slash_indices[::-1]:
                escape_sequence = s[slash:slash + 2]
                if escape_sequence in mapper:
                    s_len -= 1 * s.count(escape_sequence)
                    s = s.replace(escape_sequence, mapper[escape_sequence])
                else:
                    s = s[:slash] + "\\22" + s[slash:]
            return s, s_len

        register = self.scope.temp_register
        cleaned_string, length = clean_string(self.__value)
        self.scope.temp_register += 1
        return f'@{register} = private unnamed_addr constant [{length + 1} x i8] c"{cleaned_string}\00"\n'


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

    def exit_llvm_text(self):
        symbol_table_entry = self.scope.lookup(self.identifier().identifier)
        array_member_type = c2llvm_type(self.type())
        array_type = self.scope.lookup(self.identifier().identifier).aux_type
        array_register = symbol_table_entry.register
        if isinstance(self.indexer(), ASTConstantNode):
            idx = self.indexer().llvm_value()
        else:
            idx = self.scope.temp_register
        llvm_ir = f"%{self.scope.temp_register} = getelementptr {array_type}, {array_type}* {array_register}, i32 0, i32 {idx}\n"
        temp_reg = self.scope.temp_register
        self.scope.temp_register += 1
        llvm_ir += f"%{self.scope.temp_register} = load {array_member_type}, {array_member_type}* %{temp_reg}\n"
        return llvm_ir


class ASTFunctionCallNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTFunctionCallNode, self).__init__()
        self.name = "()"

    def arguments(self):
        return self.children[1:]

    def enter_llvm_text(self):
        return ""

    def exit_llvm_text(self):
        register = self.scope.temp_register
        self.scope.temp_register += 1

        function_register = self.scope.lookup(self.identifier().identifier).register
        function_type = c2llvm_type(self.type())

        arguments = list()
        expr_arg_count = sum(isinstance(x, ASTExpressionNode) for x in self.arguments())
        expr_idx = 0
        for arg in self.arguments():
            tspec = c2llvm_type(arg.type())
            if isinstance(arg, ASTConstantNode):
                arguments.append(f"{tspec} {arg.llvm_value()}")
            elif isinstance(arg, ASTIdentifierNode):
                entry = self.scope.lookup(arg.identifier)
                arguments.append(f"{tspec} {entry.register}")
            elif isinstance(arg, ASTExpressionNode):
                arguments.append(f"{tspec} %{register - expr_arg_count + expr_idx}")
                expr_idx += 1

        return f"%{register} = call {function_type} {function_register}({', '.join(arguments)})\n"


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
        return get_expression_type(self)


class ASTAssignmentNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAssignmentNode, self).__init__()
        self.name = "="

    def type(self):
        return self.left().type()

    def value(self):
        return self.right().value()

    def exit_llvm_text(self):
        identifier_name = self.left()._generateLLVMIR()
        llvm_type = c2llvm_type(self.type())
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

    def exit_llvm_text(self):
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

    def exit_llvm_text(self):
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

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "srem")


class ASTAdditionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAdditionNode, self).__init__()
        self.name = "+"

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fadd" if self.type() == "float" else "add")


class ASTSubtractionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSubtractionNode, self).__init__()
        self.name = "-"

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fsub" if self.type() == "float" else "sub")


class ASTLogicalNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTLogicalNode, self).__init__()
        self.name = "LogicalNode"

    def type(self):
        return "bool"

    def float_op(self):
        result = ("float" in self.left().type()) or ("float" in self.right().type())
        return result


class ASTSmallerThanNode(ASTLogicalNode):
    def __init__(self):
        super(ASTSmallerThanNode, self).__init__()
        self.name = "<"

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp olt" if self.float_op() else "icmp slt")


class ASTLargerThanNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLargerThanNode, self).__init__()
        self.name = ">"

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp ogt" if self.float_op() else "icmp sgt")


class ASTSmallerThanOrEqualNode(ASTLogicalNode):
    def __init__(self):
        super(ASTSmallerThanOrEqualNode, self).__init__()
        self.name = "<="

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp ole" if self.float_op() else "icmp sle")


class ASTLargerThanOrEqualNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLargerThanOrEqualNode, self).__init__()
        self.name = ">="

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp oge" if self.float_op() else "icmp sge")


class ASTEqualsNode(ASTLogicalNode):
    def __init__(self):
        super(ASTEqualsNode, self).__init__()
        self.name = "=="

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp oeq" if self.float_op() else "icmp eq")


class ASTNotEqualsNode(ASTLogicalNode):
    def __init__(self):
        super(ASTNotEqualsNode, self).__init__()
        self.name = "!="

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp one" if self.float_op() else "icmp ne")


class ASTLogicalAndNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLogicalAndNode, self).__init__()
        self.name = "&&"

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "and")


class ASTLogicalOrNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLogicalOrNode, self).__init__()
        self.name = "||"

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "or")


class ASTDeclarationNode(ASTBaseNode):
    def __init__(self, c_idx = None):
        super(ASTDeclarationNode, self).__init__()
        self.name = "Decl"
        self.c_idx = c_idx

    def enter_llvm_text(self):
        # Allocate new register
        if isinstance(self.children[1], ASTArrayDeclarationNode):
            return ""
        register = self.identifier()._generateLLVMIR()
        type_node = self.children[0]
        llvm_type = type_node._generateLLVMIR()

        if self.scope.parent is None:
            # Global register
            return f"{register} = global {llvm_type}"

        return f"{register} = alloca {llvm_type}\n"

    def exit_llvm_text(self):
        if isinstance(self.children[1], ASTArrayDeclarationNode):
            register = self.identifier()._generateLLVMIR()
            type_node = self.children[0]
            llvm_type = type_node._generateLLVMIR()
            member_type = llvm_type

            array_len = 0
            counter = 0
            queue = list()
            queue.append(self.children[1])
            while isinstance(queue[-1], ASTArrayDeclarationNode):
                if isinstance(queue[-1].children[1], ASTExpressionNode):
                    llvm_type = f"[%{self.scope.temp_register - counter} x {llvm_type}]"
                    self.scope.lookup(
                        self.identifier().identifier).aux_register = f"%{self.scope.temp_register - counter}"
                else:
                    array_len = queue[-1].children[1].llvm_value()
                    llvm_type = f"[{array_len} x {llvm_type}]"
                counter += 1
                queue.append(queue[-1].children[0])
            self.scope.lookup(self.identifier().identifier).aux_type = llvm_type
            llvm_ir = f"{register} = alloca {llvm_type}\n"

            for idx, init in enumerate(self.children[2:]):
                if idx >= array_len:
                    break
                # initialize array
                llvm_ir += f"%{self.scope.temp_register} = getelementptr {llvm_type}, {llvm_type}* {register}, i32 0, i32 {idx}\n"
                llvm_ir += f"store {member_type} {init.llvm_value()}, {member_type}* %{self.scope.temp_register}\n"
                self.scope.temp_register += 1
            return llvm_ir
        last_temp_register = self.scope.temp_register
        llvm_ir = ""
        identifier_name = self.identifier()._generateLLVMIR()
        llvm_type = c2llvm_type(self.type())
        if len(self.children) > 2:
            value_node = self.children[2]
            if isinstance(value_node, ASTConstantNode):
                value = value_node.llvm_value()
                if llvm_type == "float":
                    # Write value in scientific notation
                    value = hexify_float(str(value))
                elif llvm_type == "i8":
                    # Cast character to Unicode value
                    value = str(ord(value[1])) # Character of form: 'c'
            else:
                value = "%" + str(last_temp_register)
        else:
            # Initialise this to 0 by default
            if llvm_type == "i32" or llvm_type == "i8":
                value = "0"
            elif llvm_type == "float":
                value = "0.000000e+00"
        # Store value (expression or constant) in register
        if self.scope.parent is not None:
            llvm_ir += f"store {llvm_type} {value}, {llvm_type}* {identifier_name}\n"
        else:
            # Global declaration
            llvm_ir += f" {value}\n"
                
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
        if isinstance(self.children[1], ASTIdentifierNode):
            return self.children[1]
        else:
            return self.children[1].identifier()

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

    def enter_llvm_text(self):
        # Just a newline for readability
        llvmir = "\n"
        return llvmir

    def exit_llvm_text(self):
        llvmir = f"\n{self.finish_label}:\n"
        return llvmir


class ASTIfConditionNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfConditionNode, self).__init__()
        self.name = "IfCond"

    def exit_llvm_text(self):
        cond_register = self.scope.temp_register - 1
        self.parent.cond_register = f"%{cond_register}"
        self.parent.true_label = f"IfTrue{cond_register}"
        self.parent.false_label = f"IfFalse{cond_register}" 
        self.parent.finish_label = f"IfEnd{cond_register}"
        if len(self.parent.children) < 3:
            # No false/else block; jump to end if condition is false
            self.parent.false_label = self.parent.finish_label

        llvmir = f"br i1 {self.parent.cond_register}, label %{self.parent.true_label}, label %{self.parent.false_label}\n"
        return llvmir


class ASTIfTrueNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfTrueNode, self).__init__()
        self.name = "IfTrue"

    def enter_llvm_text(self):

        llvmir = f"\n{self.parent.true_label}:\n"
        return llvmir

    def exit_llvm_text(self):

        llvmir = f"br label %{self.parent.finish_label}\n"
        return llvmir


class ASTIfFalseNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfFalseNode, self).__init__()
        self.name = "IfFalse"

    def enter_llvm_text(self):

        llvmir = f"\n{self.parent.false_label}:\n"
        return llvmir

    def exit_llvm_text(self):

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
        self.name = "Return"
        self.c_idx = c_idx

    def exit_llvm_text(self):

        llvmir = ""
        return_value = ""

        return_type = c2llvm_type(self.children[0].type())
        if isinstance(self.children[0], ASTConstantNode):
            return_value = self.children[0].llvm_value()
        # Find function type
        function_return_type = None
        ancestor = self.parent
        while function_return_type is None:
            if isinstance(ancestor, ASTFunctionDefinitionNode):
                function_return_type = c2llvm_type(ancestor.type())
                break
            ancestor = ancestor.parent

        if isinstance(self.children[0], ASTConstantNode):
            return_value = self.children[0].value()

        elif isinstance(self.children[0], ASTIdentifierNode):
            ID_node = self.children[0]
            # Load dereferenced value into temp register
            id_register = ID_node.scope.lookup(ID_node.identifier).register
            llvmir += f"%{self.scope.temp_register} = load {return_type}, {return_type}* {id_register}\n"
            return_value = f"%{self.scope.temp_register}"
            self.scope.temp_register += 1

        else:
            return_value = f"%{self.children[0].scope.temp_register - 1}"

        # Implicit cast
        if return_type != function_return_type:
            llvmir += generate_llvm_impl_cast(self, return_value, function_return_type) + "\n"
            return_value = f"%{self.scope.temp_register-1}"
        
        llvmir += f"ret {function_return_type} {return_value}\n"
        return llvmir

    def optimise(self):
        # Prune siblings that come after this return
        if self.c_idx is not None:
            self.parent.children = self.parent.children[:self.c_idx+1]


    def type(self):
        return self.children[0].type()


class ASTCompoundStmtNode(ASTBaseNode):
    def __init__(self):
        super(ASTCompoundStmtNode, self).__init__()
        self.name = "CompoundStmt"


class ASTFunctionDefinitionNode(ASTBaseNode):
    def __init__(self):
        super(ASTFunctionDefinitionNode, self).__init__()
        self.name = "FuncDef"

    def enter_llvm_text(self):
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
                if isinstance(identifier_node, ASTIdentifierNode):
                    ident = identifier_node.identifier
                else:
                    ident = identifier_node.identifier().identifier
                type_spec = c2llvm_type(type_node.type())
                arg_decl += f"%{self.scope.temp_register} = alloca {type_spec}\n"
                arg_decl += f"store {type_spec} %{i}, {type_spec}* %{self.scope.temp_register}\n"
                self.scope.lookup(ident).register = f"%{self.scope.temp_register}"
                self.scope.temp_register += 1
            self.scope.temp_register -= 1 # Fix for 'overcounting' and misaligning the scope counter
        else:
            self.scope.temp_register += 1 # Don't start at %0
            arg_list = "()"
            arg_decl = ""

        return f"define {type_specifier} {identifier_name} {arg_list} {{\n{arg_decl}"

    def exit_llvm_text(self):
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

    def type(self):
        return self.returnType().type()


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
        return c2llvm_type(self.tspec)

    def type(self):
        return self.tspec


class ASTExprListNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTExprListNode, self).__init__(name)


class ASTArrayDeclarationNode(ASTBaseNode):
    def __init__(self):
        super(ASTArrayDeclarationNode, self).__init__()
        self.name = "ArrayDecl"

    def identifier(self):
        if isinstance(self.children[0], ASTArrayDeclarationNode):
            # We're working with a multidimensional array and we're not the first dimension
            return self.children[0].identifier()
        else:
            # 1D array
            return self.children[0]


