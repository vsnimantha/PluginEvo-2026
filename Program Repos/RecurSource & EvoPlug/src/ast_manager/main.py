from src.ast_manager.code_to_ast.ast_parser import ASTParser
# from ast_to_code import ASTReconstructor
# from Genetic_Programming_Module.src.AST_Manager.ast_to_code_clang import emit_translation_unit
# from LLM.ast_to_code_gorq import ast_to_code
from src.ast_manager.visualiser.visualiser import visualize_clang_ast
from src.ast_manager.cross_over_experiment import subtree_crossover,json_to_astnode,print_ast
# from Genetic_Programming_Module.src.AST_Manager.ast_to_code import emit_translation_unit 
from src.ast_manager.ast_to_code.ast_to_code_parser import emit_translation_unit 
import json


def test():
    source_path = "Genetic_Programming_Module/Test/C_Programs/example_1.c"  # Make sure this path is correct
    parser = ASTParser(source_path)
    
    print(f"\n🔍 Parsing AST for: {source_path}")
    root = parser.parse(False)
    
    if not root:
        print("⚠️ Failed to generate AST.")
        return
    

    print("\n🌳 Original AST Structure:")
    parser.dump_ast(root)
    parser.save_ast_json_to_file(root, print_to_console=True,output_file="ast.json")
 

    #visualize the AST
    # print("\n📊 Visualizing AST:")
    # ast_string=parser.ast_to_string(root)
    # visualize_clang_ast(ast_string, output_file='clang_ast')

    # Reconstruct code from AST root
    print("\n🛠️ Reconstructing C Code:")
    code = emit_translation_unit(root)
    print("\n📝 Reconstructed C Code:")
    print(code)

    #LLM
    # ast_lines=parser.ast_to_string(root)
    # print("\n📝 AST as String:")
    # ast_string="\n".join(ast_lines)
    # ast_to_code_llm(ast_string)

    # Crossover experiment
def test_crossover():
 # File paths to your source C programs
    source_path1 = "Test/C_Programs/example_1.c"
    source_path2 = "Test/C_Programs/example_2.c"

    parser1 = ASTParser(source_path1)
    parser2 = ASTParser(source_path2)

    root1 = parser1.parse(False)
    root2 = parser2.parse(False)

    if not root1 or not root2:
        print("⚠️ Failed to generate ASTs.")
        return

    # json_str1 = json.dumps(parser1.ast_to_json(root1), indent=2)
    # json1 = json_to_astnode(json.loads(json_str1))

    # json_str2 = json.dumps(parser2.ast_to_json(root2), indent=2)
    # json2 = json_to_astnode(json.loads(json_str2))


    # offspring1, offspring2 = subtree_crossover(json1, json2)
    # print_ast(offspring1)
    # print_ast(offspring2)

    ast_node1=parser1.clang_cursor_to_astnode(root1)

    # print("=== Offspring 1 ===")
    # print(parser1.dump_ast(root1))
    # print(json_str1)
    # print_ast(json1)

    # print(emit_translation_unit(json1))

    print(ast_node1)
    # print_astnode(ast_node1)
    print(emit_translation_unit(ast_node1))


    # print("=== Offspring 2 ===")
    # print(emit_stmt(offspring2))

def test_reconstruct_c():
    source_path1 = "Test/C_Programs/example_0.c"

    parser1 = ASTParser(source_path1) #C configuration
    root1 = parser1.parse(False)
    parser1.dump_ast(root1)

    ast_node1=parser1.clang_cursor_to_astnode(root1)

    # print(ast_node1)
    # print_astnode(ast_node1)

    parser1.print_astnode(ast_node1)
    print(emit_translation_unit(ast_node1))


def test_reconstruct_cpp():

    source_path1 = "Test/CPP_Programs/example_0.cpp"
    # source_path1 = "Test/CPP_Programs_Meta_Real_Sample/generated_program_2025-11-06_10-45-59-159.cpp"
    language_ext = ".cpp"

    parser1 = ASTParser(source_path1, language="c++", std="c++17")
    root1 = parser1.parse(False)


    # parser1.dump_ast(root1)

    ast_node1=parser1.clang_cursor_to_astnode(root1)

    # json_str1=parser1.ast_to_json(ast_node1,pretty=True)
    # print(json_str1)
    print()
    print("=== AST Node ===")
    parser1.print_astnode(ast_node1)
    print(emit_translation_unit(ast_node1,language_ext))



# def print_astnode(node, indent=""):
#     print(f"{indent}{node.kind}: spelling={repr(node.spelling)}, token_value={repr(node.token_value)}, type_name={repr(getattr(node, 'type_name', None))}")
#     for child in node.children:
#         print_astnode(child, indent + "  ")

if __name__ == "__main__":
    # test()
    # test_crossover()


    # test_reconstruct_c()
    test_reconstruct_cpp()


# python3 -m src.ast_manager.main
