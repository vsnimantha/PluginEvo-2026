import random

def generate_id(place_holder):
    id_number=random.randint(1,20)
    if place_holder == 'INCLUDES':
        return f"incld_{id_number}:"
    elif place_holder in ['FUNCTION_DEFINITION_NON_PARAM', 'FUNCTION_DEFINITION', 'FUNCTION_DEFINITION_PARAM','FUNCTION_DEFINITION_RECURSIVE']:
        return f"fid_{id_number}:"
    elif place_holder == 'IF_STATEMENTS':
        return f"ifstm_{id_number}:"
    elif place_holder == 'VAR_DECLARATION':
        return f"var_{id_number}:"
    elif place_holder =='FOR_LOOP':
        return f"flp_{id_number}:"
    elif place_holder== 'WHILE_LOOP':
        return f"wlp_{id_number}:"   
    elif place_holder== 'DO_WHILE_LOOP':
        return f"dwlp_{id_number}:"
    elif place_holder == 'PRINT_STATEMENT':
        return f"pstm_{id_number}:"    
    elif place_holder == 'PRINTF_STATEMENT':
        return f"psftm_{id_number}:"
    elif place_holder == 'MATH_EXPRESSION':
        return f"mexpr_{id_number}:"
    elif place_holder == 'ARRAY':
        return f"arr_{id_number}:"
    else:
        return ""

