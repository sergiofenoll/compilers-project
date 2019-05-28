"""
Module representing the structure of a tree of symbol tables
"""


class STTNode:
    def __init__(self, name=None):
        self.parent = None
        self.children = []
        self.table = dict()
        self.name = name or "Symbol Table"
        self.depth = 0
        self.temp_register = 0

        # Maintenance variable for dotfile generation
        self.__num = 0
        self.__dot_header = """
                digraph astgraph {
                  node [shape=none, fontsize=12, fontname="Courier", height=.1];
                  ranksep=.3;
                  edge [arrowsize=.5]
                """
        self.__table_header = """
                <tr>
                    <td border="1">Identifier</td>
                    <td border="1">Type</td>
                    <td border="1">Arguments</td>
                    <td border="1">Value</td>
                    <td border="1">Used</td>
                </tr>
                """

    def lookup(self, name):
        # Searches for name in scope & ancestors of scope. If found, return entry. If not found, return None

        if name in self.table:
            return self.table[name]
        else:
            scope = self
            while scope.parent:
                scope = scope.parent
                if name in scope.table:
                    return scope.table[name]
        return None

    def scope_level(self, name):
        if name in self.table:
            return self.depth
        else:
            scope = self
            while scope.parent:
                scope = scope.parent
                if name in scope.table:
                    return scope.depth
        return None

    def generateDot(self, output):
        output.write(self.__dot_header)
        ncount = 1
        queue = list()
        queue.append(self)

        entries = "\n".join(entry.dotRepresentation() for entry in self.table.values())

        table = f"""
        node{ncount}
        [label=<<table border="0" cellspacing="0">
            <tr><td border="1" colspan="5">{self.name} scope {self.depth}</td></tr>
            {self.__table_header if len(entries) else ''}
            {entries}
        </table>>]"""
        output.write(table)
        self.__num = ncount
        ncount += 1
        while queue:
            node = queue.pop(0)
            for child in node.children:
                entries = "\n".join(entry.dotRepresentation() for entry in child.table.values())
                table = f"""
                        node{ncount}
                        [label=<<table border="0" cellspacing="0">
                            <tr><td border="1" colspan="5">{node.name} scope {node.depth}</td></tr>
                            {self.__table_header if len(entries) else ''}
                            {entries}
                        </table>>]"""
                output.write(table)
                child.__num = ncount
                ncount += 1
                output.write('  node{} -> node{}\n'.format(node.__num, child.__num))
                queue.append(child)

        output.write("}")


class STTEntry:
    def __init__(self, identifier, type_desc, args=None, value=None, used=False, register=None):
        self.identifier = identifier
        self.type_desc = type_desc
        self.args = args or []
        self.value = value
        self.used = used
        self.memory_location = None

        # LLVM register maintenance
        self.register = register
        self.aux_register = None  # Used by arrays with expressions, required by LLVM
        self.aux_type = None


    def dotRepresentation(self):
        return f"""
        <tr>
            <td border="1">{self.identifier}</td>
            <td border="1">{self.type_desc}</td>
            <td border="1">{", ".join(arg for arg in self.args)}</td>
            <td border="1">{self.value if self.value is not None else ''}</td>
            <td border="1">{self.used}</td>
        </tr>"""

    def __repr__(self):
        return "{} | {} | {} | {}".format(self.identifier, self.type_desc, self.args, self.value)
