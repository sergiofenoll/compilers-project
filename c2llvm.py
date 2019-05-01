import os
import sys
import logging
import AST.AST as AST
import AST.STT as STT
from AST.ASTBuilderListener import ASTBuilder
from antlr4 import *
from parser.CLexer import CLexer
from parser.CParser import CParser

logging.basicConfig(format='[%(levelname)s] %(message)s')


def optimise_ast(ast):

    # Applies the following optimisations where possible:
    #   - Remove code that comes after return, break or continue
    #   - Remove declarations for unused variables
    #   - Fold constants
    #   - Remove useless code: arithmetic expressions that evaluate to known values

    stack = list()
    queue = list()
    queue.append(ast)

    while queue:
        node = queue.pop(0)
        stack.append(node)
        for child in node.children[::-1]:
            queue.append(child)
    
    while stack:
        node = stack.pop()
        node.optimise()


def generate_llvm_ir(ast, output):
    stack = list()
    parent_stack = list()
    stack.append(ast)
    data = ""
    text = ""
    while stack:
        node = stack.pop()

        data += node.enter_llvm_data()
        text += node.enter_llvm_text()

        parent_stack.append(node)
        for child in node.children[::-1]:
            stack.append(child)
        while parent_stack:
            last_parent = parent_stack[-1]
            if not last_parent.children or last_parent.children[-1] == node:
                node = parent_stack.pop()

                data += node.exit_llvm_data()
                text += node.exit_llvm_text()

            else:
                break
    output.write(str(data) + "\n" + str(text))


def type_checking(ast):
    stack = list()
    stack.append(ast)

    while stack:
        node = stack.pop()
        node.type()
        for child in node.children:
            stack.append(child)


def populate_symbol_table(ast):
    queue = list()
    queue.append(ast)

    while queue:
        node = queue.pop(0)
        node.populate_symbol_table()
        for child in node.children:
            queue.append(child)


def main(argv):
    input_filepath = None
    try:
        input_filepath = argv[1]
    except IndexError:
        logging.error("No C source files provided")
        exit()

    try:
        output_dir = os.path.dirname(argv[2])
        output_llvm = argv[2]
        output_filename = output_llvm.split("/")[-1].rsplit(".", 1)[0]
    except IndexError:
        output_filename = input_filepath.split("/")[-1].rsplit(".", 1)[0]
        output_dir = os.path.dirname(argv[1])
        output_llvm = os.path.join(output_dir, output_filename + ".ll")

    output_ast = os.path.join(output_dir, output_filename + ".ast.dot")
    output_stt = os.path.join(output_dir, output_filename + ".stt.dot")

    input_stream = None
    try:
        input_stream = FileStream(input_filepath)
    except FileNotFoundError:
        logging.error(f"File {input_filepath} was not found")
        exit()
    lexer = CLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)

    tree = parser.compilationUnit()

    stt = STT.STTNode()
    ast = AST.ASTBaseNode("Root", stt)

    try:
        builder = ASTBuilder(ast)
        walker = ParseTreeWalker()
        walker.walk(builder, tree)
    except Exception as e:
        logging.error(f"{type(e)}: {e}")
        raise e

    populate_symbol_table(ast)
    type_checking(ast)
    optimise_ast(ast)

    with open(output_ast, "w") as astf:
        ast.generateDot(astf)
    with open(output_stt, "w") as sttf:
        stt.generateDot(sttf)
    with open(output_llvm, mode="wt", encoding="utf-8") as irf:
        generate_llvm_ir(ast, irf)


if __name__ == '__main__':
    main(sys.argv)
