import os
import re
from itertools import product

def load_grammar(folder_path):
    grammar = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".bnf"):
            with open(os.path.join(folder_path, filename), "r") as file:
                for line in file:
                    match = re.match(r"<(.+?)>\s*::=\s*(.+)", line.strip())
                    if match:
                        key, value = match.groups()
                        productions = [v.strip() for v in value.split('|')]
                        grammar.setdefault(key, []).extend(productions)
    return grammar

def symbolic_expand_structural(symbol, grammar):
    if symbol not in grammar:
        return [f"<{symbol}>"]

    results = []
    structural_keywords = {"loop", "statement", "expression", "condition", "body"}

    for production in grammar[symbol]:
        tokens = re.findall(r'<[^>]+>|[^<>\s]+', production)

        # Select the most structurally meaningful nested symbol
        candidates = []
        for token in tokens:
            if token.startswith('<'):
                key = token[1:-1]
                if key in grammar and len(grammar[key]) > 1:
                    # Give priority if the rule name includes structural keywords
                    priority = any(word in key for word in structural_keywords)
                    candidates.append((token, len(grammar[key]), priority))

        # Pick best candidate: highest priority, most options
        if candidates:
            # Sort by: priority flag first, then number of options (descending)
            candidates.sort(key=lambda x: (not x[2], -x[1]))
            chosen_token = candidates[0][0]
            chosen_key = chosen_token[1:-1]

            for option in grammar[chosen_key]:
                substituted = [option if tok == chosen_token else tok for tok in tokens]
                results.append(' '.join(substituted))
        else:
            results.append(' '.join(tokens))

    return results

def symbolic_expand_multi_nested(symbol, grammar):
    if symbol not in grammar:
        return [f"<{symbol}>"]

    structural_keywords = {"loop", "statement", "expression", "condition", "body"}
    results = []

    for production in grammar[symbol]:
        tokens = re.findall(r'<[^>]+>|[^<>\s]+', production)

        expandable_slots = []
        slot_options = []

        for token in tokens:
            if token.startswith('<'):
                key = token[1:-1]
                if key in grammar and len(grammar[key]) > 1:
                    if any(k in key for k in structural_keywords):
                        expandable_slots.append(token)
                        slot_options.append(grammar[key])
                    else:
                        expandable_slots.append(token)
                        slot_options.append([token])  # keep as-is
                else:
                    expandable_slots.append(token)
                    slot_options.append([token])
            else:
                expandable_slots.append(token)
                slot_options.append([token])

        # Expand combinations of all meaningful tokens
        for combo in product(*slot_options):
            results.append(' '.join(combo))

    return results


# 🧪 Configure and run
folder = "Grammar/Program_Constructs_CPP"
grammar = load_grammar(folder)
print(grammar)
# print(grammar.keys())
# if "function" in grammar:
#     print(grammar["function"])
# else:
#     print("No 'function' key found.")




# target_rule = "while_loop_conditional"  # Change to other rules like 'do_while_loop', etc.
# print(f"\n🔍 High-level symbolic combinations for <{target_rule}>...\n")

# combinations = symbolic_expand_multi_nested(target_rule, grammar)
# for i, combo in enumerate(combinations):
#     print(f"{i+1}. {combo}")
