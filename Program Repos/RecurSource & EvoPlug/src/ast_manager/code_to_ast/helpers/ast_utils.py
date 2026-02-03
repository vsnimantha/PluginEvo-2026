import os
from clang.cindex import CursorKind, AccessSpecifier

def is_system_header(cursor):
    try:
        file = cursor.location.file
        if file is None:
            return False
        path = file.name
        return (
            path.startswith("/usr/include")
            or path.startswith("/Library/Developer/CommandLineTools")
            or "/Applications/Xcode.app" in path
        )
    except:
        return False

def is_unwanted_macro(cursor, source_code_path):
    if cursor.kind != CursorKind.MACRO_DEFINITION:
        return False
    loc = cursor.location
    if loc.file is None:
        return True
    try:
        return not os.path.samefile(loc.file.name, source_code_path)
    except Exception as e :
        print(e)
        return True
    

def parse_class_children(cursor, clang_cursor_to_astnode):
    children = []
    default_access = AccessSpecifier.PRIVATE if cursor.kind == CursorKind.CLASS_DECL else AccessSpecifier.PUBLIC
    current_access = default_access

    for c in cursor.get_children():
        if c.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
            current_access = c.access_specifier
            continue

        child_node = clang_cursor_to_astnode(c)
        if child_node:
            child_node.access_specifier = current_access
            children.append(child_node)

    return children
