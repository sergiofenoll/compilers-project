"""
Module representing the structure of a tree of symbol tables
"""


class STTNode:
    def __init__(self):
        self.parent = None
        self.children = []
        self.table = dict()
        self.name = "Symbol Table"

        # Maintenance variable for dotfile generation
        self.__num = 0

    def lookup(self, name):
        # Searches for name in scope & ancestors of scope. If found, return entry. If not found, return None

        if name in self.table:
            return self.table[name]
        else:
            scope = self
            while scope.parent is not None:
                scope = scope.parent
                if name in scope.table:
                    return scope.table[name]
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

        entries = "\n".join(entry.dotRepresentation() for entry in self.table.values())
        header = '''
        <tr>
            <td border="1">Identifier</td>
            <td border="1">Type</td>
            <td border="1">Arguments</td>
        </tr>''' if len(entries) else ''

        table = f'''  node{ncount}
        [shape=none
        label=<<table border="0" cellspacing="0">
            <tr><td border="1" colspan="3">{self.name}</td></tr>
            {header}
            {entries}
        </table>>
        ]'''
        output.write(table)
        self.__num = ncount
        ncount += 1
        while queue:
            node = queue.pop(0)
            for child in node.children:
                entries = "\n".join(entry.dotRepresentation() for entry in child.table.values())
                header = '''
                <tr>
                    <td border="1">Identifier</td>
                    <td border="1">Type</td>
                    <td border="1">Arguments</td>
                </tr>''' if len(entries) else ''

                table = f'''  node{ncount}
                        [shape=none
                        label=<<table border="0" cellspacing="0">
                            <tr><td border="1" colspan="3">{node.name}</td></tr>
                            {header}
                            {entries}
                        </table>>
                        ]'''
                output.write(table)
                child.__num = ncount
                ncount += 1
                output.write('  node{} -> node{}\n'.format(node.__num, child.__num))
                queue.append(child)

        output.write("}")


class STTEntry:
    def __init__(self, identifier, type_desc, args=None, value=None, used=False):
        self.identifier = identifier
        self.type_desc = type_desc
        self.args = args or []
        self.value = value
        self.used = True

    def dotRepresentation(self):
        return f'''
        <tr>
            <td border="1">{self.identifier}</td>
            <td border="1">{self.type_desc}</td>
            <td border="1">{", ".join(arg for arg in self.args)}</td>
        </tr>'''

    def __repr__(self):
        r = "{} | {} | {} | {}".format(self.identifier, self.type_desc, self.args, self.value)
        return r