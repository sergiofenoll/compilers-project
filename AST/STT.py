"""
Module representing the structure of a tree of symbol tables
"""


class STTNode:
    def __init__(self):
        self.parent = None
        self.children = []
        self.table = dict()
        self.name = "Symbol Table"


class STTEntry:
    def __init__(self, identifier, type_desc):
        self.identifier = identifier
        self.type_desc = type_desc
