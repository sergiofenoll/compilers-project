import logging
import struct
import re
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


class Allocator:

    temp_regs = [f"$t{i}" for i in range(0, 10)]
    float_regs = [f"$f{i}" for i in range(4, 11)]
    all_regs = {"int": temp_regs, "float": float_regs}

    def __init__(self):
        self.available_regs = Allocator.all_regs
        self.used_regs = {"int": list(), "float": list()}
        self.spilled_regs = dict()
        self.min_frame_size = None

    def push_register_on_stack(self, register):
        # Generates the code necessary to push a given register on the stack, taking care of the stack pointer
        mips = ""
        mips += f"sw {register}, 0($sp)\n"
        mips += "add $sp, $sp, 4\n"
        return mips

    def allocate_next_register(self, float=False):
        t = "float" if float else "int"
        if len(self.available_regs[t]):
            reg = self.available_regs[t].pop(0)
            self.used_regs[t].append(reg)
            return reg, False
        else:
            # Spill
            spilled_reg = self.used_regs[t][0]
            memory_location = f"{4 * (self.min_frame_size + len(self.spilled_regs.keys()) + 1)}($fp)"
            self.spilled_regs[spilled_reg] = memory_location
            return spilled_reg, True

    def deallocate_register(self, reg, float=False):
        t = "float" if float else "int"
        if reg in self.spilled_regs:
            memory_location = self.spilled_regs[reg]
            self.spilled_regs.pop(reg)
            return memory_location
        else:
            self.available_regs[t].insert(0, reg)
            self.used_regs[t].remove(reg)
            return None

    def get_memory_address(self, identifier, scope, idx=0):
        count = 0
        while scope.parent is not None:
            for var in scope.table.values():
                if var.identifier == identifier:
                    if "[]" in var.type_desc:
                        count += 1 + idx # idx is zero-indexed, add one to account for the fact that array _is_ one further
                    else:
                        count += var.size
                    break
                count += var.size
            scope = scope.parent
        mem_addr = (count + 1) * 4
        # count + 1 because because we pushed $ra at the begginning of the stack
        return f"{mem_addr}($fp)"



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


def c2mips_type(c_type):
    if c_type == "...":
        mips_type = "..."
    elif "int" in c_type:
        mips_type = ".word"
    elif "char" in c_type:
        mips_type =".byte"
    else:
        mips_type = ".float"
    return mips_type


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


def generate_mips_expr(node, op):
    """
        Generate mips (binary) expression of the form: op d, t, s
        Does not account for conversions (expects operands to have compatible types)
    """

    mips = ""
    target_reg = ""
    source_reg = ""

    lhs = node.left()
    rhs = node.right()
    allocator = node.get_allocator()
    float_type = False

    # No implicit conversions: check types
    if "float" in [lhs.type(), rhs.type()]:
        if lhs.type() != rhs.type():
            logging.error(f"line {node.line_info[0]}:{node.line_info[1]} Implicit conversion not supported.")
        else:
            float_type = True

    # Get proper registers
    if isinstance(lhs, ASTIdentifierNode) or isinstance(lhs, ASTBinaryExpressionNode) or isinstance(rhs, ASTArrayAccessNode):
        target_reg = lhs.value_register
        if target_reg is None:
            target_reg, spilled = allocator.allocate_next_register(float_type)
            if spilled:
                mips += f"sw {target_reg}, {allocator.spilled_regs[target_reg]}\n"
            load_op = "lwc1" if float_type else "lw"
            memory_address = lhs.scope.lookup(lhs.identifier).memory_location
            mips += f"{load_op} {target_reg}, {memory_address}\n"
    if isinstance(rhs, ASTIdentifierNode) or isinstance(rhs, ASTBinaryExpressionNode) or isinstance(rhs, ASTArrayAccessNode):
        source_reg = rhs.value_register
        if source_reg is None:
            source_reg, spilled = allocator.allocate_next_register(float_type)
            if spilled:
                mips += f"sw {source_reg}, {allocator.spilled_regs[source_reg]}\n"
            load_op = "lwc1" if float_type else "lw"
            memory_address = rhs.scope.lookup(rhs.identifier).memory_location
            mips += f"{load_op} {source_reg}, {memory_address}\n"

    immediate_operations = ["add", "div", "sub", "mul", "sgt", "seq", "sne"]
    if isinstance(lhs, ASTConstantNode):
        # Load lhs into register
        target_reg, spilled = allocator.allocate_next_register(float_type)
        if spilled:
                mips += f"sw {target_reg}, {allocator.spilled_regs[target_reg]}\n"
        mips += f"li {target_reg}, {lhs.value()}\n"    
    if isinstance(rhs, ASTConstantNode):
        if op not in immediate_operations:
            # Load rhs into register
            source_reg, spilled = allocator.allocate_next_register(float_type)
            if spilled:
                mips += f"sw {source_reg}, {allocator.spilled_regs[source_reg]}\n"
            if not float_type:
                mips += f"li {source_reg}, {rhs.value()}\n"
            else:
                mips += f"l.s {source_reg}, {rhs.value_register}\n"
        else:
            source_reg = rhs.value()

    if op == "div" or op == "div.s":
        if not isinstance(rhs, ASTConstantNode):
            move_op = ""
            if isinstance(node, ASTModuloNode):
                move_op = "mfhi"
            else: # isinstance(ASTDivisionNode)
                move_op = "mflo"
            mips += f"{op} {target_reg}, {source_reg}\n"
            mips += f"{move_op} {target_reg}\n"
        else:
            mips += f"{op} {target_reg}, {target_reg}, {source_reg}\n"
    else:
        mips += f"{op} {target_reg}, {target_reg}, {source_reg}\n"
    node.value_register = target_reg

    if not isinstance(rhs, ASTConstantNode):
        memory_location = allocator.deallocate_register(source_reg, float_type)
        if memory_location:
            # Spilled register is free again, restore value
            mips += f"lw {source_reg}, {memory_location}\n"
    return mips

def generate_mips_float_comp(node, op):
    # Generate expression for LogicalNodes that are of float type
    
    mips = ""
    allocator = node.get_allocator()
    lhs = node.left().value_register
    rhs = node.right().value_register
    lhs_allocated = False
    rhs_allocated = False

    # Get rhs and lhs into registers
    if isinstance(node.left(), ASTConstantNode):
        lhs_allocated = True
        lhs, spilled = allocator.allocate_next_register(float=True)
        if spilled:
            mips += f"swc1 {lhs}, {allocator.spilled_regs[lhs]}\n"
        mips += f"l.s {lhs}, {node.left().value_register}\n"

    if isinstance(node.left(), ASTIdentifierNode):
        lhs_allocated = True
        lhs, spilled = allocator.allocate_next_register(float=True)
        if spilled:
            mips += f"swc1 {lhs}, {allocator.spilled_regs[lhs]}\n"
        mips += f"lwc1 {lhs}, {allocator.get_memory_address(node.left().identifier, node.scope)}\n"

    if isinstance(node.right(), ASTConstantNode):
        rhs_allocated = True
        rhs, spilled = allocator.allocate_next_register(float=True)
        if spilled:
            mips += f"swc1 {rhs}, {allocator.spilled_regs[rhs]}\n"
        mips += f"l.s {rhs}, {node.right().value_register}\n"

    if isinstance(node.right(), ASTIdentifierNode):
        rhs_allocated = True
        rhs, spilled = allocator.allocate_next_register(float=True)
        if spilled:
            mips += f"swc1 {rhs}, {allocator.spilled_regs[rhs]}\n"
        mips += f"lwc1 {rhs}, {allocator.get_memory_address(node.right().identifier, node.scope)}\n"

    mips += f"{op} {lhs}, {rhs}\n"
    
    if lhs_allocated:
        memory_location = allocator.deallocate_register(lhs, True)
        if memory_location:
            mips += f"lwc1 {lhs}, {memory_location}\n"
    if rhs_allocated:
        memory_location = allocator.deallocate_register(rhs, True)
        if memory_location:
            mips += f"lwc1 {rhs}, {memory_location}\n"

    return mips

    



class ASTBaseNode:
    def __init__(self, name=None, scope=None, ctx=None):
        self.parent = None
        self.children = []
        self.scope = scope
        self.name = name or type(self).__name__
        if ctx:
            self.line_info = (ctx.start.line, ctx.start.column)
        else:
            self.line_info = None

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

    def enter_mips_data(self):
        return ""

    def exit_mips_data(self):
        return ""

    def enter_mips_text(self):
        return ""

    def exit_mips_text(self):
        return ""

    def _generateLLVMIR(self):
        return ""

    def generateMIPS(self):
        return ""

    def get_allocator(self):
        if self.parent:
            return self.parent.get_allocator()
        else:
            lineinfo = ""
            if self.line_info:
                lineinfo = f"line {self.line_info[0]}:{self.line_info[1]} "
            logging.error(f"{lineinfo}No operations in global scope allowed.")
            exit()

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
    def __init__(self, includes_stdio=False, ctx=None):
        super(ASTCompilationUnitNode, self).__init__(ctx=ctx)
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
    def __init__(self, value, ctx=None):
        super(ASTIdentifierNode, self).__init__(ctx=ctx)
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

            # Don't propagate in loop conditions
            loop_parent = self.parent
            while loop_parent:
                if isinstance(loop_parent, ASTForStmtNode) or isinstance(loop_parent, ASTWhileStmtNode):
                    return
                loop_parent = loop_parent.parent

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
        if scope:
            rank = self.scope.parent.children.index(self.scope)

        if entry:
            register = f"%{self.identifier}.scope{scope}.rank{rank}" if scope else f"@{self.identifier}"
            entry.register = register
            #self.value_register = register

            # Set usage
            anc = self.find_ancestor(ASTDeclarationNode) or self.find_ancestor(ASTAssignmentNode)
            if not anc:
                entry.used = True
            else:
                if anc.identifier().identifier != self.identifier:
                    entry.used = True
            
        else:
            logging.error(f"line {self.line_info[0]}:{self.line_info[1]} The identifier '{self.identifier}' was used before being declared")
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
    float_counter = 0
    def __init__(self, value, type_specifier, ctx=None):
        super(ASTConstantNode, self).__init__(ctx=ctx)
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


    def enter_mips_data(self):
        if self.type() == "float":
            float_label = f"fl{ASTConstantNode.float_counter}"
            if self.value() == 0:
                self.value_register = "zero_float"
                return ""
            ASTConstantNode.float_counter += 1
            self.value_register = float_label
            return f"{float_label}: .float {self.value()}\n"
        return ""

class ASTStringLiteralNode(ASTBaseNode):
    string_counter = 0
    def __init__(self, value, ctx=None):
        super(ASTStringLiteralNode, self).__init__(ctx=ctx)
        self.__value = value
        self.name = "String literal:" + str(value.replace('"', '\\"'))
        self.size = None
        self.value_register = None

    def type(self):
        return "char*"

    def value(self):
        return self.__value

    def populate_symbol_table(self):
        self.scope.lookup(self.parent.identifier().identifier).value = self.value()

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

    def enter_mips_data(self):
        if isinstance(self.parent, ASTFunctionCallNode):
            self.value_register = f"temp_str_{ASTStringLiteralNode.string_counter}"
            ASTStringLiteralNode.string_counter += 1
        else:
            self.value_register = self.parent.identifier().identifier
        
        mips = ""
        fstr = self.value().replace('"', '')
        m = re.findall(r"([^%]+)|(%s)|(%d)|(%i)|(%c)|(%f)", fstr)
        str_count = 0
        for s in m:
            if s[0] != '':
                # Matched a string as opposed to a code
                fstr_loc = f"{self.value_register}_str_part_{str_count}"
                mips += f'{fstr_loc}: .asciiz "{s[0]}"\n'
                str_count += 1
        return mips


class ASTExpressionNode(ASTBaseNode):
    def __init__(self, ctx=None):
        super(ASTExpressionNode, self).__init__(ctx=ctx)
        self.value_register = None


class ASTUnaryExpressionNode(ASTExpressionNode):
    def __init__(self, ctx=None):
        super(ASTUnaryExpressionNode, self).__init__(ctx=ctx)
        self.value = None

    def identifier(self):
        return self.children[0]

    def type(self):
        return self.identifier().type()

    def _get_operand_register(self):
        return self.identifier().register_value


class ASTArrayAccessNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTArrayAccessNode, self).__init__(ctx=ctx)
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

    def enter_mips_text(self):
        mips = ""
        allocator = self.get_allocator()
        float_type = self.type() == "float"

        store_op = "swc1" if float_type else "sw"
        load_op = "lwc1" if float_type else "lw"
        load_imm = "l.s" if float_type else "li"

        reg, spilled = allocator.allocate_next_register(float_type)
        if spilled:
            mips += f"{store_op} {reg}, {allocator.spilled_regs[reg]}\n"
        mem_addr = allocator.get_memory_address(self.identifier().identifier, self.scope)
        mips += f"la {reg}, {mem_addr}\n"

        if isinstance(self.indexer(), ASTIdentifierNode) or isinstance(self.indexer(), ASTBinaryExpressionNode):
            indexer_reg = self.indexer().value_register
            if indexer_reg is None:
                indexer_reg, spilled = allocator.allocate_next_register(float_type)
                if spilled:
                    mips += f"sw {indexer_reg}, {allocator.spilled_regs[indexer_reg]}\n"
                memory_address = self.scope.lookup(self.indexer().identifier).memory_location
                mips += f"{load_op} {indexer_reg}, {memory_address}\n"
        else:
            indexer_reg, spilled = allocator.allocate_next_register(float_type)
            if spilled:
                mips += f"sw {indexer_reg}, {allocator.spilled_regs[indexer_reg]}\n"
            mips += f"{load_imm} {indexer_reg}, {self.indexer().value()}\n"

        mips += f"mul {indexer_reg}, {indexer_reg}, 4\n"
        mips += f"add {reg}, {reg}, {indexer_reg}\n"
        memory_location = allocator.deallocate_register(indexer_reg)
        if memory_location:
            mips += f"{load_op} {indexer_reg}, {memory_location}\n"
        self.value_register = reg
        return mips

    def exit_mips_text(self):
        float_type = self.type() == "float"
        load_op = "lwc1" if float_type else "lw"
        if isinstance(self.parent, ASTAssignmentNode):
            if self != self.parent.left():
                mips = f"{load_op} {self.value_register}, ({self.value_register})\n"
        return ""


class ASTFunctionCallNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTFunctionCallNode, self).__init__(ctx=ctx)
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

    def exit_mips_text(self):
        def load_var_or_constant(node):
            mips = ""
            allocator = node.get_allocator()
            float_type = node.type() == 'float'

            store_op = "swc1" if float_type else "sw"
            load_op = "lwc1" if float_type else "lw"
            load_imm = "l.s" if float_type else "li"

            reg, spilled = allocator.allocate_next_register(float_type)
            if spilled:
                mips += f"{store_op} {reg}, {allocator.spilled_regs[reg]}\n"

            if isinstance(node, ASTConstantNode):
                mips += f"{load_imm} {reg}, {node.value()}\n"
            elif isinstance(node, ASTIdentifierNode):
                mips += f"{load_op} {reg}, {allocator.get_memory_address(node.identifier, node.scope)}\n"
            elif isinstance(node, ASTExpressionNode):
                mips += f"{load_op} {reg}, {node.value_register}\n"

            memory_location = allocator.deallocate_register(reg, float_type)
            if memory_location:
                mips += f"{load_op} {reg}, {memory_location}\n"
            return mips, reg

        mips = ""
        allocator = self.get_allocator()
        float_type = None
        if self.identifier().identifier == "printf":
            fstr_prefix = self.arguments()[0].value_register or self.scope.lookup(self.arguments()[0].identifier).register
            
            if isinstance(self.arguments()[0], ASTStringLiteralNode):
                fstr = self.arguments()[0].value()
            elif isinstance(self.arguments()[0], ASTIdentifierNode):
                fstr = self.scope.lookup(self.arguments()[0].identifier).value
            if not fstr:
                # We're printing a string on the stack
                # Special case so early return
                mips += f"la $a0, {allocator.get_memory_address(self.arguments()[0].identifier, self.scope)}\n"
                mips += "li $v0, 4\n"
                mips += "syscall\n"
                return mips
            fstr = fstr.replace('"', '')
            m = re.findall(r"([^%]+)|(%s)|(%d)|(%i)|(%c)|(%f)", fstr)

            str_count = 0
            arg_count = 1
            for s in m:
                if s[0] != '' or s[1] != '':
                    # Matched a string as opposed to a code
                    fstr_loc = f"{fstr_prefix}_str_part_{str_count}"
                    mips += f"la $a0, {fstr_loc}\n"
                    mips += "li $v0, 4\n"
                    mips += "syscall\n"
                    str_count += 1
                    if s[1] == '':
                        continue
                elif s[2] != '' or s[3] != '':
                    # Matched an integer code
                    mips_load_arg, reg = load_var_or_constant(self.arguments()[arg_count])
                    mips += mips_load_arg
                    mips += f"move $a0, {reg}\n"
                    mips += "li $v0, 1\n"
                    mips += "syscall\n"
                elif s[4] != '':
                    # Matched a character code
                    mips_load_arg, reg = load_var_or_constant(self.arguments()[arg_count])
                    mips += mips_load_arg
                    mips += f"move $a0, {reg}\n"
                    mips += "li $v0, 11\n"
                    mips += "syscall\n"
                elif s[5] != '':
                    # Matched a float code
                    mips_load_arg, reg = load_var_or_constant(self.arguments()[arg_count])
                    mips += mips_load_arg
                    mips += f"mov.s $f12, {reg}\n"
                    mips += "li $v0, 2\n"
                    mips += "syscall\n"
                arg_count += 1
        elif self.identifier().identifier == "scanf":
            fstr_prefix = self.arguments()[0].value_register or self.scope.lookup(self.arguments()[0].identifier).register
            fstr = self.arguments()[0].value()
            
            if not fstr:
                fstr = self.scope.lookup(self.arguments()[0].identifier).value
            fstr = fstr.replace('"', '')
            m = re.findall(r"(%s)|(%d)|(%i)|(%c)|(%f)", fstr)
            
            arg_count = 1
            for s in m:
                arg = self.arguments()[arg_count]
                if isinstance(arg, ASTAddressOfNode):
                    arg_id = arg.identifier().identifier
                else:
                    arg_id = arg.identifier
                if s[0] != '':
                    # Matched a string as opposed to a code
                    mem_loc = allocator.get_memory_address(arg_id, self.scope)
                    mem_len = self.scope.lookup(arg.identifier).size
                    mips += f"la $a0, {mem_loc}\n"
                    mips += f"li $a1, {mem_len}\n"
                    mips += "li $v0, 8\n"
                    mips += "syscall\n"
                    continue
                elif s[1] != '' or s[2] != '':
                    # Matched an integer code
                    mem_loc = allocator.get_memory_address(arg_id, self.scope)
                    mips += "li $v0, 5\n"
                    mips += "syscall\n"
                    mips += f"sw $v0, {mem_loc}\n"
                elif s[3] != '':
                    # Matched a character code
                    mem_loc = allocator.get_memory_address(arg_id, self.scope)
                    mips += "li $v0, 12\n"
                    mips += "syscall\n"
                    mips += f"sw $v0, {mem_loc}\n"
                elif s[4] != '':
                    # Matched a float code
                    mem_loc = allocator.get_memory_address(arg_id, self.scope)
                    mips += "li $v0, 6\n"
                    mips += "syscall\n"
                    mips += f"swc1 $f0, {mem_loc}\n"
                arg_count += 1
        else:
            for i, arg in enumerate(self.arguments()):
                mips_load_arg, reg = load_var_or_constant(arg)
                mips += mips_load_arg

                float_type = arg.type() == 'float'

                store_op = "swc1" if float_type else "sw"
                move_op = "mov.s" if float_type else "move"
                if i < 4:
                    arg_reg = f"${'f' if float_type else 'a'}{i + 12 if float_type else i}"
                    mips += f"{move_op} {arg_reg}, {reg}\n"
                else:
                    mips += f"{store_op} {reg}, ($sp)\n"
                    mips += f"add $sp, $sp, 4\n"
            mips += f"jal fun_{self.identifier().identifier}\n"

        return_reg = f"${'f' if float_type else 'v'}0"
        self.value_register = return_reg
        return mips

class ASTPostfixIncrementNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTPostfixIncrementNode, self).__init__(ctx=ctx)
        self.name = "post++"


class ASTPostfixDecrementNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTPostfixDecrementNode, self).__init__(ctx=ctx)
        self.name = "post--"


class ASTPrefixIncrementNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTPrefixIncrementNode, self).__init__(ctx=ctx)
        self.name = "pre++"


class ASTPrefixDecrementNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTPrefixDecrementNode, self).__init__(ctx=ctx)
        self.name = "pre--"


class ASTUnaryPlusNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTUnaryPlusNode, self).__init__(ctx=ctx)
        self.name = "+"

    def value(self):
        return self.identifier().value()


class ASTUnaryMinusNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTUnaryMinusNode, self).__init__(ctx=ctx)
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
    def __init__(self, ctx=None):
        super(ASTLogicalNotNode, self).__init__(ctx=ctx)
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
    def __init__(self, ctx=None):
        super(ASTIndirectionNode, self).__init__(ctx=ctx)

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

    def exit_mips_text(self):
        mips = ""

        float_type = self.type() == "float"
        store_op = "swc1" if float_type else "sw"
        load_op = "lwc1" if float_type else "lw"

        allocator = self.get_allocator()
        reg, spilled = allocator.allocate_next_register(float_type)
        if spilled:
                mips += f"{store_op} {reg}, {allocator.spilled_regs[reg]}\n"

        mem_addr = self.identifier().value_register or allocator.get_memory_address(self.identifier().identifier, self.scope)
        mips += f"{load_op} {reg}, {mem_addr}\n"
        mips += f"{load_op} {reg}, ({reg})\n"
        self.value_register = reg
        return mips


class ASTAddressOfNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTAddressOfNode, self).__init__(ctx=ctx)

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

    def exit_mips_text(self):
        if isinstance(self.parent, ASTFunctionCallNode) and self.parent.identifier().identifier == "scanf":
            return ""

        mips = ""

        float_type = self.type() == "float"
        store_op = "swc1" if float_type else "sw"
        load_op = "lwc1" if float_type else "lw"

        allocator = self.get_allocator()
        reg, spilled = allocator.allocate_next_register(float_type)
        if spilled:
                mips += f"{store_op} {reg}, {allocator.spilled_regs[reg]}\n"

        mem_addr = allocator.get_memory_address(self.identifier().identifier, self.scope)
        mips += f"la {reg}, {mem_addr}\n"
        self.value_register = reg
        return mips


class ASTCastNode(ASTUnaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTCastNode, self).__init__(ctx=ctx)

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
    def __init__(self, c_idx = None, ctx=None):
        super(ASTBinaryExpressionNode, self).__init__(ctx=ctx)
        self.c_idx = c_idx

    def left(self):
        return self.children[0]

    def right(self):
        return self.children[1]

    def type(self):
        return get_expression_type(self)

    def float_op(self):
        lhs = self.left().type() == "float"
        rhs = self.right().type() == "float"

        if isinstance(self.left(), ASTBinaryExpressionNode):
            lhs = self.left().float_op()

        if isinstance(self.right(), ASTBinaryExpressionNode):
            rhs = self.right().float_op()

        result = lhs or rhs
        return result

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
    def __init__(self, ctx=None):
        super(ASTAssignmentNode, self).__init__(ctx=ctx)
        self.name = "="

    def type(self):
        return self.left().type()

    def identifier(self):
        try:
            return self.left().identifier()
        except:
            return self.left()

    def value(self):
        return self.right().value()

    def optimise(self):
        ancestor = self.parent
        while ancestor is not None:
            if isinstance(ancestor, ASTIfStmtNode) or isinstance(ancestor, ASTWhileStmtNode) or isinstance(ancestor, ASTForStmtNode):
                # Do not optimize assignments inside conditionally executed code blocks
                # Reset symbol table value
                entry = self.scope.lookup(self.children[0].identifier)
                if entry:
                    entry.value = None
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

    def exit_mips_text(self):
        # Store variable in memory
        float_type = self.type() == "float"
        mips = ""

        source_reg = self.right().value_register
        store_op = "swc1" if float_type else "sw"
        load_op = "lwc1" if float_type else "lw"
        load_imm = "l.s" if float_type else "li"
        allocated = False
        if isinstance(self.right(), ASTConstantNode):
            allocated = True
            init_reg, spilled = self.get_allocator().allocate_next_register(float_type)
            init_value = self.right().value_register if float_type else self.right().value()
            if spilled:
                mips += f"{store_op} {init_reg}, {self.get_allocator().spilled_regs[init_reg]}\n"
            mips += f"{load_imm} {init_reg}, {init_value}\n"
            source_reg = init_reg
        elif isinstance(self.right(), ASTIdentifierNode):
            allocated = True
            id_reg, spilled = self.get_allocator().allocate_next_register(float_type)
            if spilled:
                mips += f"{store_op} {id_reg}, {self.get_allocator().spilled_regs[id_reg]}\n"
            mips += f"{load_op} {id_reg}, {self.get_allocator().get_memory_address(self.right().identifier, self.scope)}\n"
            source_reg = id_reg

        mem_addr = self.get_allocator().get_memory_address(self.identifier().identifier, self.scope)
        if isinstance(self.left(), ASTArrayAccessNode):
            mips += f"{store_op} {source_reg}, ({self.left().value_register})\n"
            mem_loc = self.get_allocator().deallocate_register(self.left().value_register, float_type)
            if mem_loc:
                mips += f"{load_op} {self.left().value_register}, {mem_loc}\n"
        else:
            mips += f"{store_op} {source_reg}, {mem_addr}\n"

        if allocated:
            memory_location = self.get_allocator().deallocate_register(source_reg, float_type)
            if memory_location:
                mips += f"{load_op} {source_reg}, {memory_location}\n"

        # Update Symbol Table
        entry = self.scope.lookup(self.identifier().identifier)
        entry.memory_location = mem_addr
        return mips

    def populate_symbol_table(self):
        # If the rhs is a constant, assign the symbol table value
        # Exception: in control flow bodies, set value to None
        cf_parent = self.parent
        while cf_parent:
            if isinstance(cf_parent, ASTIfStmtNode) or isinstance(cf_parent, ASTForStmtNode) or isinstance(cf_parent, ASTWhileStmtNode):
                entry = self.scope.lookup(self.children[0].identifier)
                if entry:
                    entry.value = None
                return
            cf_parent = cf_parent.parent

        if isinstance(self.children[1], ASTConstantNode):
            entry = self.scope.lookup(self.children[0].identifier)
            if entry:
                cf_parent = self.parent
                while cf_parent:
                    if isinstance(cf_parent, ASTIfStmtNode) or isinstance(cf_parent, ASTForStmtNode) or isinstance(cf_parent, ASTWhileStmtNode):
                        entry.value = None
                        return
                    cf_parent = cf_parent.parent
                entry.value = self.children[1].value()


class ASTMultiplicationNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx, ctx=None):
        super(ASTMultiplicationNode, self).__init__(c_idx, ctx=ctx)
        self.name = "*"

    def value(self):
        if self.left().value() and self.right().value():
            return self.left().value() * self.right().value()

    def optimise(self):
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
            self.propagate_constants()

        rhs = self.right().value() if isinstance(self.right(), ASTConstantNode) else None
        lhs = self.left().value() if isinstance(self.left(), ASTConstantNode) else None

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
        return generate_llvm_expr(self, "fmul" if self.type() == "float" else "        mul")

    def exit_mips_text(self):
        return generate_mips_expr(self, "mul.s" if self.type() == "float" else "mul")


class ASTDivisionNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx, ctx=None):
        super(ASTDivisionNode, self).__init__(c_idx, ctx=ctx)
        self.name = "/"

    def optimise(self):
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        return generate_mips_expr(self, "div.s" if self.type() == "float" else "div")


class ASTModuloNode(ASTBinaryExpressionNode):
    def __init__(self, c_idx, ctx=None):
        super(ASTModuloNode, self).__init__(c_idx, ctx=ctx)
        self.name = "%"

    def optimise(self):
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        return generate_mips_expr(self, "div.s" if self.type() == "float" else "div")


class ASTAdditionNode(ASTBinaryExpressionNode):
    def __init__(self,ctx=None):
        super(ASTAdditionNode, self).__init__(ctx=ctx)
        self.name = "+"

    def optimise(self):
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        return generate_mips_expr(self, "add.s" if self.type() == "float" else "add") 


class ASTSubtractionNode(ASTBinaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTSubtractionNode, self).__init__(ctx=ctx)
        self.name = "-"

    def optimise(self):
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        return generate_mips_expr(self, "sub.s" if self.type() == "float" else "sub")


class ASTLogicalNode(ASTBinaryExpressionNode):
    def __init__(self, ctx=None):
        super(ASTLogicalNode, self).__init__(ctx=ctx)
        self.name = "LogicalNode"

    def type(self):
        return "bool"


class ASTSmallerThanNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTSmallerThanNode, self).__init__(ctx=ctx)
        self.name = "<"

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        # Exception: Loop conditions
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        if self.float_op():
            return generate_mips_float_comp(self, "c.lt.s")
        else:
            return generate_mips_expr(self, "slt")


class ASTLargerThanNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTLargerThanNode, self).__init__(ctx=ctx)
        self.name = ">"
    
    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        if self.float_op():
            return generate_mips_float_comp(self, "c.gt.s")
        else:
            return generate_mips_expr(self, "sgt")


class ASTSmallerThanOrEqualNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTSmallerThanOrEqualNode, self).__init__(ctx=ctx)
        self.name = "<="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        if self.float_op():
            return generate_mips_float_comp(self, "c.le.s")
        else:
            return generate_mips_expr(self, "sle")


class ASTLargerThanOrEqualNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTLargerThanOrEqualNode, self).__init__(ctx=ctx)
        self.name = ">="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        if self.float_op():
            return generate_mips_float_comp(self, "c.ge.s")
        else:
            return generate_mips_expr(self, "sge")


class ASTEqualsNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTEqualsNode, self).__init__(ctx=ctx)
        self.name = "=="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        if self.float_op():
            return generate_mips_float_comp(self, "c.eq.s")
        else:
            return generate_mips_expr(self, "seq")


class ASTNotEqualsNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTNotEqualsNode, self).__init__(ctx=ctx)
        self.name = "!="

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        if self.float_op():
            return generate_mips_float_comp(self, "c.ne.s")
        else:
            return generate_mips_expr(self, "sne")


class ASTLogicalAndNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTLogicalAndNode, self).__init__(ctx=ctx)
        self.name = "&&"

    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        return generate_mips_expr(self, "and")


class ASTLogicalOrNode(ASTLogicalNode):
    def __init__(self, ctx=None):
        super(ASTLogicalOrNode, self).__init__(ctx=ctx)
        self.name = "||"
        
    def optimise(self):
        # If both children are constants, evaluate expression in compiler
        loop_parent = self.parent
        while loop_parent:
            if isinstance(loop_parent, ASTForCondNode) or isinstance(loop_parent, ASTWhileCondNode) \
                or isinstance(loop_parent, ASTForUpdaterNode):
                break
            loop_parent = loop_parent.parent
        if not loop_parent:
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

    def exit_mips_text(self):
        return generate_mips_expr(self, "or")


class ASTDeclarationNode(ASTBaseNode):
    def __init__(self, c_idx = None, ctx=None):
        super(ASTDeclarationNode, self).__init__(ctx=ctx)
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

    def enter_mips_data(self):
        if not self.scope.depth:
            return f"{self.identifier().identifier}: {c2mips_type(self.type())} {self.initializer().value()}\n"
        else:
            return ""

    def exit_mips_text(self):
        if not self.scope.depth:
            return ""

        if self.type() == "char*":
            self.scope.lookup(self.identifier().identifier).register = self.initializer().value_register
            return ""

        mips = ""
        allocator = self.get_allocator()
        float_type = self.type() == "float"

        store_op = "swc1" if float_type else "sw"
        load_op = "lwc1" if float_type else "lw"
        load_imm = "l.s" if float_type else "li"
        mem_addr = self.get_allocator().get_memory_address(self.identifier().identifier, self.scope)

        if isinstance(self.children[1], ASTArrayDeclarationNode):
            array_len = self.scope.lookup(self.identifier().identifier).size
            for idx, init in enumerate(self.children[2:]):
                if idx >= array_len:
                    break
                # initialize array
                reg, spilled = allocator.allocate_next_register(float_type)
                if spilled:
                    mips += f"{store_op} {reg}, {allocator.spilled_regs[reg]}\n"
                mips += f"{load_imm} {reg}, {init.value()}\n"
                mips += f"{store_op} {reg}, {allocator.get_memory_address(self.identifier().identifier, self.scope, idx)}\n"
                memory_location = allocator.deallocate_register(reg, float_type)
                if memory_location:
                    mips += f"{load_op} {reg}, {memory_location}\n"
        else:
            if self.initializer():
                # This variable is initialized
                # Store variable in memory
                source_reg = self.initializer().value_register
                allocated = False
                if isinstance(self.initializer(), ASTConstantNode):
                    allocated = True
                    init_reg, spilled = self.get_allocator().allocate_next_register(float_type)
                    init_value = self.initializer().value_register if float_type else self.initializer().value()
                    if spilled:
                        mips += f"{store_op} {init_reg}, {self.get_allocator().spilled_regs[init_reg]}\n"
                    mips += f"{load_imm} {init_reg}, {init_value}\n"
                    source_reg = init_reg

                elif isinstance(self.initializer(), ASTIdentifierNode):
                    allocated = True
                    id_reg, spilled = self.get_allocator().allocate_next_register(float_type)
                    if spilled:
                        mips += f"{store_op} {id_reg}, {self.get_allocator().spilled_regs[id_reg]}\n"
                    mips += f"{load_op} {id_reg}, {self.get_allocator().get_memory_address(self.initializer().identifier, self.scope)}\n"
                    source_reg = id_reg
                elif isinstance(self.initializer(), ASTArrayAccessNode):
                    allocated = True
                    source_reg, spilled = self.get_allocator().allocate_next_register(float_type)
                    if spilled:
                        mips += f"{store_op} {source_reg}, {self.get_allocator().spilled_regs[source_reg]}\n"
                    mips += f"{load_op} {source_reg}, ({self.initializer().value_register})\n"
                    mem_loc = self.get_allocator().deallocate_register(self.initializer().value_register, float_type)
                    if mem_loc:
                        mips += f"{load_op} {self.initializer().value_register}, {mem_loc}\n"
                elif isinstance(self.initializer(), ASTExpressionNode) and not isinstance(self.initializer(), ASTFunctionCallNode):
                    allocated = True

                mips += f"{store_op} {source_reg}, {mem_addr}\n"

                if allocated:
                    memory_location = self.get_allocator().deallocate_register(source_reg, float_type)
                    if memory_location:
                        mips += f"{load_op} {source_reg}, {memory_location}\n"

        # Update Symbol Table
        entry = self.scope.lookup(self.identifier().identifier)
        entry.memory_location = mem_addr

        return mips


    def optimise(self):
        STEntry = self.scope.lookup(self.identifier().identifier)
        if STEntry:
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
            if self.line_info:
                logging.error(f"line {self.line_info[0]}:{self.line_info[1]} The variable '{identifier}' was redeclared")
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
    def __init__(self, name,ctx=None):
        super(ASTLabelStmtNode, self).__init__(name, ctx=ctx)


class ASTCaseStmtNode(ASTBaseNode):
    def __init__(self, name, ctx=None):
        super(ASTCaseStmtNode, self).__init__(name, ctx=ctx)


class ASTDefaultStmtNode(ASTBaseNode):
    def __init__(self, name, ctx=None):
        super(ASTDefaultStmtNode, self).__init__(ctx=ctx)


class ASTIfStmtNode(ASTBaseNode):

    if_counter = 0

    def __init__(self, ctx=None):
        super(ASTIfStmtNode, self).__init__(ctx=ctx)
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

    def enter_mips_text(self):
        ASTIfStmtNode.if_counter += 1
        mips = "\n"
        return mips

    def exit_mips_text(self):
        mips = f"{self.finish_label}:\n"
        return mips


class ASTIfConditionNode(ASTBaseNode):
    def __init__(self, ctx=None):
        super(ASTIfConditionNode, self).__init__(ctx=ctx)
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

    def exit_mips_text(self):
        # Get register with condition and jump to label

        cond_register = self.children[0].value_register
        mips = ""
        float_type = self.children[0].type() == "float"
        load_op = "lw"
        flag_jump_on = "f"
        if isinstance(self.children[0], ASTBinaryExpressionNode):
            float_type = self.children[0].float_op()

        if isinstance(self.children[0], ASTConstantNode):
            # Load constant into register (can be saved as int, bool value resolved by compiler)
            float_type = False # This constant is always treated as an int
            value = 1 if self.children[0].value != 0 else 0
            cond_register, spilled = self.get_allocator().allocate_next_register(float_type)
            if spilled:
                mips += f"sw {cond_register}, {self.get_allocator().spilled_regs[cond_register]}\n"
            mips += f"li {cond_register} {value}\n"
        elif isinstance(self.children[0], ASTIdentifierNode):
            # Load variable from memory into register
            if float_type:
                # Generate comparison to set flag
                compare_node = ASTEqualsNode()
                compare_node.parent = self
                compare_node.scope = self.scope
                zero_node = ASTConstantNode(0.0, "float")
                zero_node.parent = compare_node
                zero_node.scope = self.scope
                zero_node.value_register = "zero_float"
                compare_node.children = [self.children[0], zero_node]
                mips += generate_mips_float_comp(compare_node, "c.eq.s")
                flag_jump_on = "t"
            else:
                memory_address = self.get_allocator().get_memory_address(self.children[0].identifier, self.scope)
                cond_register, spilled = self.get_allocator().allocate_next_register(float_type)
                if spilled:
                    mips += f"sw {cond_register}, {self.get_allocator().spilled_regs[cond_register]}\n"
                mips += f"lw {cond_register}, {memory_address}\n"

        # Set labels
        if float_type:
            self.parent.cond_register = cond_register # Will be used to deallocate afterwards
        self.parent.false_label = f"IfFalse{ASTIfStmtNode.if_counter}"
        self.parent.finish_label = f"IfEnd{ASTIfStmtNode.if_counter}"

        # MIPS has falltrough: branch to false label if condition is 0
        if float_type:
            mips += f"bc1{flag_jump_on} {self.parent.false_label}\n"
        else:
            mips += f"beq {cond_register}, $0, {self.parent.false_label}\n"
        
        return mips



class ASTIfTrueNode(ASTBaseNode):
    def __init__(self, ctx=None):
        super(ASTIfTrueNode, self).__init__(ctx=ctx)
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

    def enter_mips_text(self):
        mips = "\n" # readability
        # Deallocate condition register (if it exists, the condition wasn't float)
        cond_reg = self.parent.cond_register
        if cond_reg:
            memory_address = self.get_allocator().deallocate_register(cond_reg, False)
            if memory_address:
                mips += f"lw {cond_reg}, {memory_address}\n"
        return mips

    def exit_mips_text(self):
        mips = f"j {self.parent.finish_label}\n\n"
        mips += f"{self.parent.false_label}:\n"
        return mips


class ASTIfFalseNode(ASTBaseNode):
    def __init__(self, ctx=None):
        super(ASTIfFalseNode, self).__init__(ctx=ctx)
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

    def enter_mips_text(self):
        mips = ""
        # Deallocate condition register
        cond_reg = self.parent.cond_register
        if cond_reg:
            memory_address = self.get_allocator().deallocate_register(cond_reg, False)
            if memory_address:
                mips += f"lw {cond_reg}, {memory_address}\n"
        return mips

    def exit_mips_text(self):
        mips = "\n"  # readability
        return mips


class ASTSwitchStmtNode(ASTBaseNode):
    def __init__(self, ctx=None):
        super(ASTSwitchStmtNode, self).__init__(ctx=ctx)
        self.name = "Switch"


class ASTWhileStmtNode(ASTBaseNode):

    while_counter = 0

    def __init__(self, name="While", ctx=None):
        super(ASTWhileStmtNode, self).__init__(name, ctx=ctx)
        self.cond_label = None
        self.true_label = None
        self.finish_label = None
        self.cond_register = None

    def optimise(self):
        # If condition is a constant and false, delete this node
        cond_node = self.children[0]
        if len(cond_node.children) == 1 and isinstance(cond_node.children[0], ASTConstantNode):
            if cond_node.children[0].value() == 0:
                self.parent.children.pop(self.parent.children.index(self))

    def exit_llvm_text(self):
        # Set outer scope counter to scope counter
        self.parent.scope.temp_register = self.scope.temp_register

        llvmir = f"\n{self.finish_label}:\n"
        return llvmir

    def enter_mips_text(self):
        ASTWhileStmtNode.while_counter += 1
        return ""

    def exit_mips_text(self):
        mips = ""
        mips += f"\n{self.finish_label}:\n"
        # Deallocate condition register
        if self.cond_register:
            memory_location = self.get_allocator().deallocate_register(self.cond_register[0], self.cond_register[1])
            if memory_location:
                load_op = "lwc1" if self.cond_register[1] else "lw"
                mips += f"{load_op} {self.cond_register[0]}, {memory_location}\n\n"
        return mips


class ASTWhileCondNode(ASTWhileStmtNode):

    def __init__(self, ctx=None):
        super(ASTWhileCondNode, self).__init__("WhileCond", ctx=ctx)

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

    def enter_mips_text(self):
        # Set labels
        self.parent.cond_label = f"WhileCond{ASTWhileStmtNode.while_counter}"
        self.parent.finish_label = f"WhileEnd{ASTWhileStmtNode.while_counter}"
        mips = f"\n{self.parent.cond_label}:\n"
        return mips

    def exit_mips_text(self):
        # Branch on condition

        mips = ""
        float_type = self.children[0].type() == "float"
        if isinstance(self.children[0], ASTBinaryExpressionNode):
            float_type = self.children[0].float_op()
        load_op = "lwc1" if float_type else "lw"
        value_register = self.children[0].value_register
        allocated = False
        flag_jump_on = "f"
        if isinstance(self.children[0], ASTConstantNode):
            # Jump if condition is 0, else fall through
            value = self.children[0].value
            if value == 0:
                return f"j {self.parent.finish_label}\n"
            return ""
        if isinstance(self.children[0], ASTIdentifierNode):
            # Load variable from memory
            if float_type:
                # Generate comparison to set flag
                compare_node = ASTEqualsNode()
                compare_node.scope = self.scope
                compare_node.parent = self
                zero_node = ASTConstantNode(0.0, "float")
                zero_node.parent = compare_node
                zero_node.scope = self.scope
                zero_node.value_register = "zero_float"
                compare_node.children = [self.children[0], zero_node]
                mips += generate_mips_float_comp(compare_node, "c.eq.s")
                flag_jump_on = "t"
            else:
                allocated = True
                value_register, spilled = self.get_allocator().allocate_next_register(float_type)
                if spilled:
                    mips += f"sw {value_register}, {self.get_allocator().spilled_regs[value_register]}\n"
                self.parent.cond_register = (value_register, float_type)
                memory_location = self.get_allocator().get_memory_address(self.children[0].identifier, self.scope)
                mips += f"{load_op} {value_register}, {memory_location}\n"

        if float_type:
            mips += f"bc1{flag_jump_on} {self.parent.finish_label}\n\n"
        else:
            mips += f"beq {value_register}, $0, {self.parent.finish_label}\n\n"
        
        # Deallocate value register
        if allocated:
            memory_location = self.get_allocator().deallocate_register(value_register, float_type)
            if memory_location:
                mips += f"{load_op} {value_register}, {memory_location}\n"
        return mips


class ASTWhileTrueNode(ASTWhileStmtNode):
    def __init__(self, ctx=None):
        super(ASTWhileTrueNode, self).__init__("WhileTrue", ctx=ctx)

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

    def exit_mips_text(self):
        mips = f"j {self.parent.cond_label}\n"
        return mips


class ASTForStmtNode(ASTBaseNode):

    for_counter = 0

    def __init__(self, name="For", ctx=None):
        super(ASTForStmtNode, self).__init__(name, ctx=ctx)
        self.cond_register = None
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

    def enter_mips_text(self):
        ASTForStmtNode.for_counter += 1
        return ""

    def exit_mips_text(self):
        mips = f"\n{self.finish_label}:\n"
        if self.cond_register:
            # Deallocate if necessary, can only be int
            memory_location = self.get_allocator().deallocate_register(self.cond_register)
            if memory_location:
                mips += f"lw {self.cond_register}, {memory_location}\n"

        return mips


class ASTForInitNode(ASTForStmtNode):
    def __init__(self, ctx=None):
        super(ASTForInitNode, self).__init__("ForInit", ctx=ctx)

    def enter_llvm_text(self):
        # Newline for readability
        llvmir = "\n"
        return llvmir
    
    def exit_llvm_text(self):
        # Override parent method because this returns nothing
        return ""

    def enter_mips_text(self):
        mips = "\n"
        return mips
    
    def exit_mips_text(self):
        return ""


class ASTForCondNode(ASTForStmtNode):
    def __init__(self, ctx=None):
        super(ASTForCondNode, self).__init__("ForCond", ctx=ctx)

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

    def enter_mips_text(self):
        self.parent.cond_label = f"ForCond{ASTForStmtNode.for_counter}"
        self.parent.finish_label = f"ForEnd{ASTForStmtNode.for_counter}"
        mips = f"{self.parent.cond_label}:\n"
        return mips

    def exit_mips_text(self):
        # Evaluate condition and branch if false
        mips = ""
        value_register = self.children[0].value_register
        float_type = self.children[0].type() == "float"
        if isinstance(self.children[0], ASTBinaryExpressionNode):
            float_type = self.children[0].float_op()
        flag_jump_on = "f"
        allocated = False


        if isinstance(self.children[0], ASTConstantNode):
            # This shouldn't technically be possible
            # Jump if 0, else fallthrough
            value = self.children[0].value
            if value == 0:
                return f"j {self.parent.finish_label}\n"
        if isinstance(self.children[0], ASTIdentifierNode):
            # Load variable from memory
            if float_type:
                # Generate comparison to set flag
                compare_node = ASTEqualsNode()
                compare_node.scope = self.scope
                compare_node.parent = self
                zero_node = ASTConstantNode(0.0, "float")
                zero_node.parent = compare_node
                zero_node.scope = self.scope
                zero_node.value_register = "zero_float"
                compare_node.children = [self.children[0], zero_node]
                mips += generate_mips_float_comp(compare_node, "c.eq.s")
                flag_jump_on = "t"
            else:
                allocated = True
                value_register, spilled = self.get_allocator().allocate_next_register(float_type)
                if spilled:
                    mips += f"sw {value_register}, {self.get_allocator().spilled_regs[value_register]}\n"
                self.parent.cond_register = value_register
                memory_location = self.get_allocator().get_memory_address(self.children[0].identifier, self.scope)
                mips += f"lw {value_register}, {memory_location}\n"

        if float_type:
            mips += f"bc1{flag_jump_on} {self.parent.finish_label}\n\n"
        else:
            mips += f"beq {value_register}, $0, {self.parent.finish_label}\n\n"

        if allocated:
            memory_location = self.get_allocator().deallocate_register(value_register, float_type)
            if memory_location:
                mips += f"lw {value_register}, {memory_location}\n"            

        return mips


class ASTForUpdaterNode(ASTForStmtNode):
    def __init__(self, ctx=None):
        super(ASTForUpdaterNode, self).__init__("ForUpdater", ctx=ctx)

    def enter_llvm_text(self):

        llvmir = f"{self.parent.updater_label}:\n"
        return llvmir

    def exit_llvm_text(self):

        llvmir = f"br label %{self.parent.cond_label}\n"
        return llvmir

    def enter_mips_text(self):
        # Override parent method
        return ""

    def exit_mips_text(self):
        return ""


class ASTForTrueNode(ASTForStmtNode):
    def __init__(self, ctx=None):
        super(ASTForTrueNode, self).__init__("ForTrue", ctx=ctx)

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

    def exit_mips_text(self):
        mips = f"j {self.parent.cond_label}\n"
        return mips


class ASTGotoNode(ASTBaseNode):
    def __init__(self, ctx=None):
        super(ASTGotoNode, self).__init__(ctx=ctx)


class ASTContinueNode(ASTBaseNode):
    def __init__(self, c_idx = None, ctx=None):
        super(ASTContinueNode, self).__init__(ctx=ctx)
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

    def exit_mips_text(self):
        # Get loop parent & jump to condition label
        loop_parent = self.parent
        while not (isinstance(loop_parent, ASTWhileStmtNode) or isinstance(loop_parent, ASTForStmtNode)):
            loop_parent = loop_parent.parent

        mips = f"j {loop_parent.cond_label}\n"
        return mips
    
    def optimise(self):
        # Prune siblings that come after this continue
        if self.c_idx is not None:
            self.parent.children = self.parent.children[:self.c_idx+1]


class ASTBreakNode(ASTBaseNode):
    def __init__(self, c_idx = None, ctx=None):
        super(ASTBreakNode, self).__init__(ctx=ctx)
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

    def exit_mips_text(self):
        # Get loop parent & jump to finish label
        loop_parent = self.parent
        while not (isinstance(loop_parent, ASTWhileStmtNode) or isinstance(loop_parent, ASTForStmtNode)):
            loop_parent = loop_parent.parent
        
        mips = f"j {loop_parent.finish_label}\n"
        return mips
    
    def optimise(self):
        # Prune siblings that come after this break
        if self.c_idx is not None:
            self.parent.children = self.parent.children[:self.c_idx+1]


class ASTReturnNode(ASTBaseNode):
    def __init__(self, c_idx, ctx=None):
        super(ASTReturnNode, self).__init__(ctx=ctx)
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

    def exit_mips_text(self):
        # Set $v0 to return value
        mips = ""
        float_type = self.type() == "float"
        move_op = "mfc1" if float_type else "move"
        load_op = "lwc1" if float_type else "lw"
        value_register = self.children[0].value_register
        allocated = False
        if isinstance(self.children[0], ASTConstantNode):
            # Load constant into register
            allocated = True
            value_register, spilled = self.get_allocator().allocate_next_register(float_type)
            target_value = self.children[0].value() if not float_type else self.children[0].value_register
            load_op = "li" if not float_type else "l.s"
            mips += f"{load_op} {value_register}, {target_value}\n"
        if isinstance(self.children[0], ASTIdentifierNode):
            # Load variable from memory into register
            allocated = True
            value_register, spilled = self.get_allocator().allocate_next_register(float_type)
            memory_address = self.get_allocator().get_memory_address(self.children[0].identifier, self.scope)
            mips += f"{load_op} {value_register}, {memory_address}\n"
        
        return_reg = f"${'f' if float_type else 'v'}0"
        mips += f"{move_op} {return_reg}, {value_register}\n"

        if allocated:
            memory_location = self.get_allocator().deallocate_register(value_register, float_type)
            if memory_location:
                mips += f"{load_op} {value_register}, {memory_location}\n"

        return mips

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
    def __init__(self, ctx=None):
        super(ASTCompoundStmtNode, self).__init__(ctx=ctx)
        self.name = "CompoundStmt"


class ASTFunctionDefinitionNode(ASTBaseNode):
    def __init__(self, allocator=None, ctx=None):
        super(ASTFunctionDefinitionNode, self).__init__(ctx=ctx)
        self.name = "FuncDef"
        self.allocator = allocator

    def get_allocator(self):
        return self.allocator

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

    def enter_mips_text(self):
        self.allocator.min_frame_size = (1 + self.scope.variable_count()) * 4
        mips = ""
        mips += f"fun_{self.identifier().identifier}:\n"
        mips += f"sw $fp, 0($sp)\n"
        mips += f"move $fp, $sp\n"
        mips += f"add $sp, $sp, 4\n"
        mips += f"sw $ra, 0($sp)\n"
        mips += f"add $sp, $sp, {self.allocator.min_frame_size}\n"

        # Prepare arguments
        args = self.arguments()[1::2]
        for i, arg in enumerate(args):
            float_type = arg.type() == 'float'
            store_op = "swc1" if float_type else "sw"
            load_op = "lwc1" if float_type else "lw"
            arg_reg = '$f12' if float_type else '$a0'
            if i < 4:
                arg_reg = f"${'f' if float_type else 'a'}{i + 12 if float_type else i}"
            else:
                mips += f"{load_op} {arg_reg}, -{(len(args) - i) * 4}($fp)\n"
            mips += f"{store_op} {arg_reg}, {self.allocator.get_memory_address(arg.identifier, self.scope)}\n"

        mips += "\n" #readability
        return mips

    def exit_mips_text(self):
        mips = "\n"
        if not self.identifier().identifier == "main":
            mips += "lw $ra, 4($fp)\n"
            mips += "move $sp, $fp\n"
            mips += "lw $fp, 0($fp)\n"
            mips += "jr $ra\n"
        else:
            # Special case: main function closes program
            # First move return value from the standard register of $v0 to $a0
            mips += "move $a0, $v0\n"
            mips += "li $v0, 17\n"
            mips += "syscall\n"
        mips += "\n" #readability
        return mips

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
    def __init__(self, ctx=None):
        super(ASTParameterTypeList, self).__init__(ctx=ctx)
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
    def __init__(self, tspec, ctx=None):
        super(ASTTypeSpecifierNode, self).__init__(ctx=ctx)
        self.tspec = tspec
        self.name = "Type:" + str(tspec)

    def type(self):
        return self.tspec


class ASTExprListNode(ASTBaseNode):
    def __init__(self, name, ctx=None):
        super(ASTExprListNode, self).__init__(name, ctx=ctx)


class ASTArrayDeclarationNode(ASTBaseNode):
    def __init__(self, ctx=None):
        super(ASTArrayDeclarationNode, self).__init__(ctx=ctx)
        self.name = "ArrayDecl"
        self.value_register = None

    def populate_symbol_table(self):
        scope = self.scope.scope_level(self.identifier().identifier)
        self.value_register = f"%{self.identifier().identifier}.scope{scope}" if scope else f"@{self.identifier().identifier}"
        self.scope.lookup(self.identifier().identifier).size = self.children[1].value()

    def identifier(self):
        if isinstance(self.children[0], ASTArrayDeclarationNode):
            # We're working with a multidimensional array and we're not the first dimension
            return self.children[0].identifier()
        else:
            # 1D array
            return self.children[0]


