import logging
import struct
import AST.STT as STT


class TempRegisterCounter:
    def __init__(self):
        self.last = 0

    def get_curr(self):
        return f"%{self.last - 1}"

    def get_prev(self, n=1):
        return f"%{self.last - n}"

    def get_next(self):
        last = self.last
        self.last += 1
        return f"%{last}"


temp_reg = TempRegisterCounter()


def c2llvm_type(c_type):
    if c_type == "...":
        ir_type = "..."
    elif "int" in c_type:
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

    # Simplest case: take use the value/register from the expression
    lhs = l_child.value_register
    rhs = r_child.value_register

    # Special case: expression is identifier
    # lhs/rhs must contain dereferenced identifier, i.e. its value
    if isinstance(node.left(), ASTIdentifierNode):
        identifier_register = l_child.value_register
        lhs = f"%{node.scope.temp_register}"
        lhs_type = c2llvm_type(l_type)
        llvmir += f"{lhs} = load {lhs_type}, {lhs_type}* {identifier_register}\n"
        node.scope.temp_register += 1

    if isinstance(node.right(), ASTIdentifierNode):
        identifier_register = r_child.value_register
        rhs = f"%{node.scope.temp_register}"
        rhs_type = c2llvm_type(r_type)
        llvmir += f"{rhs} = load {rhs_type}, {rhs_type}* {identifier_register}\n"
        node.scope.temp_register += 1

    # Account for implicit conversions
    if l_type != expr_type:
        llvmir += generate_llvm_impl_cast(l_child, lhs, llvm_type)
        lhs = f"%{l_child.scope.temp_register-1}"
    elif r_type != expr_type:
        llvmir += generate_llvm_impl_cast(r_child, rhs, llvm_type)
        rhs = f"%{r_child.scope.temp_register-1}"

    llvmir += f"%{node.scope.temp_register} = {op} {llvm_type} {lhs}, {rhs}\n"
    node.value_register = f"%{node.scope.temp_register}"
    node.scope.temp_register += 1
    return llvmir


def generate_llvm_impl_cast(origin_node, origin_register, dest_type):
    # Handles implicit cast to destination type (given as LLVMIR type)
    llvmir = ""
    origin_type = c2llvm_type(origin_node.type())

    # Casting hierarchy:
    #   bool --> char --> int --> float
    #   float --> (this generates a warning) int --> char --> bool
    cast_weight = {
        "i1": 0,
        "i8": 1,
        "i32": 2,
        "float": 3,
    }

    if cast_weight[origin_type] < cast_weight[dest_type]:
        if dest_type == "float":
            if origin_type != "i32":
                # First convert to i32
                llvmir += f"%{origin_node.scope.temp_register} = sext i8 {origin_register} to i32\n"
                origin_node.scope.temp_register += 1
            origin_register = f"%{origin_node.scope.temp_register}"
            cast_instruction = "sitofp"
        else:
            cast_instruction = "zext"
    elif cast_weight[origin_type] > cast_weight[dest_type]:
        if origin_type == "float":
            logging.warning(f"Implicit conversion from float to int")
            cast_instruction = "fptosi"
        else:
            cast_instruction = "trunc"
    else:
        return ""  # origin_type and dest_type must be the same, no need to cast at all

    dest_register = f"%{origin_node.scope.temp_register}"   
    llvmir += f"{dest_register} = {cast_instruction} {origin_type} {origin_register} to {dest_type}\n"
    origin_node.value_register = dest_register
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

    def propagate_constants(self):
        for c_idx in range(len(self.children)):
            if isinstance(self.children[c_idx], ASTIdentifierNode):
                entry = self.scope.lookup(self.children[c_idx].identifier)
                if entry and entry.value is not None:
                    new_node = ASTConstantNode(entry.value, entry.type_desc)
                    new_node.parent = self
                    new_node.scope = self.children[c_idx].scope
                    self.children.pop(c_idx)
                    self.children.insert(c_idx, new_node)

    def find_ancestor(self, anc_type):
        # Returns ancestor of required type. If none exists, returns None
        anc = self.parent
        while anc is not None:
            if isinstance(anc, anc_type):
                return anc
            anc = anc.parent
        return None

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

    def populate_symbol_table(self):
        pass

    def type(self):
        return None

    def value(self):
        return None


class ASTCompilationUnitNode(ASTBaseNode):
    def __init__(self, includes_stdio=False):
        super(ASTCompilationUnitNode, self).__init__()
        self.name = "CompilationUnit"
        self.includes_stdio = includes_stdio

    def enter_llvm_text(self):
        if self.includes_stdio:
            return "declare i32 @printf(i8*, ...)\ndeclare i32 @scanf(i8*, ...)\n\n"
        else:
            return ""

    def populate_symbol_table(self):
        if self.includes_stdio:
            self.scope.table["printf"] = STT.STTEntry("printf", "int", ["char*", "..."], register="@printf")
            self.scope.table["scanf"] = STT.STTEntry("scanf", "int", ["char*", "..."], register="@scanf")


class ASTIdentifierNode(ASTBaseNode):
    def __init__(self, value):
        super(ASTIdentifierNode, self).__init__()
        self.identifier = value
        self.name = "Identifier:" + str(value)
        self.value_register = None

    def optimise(self):
        # If value known from Symbol Table, swap with constant value

        # Lookup identifier in accessible scopes
        entry = self.scope.lookup(self.identifier)
        if entry is not None and entry.value is not None:
            if isinstance(self.parent, ASTAssignmentNode) and self.parent.left() == self:
                return
            if isinstance(self.parent, ASTDeclarationNode):
                # Delete declaration
                pass
            if isinstance(self.parent, ASTBinaryExpressionNode) or isinstance(self.parent, ASTLogicalNode) \
               or isinstance(self.parent, ASTReturnNode):
                # Replace with constant node
                new_node = ASTConstantNode(entry.value, entry.type_desc)
                new_node.parent = self.parent
                new_node.scope = self.scope

                current_idx = self.parent.children.index(self)
                self.parent.children.pop(current_idx)
                self.parent.children.insert(current_idx, new_node)
                self = new_node

    def populate_symbol_table(self):
        entry = self.scope.lookup(self.identifier)
        scope = self.scope.scope_level(self.identifier)
        rank = self.scope.parent.children.index(self.scope)

        if entry:
            register = f"%{self.identifier}.scope{scope}.rank{rank}" if scope else f"@{self.identifier}"
            entry.register = register
            self.value_register = register
            entry.used = True
        else:
            logging.error(f"The identifier '{self.identifier}' was used before being declared")
            exit()

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
        self.value_register = self.llvm_value()

    def type(self):
        return self.type_specifier

    def value(self):
        return self.__value

    def llvm_value(self):
        if self.type_specifier == "float":
            return hexify_float(self.__value)
        elif self.type_specifier == "char":
            try:
                return str(ord(self.__value[1]))  # 'c' char
            except TypeError:
                return self.__value  # 99 char
        else:
            return self.__value


class ASTStringLiteralNode(ASTBaseNode):
    def __init__(self, value):
        super(ASTStringLiteralNode, self).__init__()
        self.__value = value
        self.name = "String literal:" + str(value.replace('"', '\\"'))
        self.size = None
        self.value_register = None

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

        cleaned_string, length = clean_string(self.__value)
        global_scope_node = self
        while global_scope_node.scope.parent is not None:
            global_scope_node = global_scope_node.parent 
        self.size = f"[{length + 1} x i8]"
        self.value_register = f"@str{global_scope_node.scope.temp_register}"
        global_scope_node.scope.temp_register += 1

        return f'{self.value_register} = private unnamed_addr constant {self.size} c"{cleaned_string}\\00"\n'


class ASTExpressionNode(ASTBaseNode):
    def __init__(self):
        super(ASTExpressionNode, self).__init__()
        self.value_register = None


class ASTUnaryExpressionNode(ASTExpressionNode):
    def __init__(self):
        super(ASTUnaryExpressionNode, self).__init__()
        self.value = None

    def identifier(self):
        return self.children[0]

    def type(self):
        return self.identifier().type()

    def _get_operand_register(self):
        return self.identifier().register_value


class ASTArrayAccessNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTArrayAccessNode, self).__init__()
        self.name = "ArrayAccess"

    def indexer(self):
        return self.children[1]

    def type(self):
        return self.identifier().type()[:-2] # leave out '[]'

    def exit_llvm_text(self):
        symbol_table_entry = self.scope.lookup(self.identifier().identifier)

        array_member_type = c2llvm_type(self.type())
        array_type = self.scope.lookup(self.identifier().identifier).aux_type
        array_register = symbol_table_entry.register

        idx = self.indexer().value_register
        llvm_ir = f"%{self.scope.temp_register} = getelementptr {array_type}, {array_type}* {array_register}, i32 0, i32 {idx}\n"

        temp_reg = self.scope.temp_register
        self.scope.temp_register += 1

        self.value_register = f"%{self.scope.temp_register}"
        self.scope.temp_register += 1

        llvm_ir += f"{self.value_register} = load {array_member_type}, {array_member_type}* %{temp_reg}\n"
        return llvm_ir


class ASTFunctionCallNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTFunctionCallNode, self).__init__()
        self.name = "FunctionCall"

    def type(self):
        return self.scope.lookup(self.identifier().identifier).type_desc

    def arguments(self):
        return self.children[1:]

    def exit_llvm_text(self):
        register = self.scope.temp_register

        entry = self.scope.lookup(self.identifier().identifier)
        self.value_register = entry.register
        arg_types = [c2llvm_type(tspec) for tspec in entry.args]
        function_type = c2llvm_type(self.type())

        args = list()
        llvmir = ""
        for arg in self.arguments():
            tspec = c2llvm_type(arg.type())
            if isinstance(arg, ASTConstantNode):
                args.append(f"{tspec} {arg.value_register}")
            elif isinstance(arg, ASTIdentifierNode):
                # Load value of identifier into temp. register
                llvmir += f"%{register} = load {tspec}, {tspec}* {arg.value_register}\n"
                args.append(f"{tspec} %{register}")
                register += 1
            elif isinstance(arg, ASTExpressionNode):
                args.append(f"{tspec} {arg.value_register}")
            elif isinstance(arg, ASTStringLiteralNode):
                llvmir += f"%{register} = getelementptr {arg.size}, {arg.size}* {arg.value_register}, i32 0, i32 0\n"
                args.append(f"{tspec} %{register}")
                register += 1
        reg_assign = ""
        if function_type != "void":
            reg_assign = f"%{register} = "
            register += 1
        llvmir += f"{reg_assign}call {function_type} ({', '.join(arg_types)}) {self.value_register}({', '.join(args)})\n"
        if reg_assign != "":
            self.value_register = f"%{register - 1}"
        self.scope.temp_register = register
        return llvmir


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
            logging.error("Cannot apply unary minus operator to pointer")
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


class ASTIndirectionNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTIndirectionNode, self).__init__()

    def type(self):
        if self.identifier().type()[-1] != "*":
            logging.error(
                f"Type mismatch: Cannot apply indirection operator * to \
                variable {self.identifier()} because it is not a pointer")
            exit()
        else:
            return self.identifier().type()[:-1]

    def exit_llvm_text(self):
        llvm_ir = ""
        if not isinstance(self.identifier(), ASTIndirectionNode):
            temp_register = self.scope.temp_register
            llvm_ir += f"%{temp_register} = load {c2llvm_type(self.type())}*, {c2llvm_type(self.identifier().type())}* {self.identifier().value_register}\n"
            self.scope.temp_register += 1

        self.value_register = f"%{self.scope.temp_register}"
        last_temp_register = self.scope.temp_register - 1
        llvm_ir += f"{self.value_register} = load {c2llvm_type(self.type())}, {c2llvm_type(self.identifier().type())} %{last_temp_register}\n"
        self.scope.temp_register += 1
        return llvm_ir


class ASTAddressOfNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTAddressOfNode, self).__init__()

    def type(self):
        if not isinstance(self.identifier(), ASTIdentifierNode):
            logging.error("Cannot apply address-of operator & to a non-variable")
        return self.identifier().type() + "*"

    def optimise(self):
        # For safety reasons, delete value from symbol table if possible
        entry = self.scope.lookup(self.children[0].identifier)
        if entry:
            entry.value = None

    def exit_llvm_text(self):
        temp_register = self.scope.temp_register
        llvm_ir = f"%{temp_register} = alloca {c2llvm_type(self.type())}\n"
        llvm_ir += f"store {c2llvm_type(self.identifier().type())}* {self.identifier().value_register}, {c2llvm_type(self.type())}* %{temp_register}\n"
        self.scope.temp_register += 1

        last_temp_register = temp_register
        self.value_register = f"%{self.scope.temp_register}"
        llvm_ir += f"{self.value_register} = load {c2llvm_type(self.type())}, {c2llvm_type(self.type())}* %{last_temp_register}\n"
        self.scope.temp_register += 1

        return llvm_ir


class ASTCastNode(ASTUnaryExpressionNode):
    def __init__(self):
        super(ASTCastNode, self).__init__()

    def identifier(self):
        return self.children[1]

    def type(self):
        if "*" in self.children[0].type():
            logging.error(f"Type mismatch: Cannot cast variable '{self.identifier()}' to pointer type")
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

    def result_type(self):
        """
            To be used in constant folding.
            If this expression is folded as part of a declaration/assignment, returns the type of the variable.
            Otherwise, returns the 'default' expression type.
        """

        anc = self.find_ancestor(ASTDeclarationNode) or self.find_ancestor(ASTAssignmentNode)
        if anc:
            return anc.type()
        return get_expression_type(self)


class ASTAssignmentNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAssignmentNode, self).__init__()
        self.name = "="

    def type(self):
        return self.left().type()

    def value(self):
        return self.right().value()

    def optimise(self):
        ancestor = self.parent
        while ancestor is not None:
            if isinstance(ancestor, ASTIfStmtNode) or isinstance(ancestor, ASTWhileStmtNode) or isinstance(ancestor, ASTForStmtNode):
                # Do not optimize assignments inside conditionally executed code blocks
                return
            ancestor = ancestor.parent

        # If possible, update the value in the symbol table
        if isinstance(self.children[1], ASTConstantNode):
            entry = self.scope.lookup(self.children[0].identifier)
            if entry:
                entry.value = self.children[1].value()

    def exit_llvm_text(self):
        indentifier_register = self.left().value_register
        llvm_type = c2llvm_type(self.type())
        self.value_register = self.right().value_register  # We re-use the register from the rhs expression for this assignment expression
        return f"store {llvm_type} {self.right().value_register}, {llvm_type}* {indentifier_register}\n"

    def populate_symbol_table(self):
        # If the rhs is a constant, assign the symbol table value
        if isinstance(self.children[1], ASTConstantNode):
            entry = self.scope.lookup(self.children[0].identifier)
            if entry:
                entry.value = self.children[1].value()


class ASTMultiplicationNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx):
        super(ASTMultiplicationNode, self).__init__(c_idx)
        self.name = "*"

    def value(self):
        if self.left().value() and self.right().value():
            return self.left().value() * self.right().value()

    def optimise(self):
        self.propagate_constants()

        rhs = int(self.right().value()) if isinstance(self.right(), ASTConstantNode) else None
        lhs = int(self.left().value()) if isinstance(self.left(), ASTConstantNode) else None

        if rhs == 0 or lhs == 0:
            # Evaluates to 0
            new_node = ASTConstantNode(0, get_expression_type(self))
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = new_node

        elif rhs == 1:
            # Evaluates to lhs
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, self.left())
            self = None
        
        elif lhs == 1:
            # Evaluaties to rhs
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, self.right())
            self = None

        elif lhs is not None and rhs is not None:
            # Evaluate expression in compiler
            value = lhs * rhs
            expr_type = self.result_type()
            if "float" not in expr_type:
                value = int(value)
            new_node = ASTConstantNode(value, expr_type)
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fmul" if self.type() == "float" else "mul")


class ASTDivisionNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx):
        super(ASTDivisionNode, self).__init__(c_idx)
        self.name = "/"

    def optimise(self):
        self.propagate_constants()

        value = self.right().value()
        if value and int(value) == 1:
            # This entire division will evaluate to the lhs
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, self.left())
            self = None
        elif value and int(value) == 0:
            # Division by 0: warn user
            logging.warning("Division by 0")
        elif isinstance(self.right(), ASTConstantNode) and isinstance(self.left(), ASTConstantNode):
            # Evaluate in compiler
            value = self.left().value() / self.right().value()
            expr_type = self.result_type()
            if expr_type != "float":
                value = int(value)
            new_node = ASTConstantNode(value, expr_type)
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fdiv" if self.type() == "float" else "sdiv")


class ASTModuloNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx):
        super(ASTModuloNode, self).__init__(c_idx)
        self.name = "%"

    def optimise(self):
        self.propagate_constants()

        value = self.right().value()
        if value and int(value) == 1:
            # Always returns 0, so replace with constant
            new_node = ASTConstantNode(0, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = new_node
        elif isinstance(self.right(), ASTConstantNode) and isinstance(self.left(), ASTConstantNode):
            # Evaluate in compiler
            value = self.left().value() % self.right().value()
            expr_type = self.result_type()
            if "float" not in expr_type:
                value = int(value)
            new_node = ASTConstantNode(value, expr_type)
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def type(self):
        if self.left().type() == "float" or self.right().type() == "float":
            logging.error("Can't do modulo on floating types")
            exit()
        return get_expression_type(self)

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "srem")


class ASTAdditionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTAdditionNode, self).__init__()
        self.name = "+"

    def optimise(self):
        self.propagate_constants()

        if isinstance(self.right(), ASTConstantNode) and isinstance(self.left(), ASTConstantNode):
            # Evaluate in compiler
            value = self.left().value() + self.right().value()
            expr_type = self.result_type()
            if "float" not in expr_type:
                value = int(value)
            new_node = ASTConstantNode(value, expr_type)
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fadd" if self.type() == "float" else "add")


class ASTSubtractionNode(ASTBinaryExpressionNode):
    def __init__(self):
        super(ASTSubtractionNode, self).__init__()
        self.name = "-"

    def optimise(self):
        self.propagate_constants()

        if isinstance(self.right(), ASTConstantNode) and isinstance(self.left(), ASTConstantNode):
            # Evaluate in compiler
            value = self.left().value() - self.right().value()
            expr_type = self.result_type()
            if "float" not in expr_type:
                value = int(value)
            new_node = ASTConstantNode(value, expr_type)
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

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

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() < self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp olt" if self.float_op() else "icmp slt")


class ASTLargerThanNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLargerThanNode, self).__init__()
        self.name = ">"
    
    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() > self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp ogt" if self.float_op() else "icmp sgt")


class ASTSmallerThanOrEqualNode(ASTLogicalNode):
    def __init__(self):
        super(ASTSmallerThanOrEqualNode, self).__init__()
        self.name = "<="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() <= self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp ole" if self.float_op() else "icmp sle")


class ASTLargerThanOrEqualNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLargerThanOrEqualNode, self).__init__()
        self.name = ">="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() >= self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp oge" if self.float_op() else "icmp sge")


class ASTEqualsNode(ASTLogicalNode):
    def __init__(self):
        super(ASTEqualsNode, self).__init__()
        self.name = "=="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() == self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp oeq" if self.float_op() else "icmp eq")


class ASTNotEqualsNode(ASTLogicalNode):
    def __init__(self):
        super(ASTNotEqualsNode, self).__init__()
        self.name = "!="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() != self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

    def exit_llvm_text(self):
        return generate_llvm_expr(self, "fcmp one" if self.float_op() else "icmp ne")


class ASTLogicalAndNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLogicalAndNode, self).__init__()
        self.name = "&&"

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() and self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None


    def exit_llvm_text(self):
        return generate_llvm_expr(self, "and")


class ASTLogicalOrNode(ASTLogicalNode):
    def __init__(self):
        super(ASTLogicalOrNode, self).__init__()
        self.name = "||"
        
    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        self.propagate_constants()

        if isinstance(self.left(), ASTConstantNode) and isinstance(self.right(), ASTConstantNode):
            value = int(self.left().value() or self.right().value())
            new_node = ASTConstantNode(value, "int")
            new_node.parent = self.parent
            new_node.scope = self.scope
            c_idx = self.parent.children.index(self)
            self.parent.children.pop(c_idx)
            self.parent.children.insert(c_idx, new_node)
            self = None

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
        register = self.identifier().value_register
        llvm_type = c2llvm_type(self.type())

        if self.scope.parent is None:
            # Global register
            return f"{register} = global {llvm_type}\n"

        return f"{register} = alloca {llvm_type}\n"

    def exit_llvm_text(self):
        identifier_name = self.identifier().value_register
        llvm_type = c2llvm_type(self.type())

        if isinstance(self.children[1], ASTArrayDeclarationNode):
            member_type = llvm_type

            array_len = 0
            counter = 0
            queue = list()
            queue.append(self.children[1])
            while isinstance(queue[-1], ASTArrayDeclarationNode):
                array_len = queue[-1].children[1].llvm_value()
                llvm_type = f"[{array_len} x {llvm_type}]"
                counter += 1
                queue.append(queue[-1].children[0])
            self.scope.lookup(self.identifier().identifier).aux_type = llvm_type
            llvm_ir = f"{identifier_name} = alloca {llvm_type}\n"

            for idx, init in enumerate(self.children[2:]):
                if idx >= array_len:
                    break
                # initialize array
                llvm_ir += f"%{self.scope.temp_register} = getelementptr {llvm_type}, {llvm_type}* {identifier_name}, i32 0, i32 {idx}\n"
                llvm_ir += f"store {member_type} {init.llvm_value()}, {member_type}* %{self.scope.temp_register}\n"
                self.scope.temp_register += 1
            return llvm_ir

        last_temp_register = self.scope.temp_register
        llvm_ir = ""
        value = None
        if len(self.children) > 2:
            value_node = self.children[2]
            if isinstance(value_node, ASTConstantNode):
                value = value_node.llvm_value()
                if llvm_type == "i8" and str(value)[0] == "'":
                    # Cast character to Unicode value
                    value = str(ord(value[1]))  # Character of form: 'c'
            else:
                # Account for implicit conversion
                if self.type() != self.children[2].type():
                    llvm_ir += generate_llvm_impl_cast(self.children[2], f"%{last_temp_register-1}", llvm_type)
                    last_temp_register += 1
                value = "%" + str(last_temp_register - 1)
        else:
            # Initialise this to 0 by default
            if llvm_type == "i32" or llvm_type == "i8":
                value = "0"
            elif llvm_type == "float":
                value = "0.000000e+00"

        if value is not None:
            # Store value (expression or constant) in register
            if self.scope.parent is not None:
                llvm_ir += f"store {llvm_type} {value}, {llvm_type}* {identifier_name}\n"
            else:
                # Global declaration
                llvm_ir += f" {value}\n"

        return llvm_ir

    def optimise(self):
        # Prune declarations for unused variables
        STEntry = self.scope.lookup(self.identifier().identifier)
        if STEntry and not STEntry.used:
            self.parent.children.pop(self.parent.children.index(self))
            self = None
        elif STEntry and STEntry.used:
             # If possible, update the value of the variable in the symbol table
            value = None
            if len(self.children) > 2 and isinstance(self.children[2], ASTConstantNode):
                value = self.children[2].value()
            STEntry.value = value

    def populate_symbol_table(self):
        type_spec = self.type()
        identifier = self.identifier().identifier

        if identifier not in self.scope.table:
            # If possible, assign the value of the assigned variable in the symbol table
            value = None
            if len(self.children) > 2 and isinstance(self.children[2], ASTConstantNode):
                value = self.children[2].value()
            self.scope.table[identifier] = STT.STTEntry(identifier, type_spec, value=value)
        else:
            logging.error(f"The variable '{identifier}' was redeclared")
            exit()

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

    def optimise(self):
        # If condition is a constant, replace IfStmtNode by appropriate (conditional) subtree
        cond_node = self.children[0]
        if len(cond_node.children) == 1 and isinstance(cond_node.children[0], ASTConstantNode):
            new_tree = None
            # If not 0, replace this node with the 'true' subtree
            if cond_node.children[0].value() != 0:
                new_tree = self.children[1].children[0] # self->IfTrue->compound
            # Else, replace it with the 'false' subtree if one exists, otherwise just delete this node
            else:
                if len(self.children) > 2:
                    new_tree = self.children[2].children[0]
                else:
                    new_tree = -1
            
            if new_tree == -1:
                # Delete this node
                self.parent.children.pop(self.parent.children.index(self))
            elif new_tree is not None:
                # Replace this node
                new_tree.parent = self.parent
                c_idx = self.parent.children.index(self)
                self.parent.children.pop(c_idx)
                self.parent.children.insert(c_idx, new_tree)
                self = None


    def enter_llvm_text(self):
        # Just a newline for readability
        llvmir = "\n"
        return llvmir

    def exit_llvm_text(self):
        # Update outer scope counter
        self.parent.scope.temp_register = self.scope.temp_register
        llvmir = f"\n{self.finish_label}:\n"
        return llvmir


class ASTIfConditionNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfConditionNode, self).__init__()
        self.name = "IfCond"

    def optimise(self):
        # Constant propagation if possible
        self.propagate_constants()

    def exit_llvm_text(self):
        cond_register = self.scope.temp_register - 1
        self.parent.cond_register = f"%{cond_register}"
        self.parent.true_label = f"IfTrue{cond_register}"
        self.parent.false_label = f"IfFalse{cond_register}"
        self.parent.finish_label = f"IfEnd{cond_register}"

        if len(self.parent.children) < 3:
            # No false/else block; jump to end if condition is false
            self.parent.false_label = self.parent.finish_label

        llvmir = ""

        if isinstance(self.children[0], ASTIdentifierNode):
            identifier_register = self.children[0].value_register
            identifer_type = c2llvm_type(self.children[0].type())

            llvmir += f"%{self.scope.temp_register} = load {identifer_type}, {identifer_type}* {identifier_register}\n"
            self.scope.temp_register += 1

        llvmir += generate_llvm_impl_cast(self.children[0], f"%{self.scope.temp_register - 1}", "i1")
        cond_register = self.children[0].value_register

        llvmir += f"br i1 {cond_register}, label %{self.parent.true_label}, label %{self.parent.finish_label}\n"
        return llvmir


class ASTIfTrueNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfTrueNode, self).__init__()
        self.name = "IfTrue"

    def enter_llvm_text(self):
        # Set body scope counter to outer scope counter
        self.children[0].scope.temp_register = self.parent.scope.temp_register
        llvmir = f"\n{self.parent.true_label}:\n"
        return llvmir

    def exit_llvm_text(self):
        # Set outer scope counter to body scope counter
        self.parent.scope.temp_register = self.children[0].scope.temp_register
        llvmir = f"br label %{self.parent.finish_label}\n"
        return llvmir


class ASTIfFalseNode(ASTBaseNode):
    def __init__(self):
        super(ASTIfFalseNode, self).__init__()
        self.name = "IfFalse"

    def enter_llvm_text(self):
        # Set body scope counter to outer scope counter
        self.children[0].scope.temp_register = self.parent.scope.temp_register
        llvmir = f"\n{self.parent.false_label}:\n"
        return llvmir

    def exit_llvm_text(self):
        # Set outer scope counter to body scope counter
        self.parent.scope.temp_register = self.children[0].scope.temp_register
        llvmir = f"br label %{self.parent.finish_label}\n"
        return llvmir


class ASTSwitchStmtNode(ASTBaseNode):
    def __init__(self):
        super(ASTSwitchStmtNode, self).__init__()
        self.name = "Switch"


class ASTWhileStmtNode(ASTBaseNode):
    def __init__(self, name="While"):
        super(ASTWhileStmtNode, self).__init__(name)
        self.cond_label = None
        self.true_label = None
        self.finish_label = None

    def optimise(self):
        # If condition is a constant, replace IfStmtNode by appropriate (conditional) subtree
        cond_node = self.children[0]
        if len(cond_node.children) == 1 and isinstance(cond_node.children[0], ASTConstantNode):
            if cond_node.children[0].value() == 0:
                # Delete this node
                self.parent.children.pop(self.parent.children.index(self))

    def exit_llvm_text(self):
        # Set outer scope counter to scope counter
        self.parent.scope.temp_register = self.scope.temp_register

        llvmir = f"\n{self.finish_label}:\n"
        return llvmir


class ASTWhileCondNode(ASTWhileStmtNode):
    def __init__(self):
        super(ASTWhileCondNode, self).__init__("WhileCond")

    def optimise(self):
        self.propagate_constants()

    def enter_llvm_text(self):
        # Set body scope counter to outer scope counter
        self.children[0].scope.temp_register = self.parent.scope.temp_register
        counter = self.scope.temp_register
        self.parent.cond_label = f"WhileCond{counter}"
        self.parent.true_label = f"WhileTrue{counter}"
        self.parent.finish_label = f"WhileEnd{counter}"

        llvmir = f"br label %{self.parent.cond_label}\n"
        llvmir += f"\n{self.parent.cond_label}:\n"
        return llvmir

    def exit_llvm_text(self):
        # Set outer scope counter to body scope counter
        self.parent.scope.temp_register = self.children[0].scope.temp_register

        llvmir = ""

        if isinstance(self.children[0], ASTIdentifierNode):
            identifier_register = self.children[0].value_register
            identifer_type = c2llvm_type(self.children[0].type())

            llvmir += f"%{self.scope.temp_register} = load {identifer_type}, {identifer_type}* {identifier_register}\n"
            self.scope.temp_register += 1

        llvmir += generate_llvm_impl_cast(self.children[0], self.children[0].value_register, "i1")

        cond_register = self.children[0].value_register

        llvmir += f"br i1 {cond_register}, label %{self.parent.true_label}, label %{self.parent.finish_label}\n"
        return llvmir


class ASTWhileTrueNode(ASTWhileStmtNode):
    def __init__(self):
        super(ASTWhileTrueNode, self).__init__("WhileTrue")

    def enter_llvm_text(self):
        # Set body scope counter to outer scope counter
        self.children[0].scope.temp_register = self.parent.scope.temp_register

        llvmir = f"\n{self.parent.true_label}:\n"
        return llvmir

    def exit_llvm_text(self):
        # Set outer scope counter to body scope counter
        self.parent.scope.temp_register = self.children[0].scope.temp_register

        llvmir = f"br label %{self.parent.cond_label}\n"
        return llvmir


class ASTForStmtNode(ASTBaseNode):
    def __init__(self, name="For"):
        super(ASTForStmtNode, self).__init__(name)
        self.cond_label = None
        self.updater_label = None
        self.true_label = None
        self.finish_label = None

    def enter_llvm_text(self):
        self.scope.temp_register = self.parent.scope.temp_register
        return ""

    def exit_llvm_text(self):
        self.scope.parent.temp_register = self.scope.temp_register
        llvmir = f"\n{self.finish_label}:\n"
        return llvmir


class ASTForInitNode(ASTForStmtNode):
    def __init__(self):
        super(ASTForInitNode, self).__init__("ForInit")

    def enter_llvm_text(self):
        # Newline for readability
        llvmir = "\n"
        return llvmir
    
    def exit_llvm_text(self):
        # Override parent method because this returns nothing
        return ""


class ASTForCondNode(ASTForStmtNode):
    def __init__(self):
        super(ASTForCondNode, self).__init__("ForCond")

    def enter_llvm_text(self):
        counter = self.scope.temp_register
        self.scope.temp_register += 1
        self.parent.cond_label = f"ForCond{counter}"
        self.parent.updater_label = f"ForUpdater{counter}"
        self.parent.true_label = f"ForTrue{counter}"
        self.parent.finish_label = f"ForEnd{counter}"

        llvmir = f"br label %{self.parent.cond_label}\n\n"
        llvmir += f"{self.parent.cond_label}:\n"
        return llvmir

    def exit_llvm_text(self):
        llvmir = ""

        if isinstance(self.children[0], ASTIdentifierNode):
            identifier_register = self.children[0].value_register
            identifer_type = c2llvm_type(self.children[0].type())

            llvmir += f"%{self.scope.temp_register} = load {identifer_type}, {identifer_type}* {identifier_register}\n"
            self.scope.temp_register += 1

        llvmir += generate_llvm_impl_cast(self.children[0], f"%{self.scope.temp_register - 1}", "i1")
        cond_register = self.children[0].value_register

        llvmir += f"br i1 {cond_register}, label %{self.parent.true_label}, label %{self.parent.finish_label}\n"
        return llvmir


class ASTForUpdaterNode(ASTForStmtNode):
    def __init__(self):
        super(ASTForUpdaterNode, self).__init__("ForUpdater")

    def enter_llvm_text(self):

        llvmir = f"{self.parent.updater_label}:\n"
        return llvmir

    def exit_llvm_text(self):

        llvmir = f"br label %{self.parent.cond_label}\n"
        return llvmir


class ASTForTrueNode(ASTForStmtNode):
    def __init__(self):
        super(ASTForTrueNode, self).__init__("ForTrue")

    def enter_llvm_text(self):
        # Set scope counter to parent scope counter
        self.scope.temp_register = self.parent.scope.temp_register

        llvmir = f"\n{self.parent.true_label}:\n"
        return llvmir

    def exit_llvm_text(self):
        # Set parent scope counter to scope counter
        self.parent.scope.temp_register = self.scope.temp_register

        llvmir = f"br label %{self.parent.updater_label}\n"
        return llvmir


class ASTGotoNode(ASTBaseNode):
    def __init__(self):
        super(ASTGotoNode, self).__init__()


class ASTContinueNode(ASTBaseNode):
    def __init__(self, c_idx = None):
        super(ASTContinueNode, self).__init__()
        self.c_idx = c_idx

    def exit_llvm_text(self):
        # Get loop parent
        loop_parent = self.parent
        while not (isinstance(loop_parent, ASTWhileStmtNode) or isinstance(loop_parent, ASTForStmtNode)):
            loop_parent = loop_parent.parent

        # Loop cuts short, so increment counter to account for next block
        self.scope.temp_register += 1
        
        llvmir = f"br label %{loop_parent.cond_label}\n"
        return llvmir
    
    def optimise(self):
        # Prune siblings that come after this continue
        if self.c_idx is not None:
            self.parent.children = self.parent.children[:self.c_idx+1]


class ASTBreakNode(ASTBaseNode):
    def __init__(self, c_idx = None):
        super(ASTBreakNode, self).__init__()
        self.c_idx = c_idx

    def exit_llvm_text(self):
        # Get loop parent (this is guaranteed to end since compilation fails if break outside of loop)
        loop_parent = self.parent
        while not (isinstance(loop_parent, ASTWhileStmtNode) or isinstance(loop_parent, ASTForStmtNode)):
            loop_parent = loop_parent.parent

        # Loop cuts short, so increment counter to account for next block
        self.scope.temp_register += 1

        llvmir = f"br label %{loop_parent.finish_label}\n"
        return llvmir
    
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
        if function_return_type == "void":
            # Doesn't return anything
            return "ret void\n"

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
            return_value = f"%{self.scope.temp_register - 1}"
        
        llvmir += f"ret {function_return_type} {return_value}\n"
        return llvmir

    def optimise(self):
        # Check if child value known at compiletime
        if isinstance(self.children[0], ASTIdentifierNode):
            entry = self.scope.lookup(self.children[0].identifier)
            if entry and entry.value is not None:
                new_node = ASTConstantNode(entry.value, entry.type_desc)
                new_node.parent = self
                new_node.scope = self.children[0].scope
                self.children[0] = new_node

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
        type_specifier = c2llvm_type(self.returnType().type())
        identifier_name = self.identifier().value_register
        has_params = isinstance(self.children[2], ASTParameterTypeList)
        if has_params:
            args = self.children[2]
            arg_list = args._generateLLVMIR()
            arg_decl = ""
            argc = len(args.children) // 2
            self.scope.temp_register = argc + 1
            for i, (type_node, identifier_node) in enumerate(zip(args.children[0::2], args.children[1::2])):
                type_spec = c2llvm_type(type_node.type())
                arg_decl += f"{identifier_node.value_register} = alloca {type_spec}\n"
                arg_decl += f"store {type_spec} %{i}, {type_spec}* {identifier_node.value_register}\n"
        else:
            self.scope.temp_register = 1  # Don't start at %0
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

    def populate_symbol_table(self):
        type_spec = self.returnType().tspec
        identifier = self.identifier().identifier
        args = []
        for arg in self.arguments():
            try:
                args.append(arg.tspec)
            except AttributeError:
                # Skip identifiers
                pass
        if identifier not in self.parent.scope.table:
            self.parent.scope.table[identifier] = STT.STTEntry(identifier, type_spec, args)
        else:
            logging.error(f"The function '{identifier}' was redeclared")
            exit()


class ASTParameterTypeList(ASTBaseNode):
    def __init__(self):
        super(ASTParameterTypeList, self).__init__()
        self.name = "ParamList"

    def _generateLLVMIR(self):

        llvmir = "("
        for type_child in self.children[::2]:
            llvmir += c2llvm_type(type_child.type()) + ", "

        llvmir = llvmir[:-2]
        llvmir += ")"
        return llvmir

    def populate_symbol_table(self):
        if isinstance(self.parent, ASTFunctionDefinitionNode):
            for type_node, identifier_node in zip(self.children[0::2], self.children[1::2]):
                if identifier_node.identifier not in self.scope.table:
                    if isinstance(identifier_node, ASTIdentifierNode):
                        iden = identifier_node.identifier
                    else:
                        iden = identifier_node.identifier().identifier
                    self.scope.table[iden] = STT.STTEntry(iden, type_node.type())


class ASTTypeSpecifierNode(ASTBaseNode):
    def __init__(self, tspec):
        super(ASTTypeSpecifierNode, self).__init__()
        self.tspec = tspec
        self.name = "Type:" + str(tspec)

    def type(self):
        return self.tspec


class ASTExprListNode(ASTBaseNode):
    def __init__(self, name):
        super(ASTExprListNode, self).__init__(name)


class ASTArrayDeclarationNode(ASTBaseNode):
    def __init__(self):
        super(ASTArrayDeclarationNode, self).__init__()
        self.name = "ArrayDecl"
        self.value_register = None

    def populate_symbol_table(self):
        scope = self.scope.scope_level(self.identifier().identifier)
        self.value_register = f"%{self.identifier().identifier}.scope{scope}" if scope else f"@{self.identifier().identifier}"

    def identifier(self):
        if isinstance(self.children[0], ASTArrayDeclarationNode):
            # We're working with a multidimensional array and we're not the first dimension
            return self.children[0].identifier()
        else:
            # 1D array
            return self.children[0]


