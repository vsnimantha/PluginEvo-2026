import random
import Utilities.grammar_parser_utils as grammar_parser_utils
import Utilities.ast_utils as ast_utils
from Utilities.utils import Constants
from collections import defaultdict
from typing import Dict, List, Union, Any
from Grammar_Parser.parameter_info import ParameterInfo
from Grammar_Parser.ast_node import ASTNode
from Config.global_config import config


class SmartCodeGenerator:
    def __init__(self, original_grammar, grammar: Dict[str, Any]):
        self.grammar = grammar
        self.original_grammar = original_grammar
        self.usage_stats = defaultdict(lambda: defaultdict(int))
        self.context = {}
        self.processing_data_type = ""
        self.array_loop = ""
        self.is_function = False
        self.is_recursive_function = False
        self.recursive_function_name=""
        self.is_param_function = False
        self.is_param_processing = False
        self.param_data_type = ""
        self.param_data_type_block = ""
        self.param_identifier_block = ""
        self.param_identifier = ""
        self.param_value = ""
        self.param_code = ""
        self.param_list = []
        
        # AST related attributes
        self.ast_root = ASTNode("root")
        self.current_ast_node = self.ast_root
        self.ast_stack = [self.ast_root]
        
        # Function related attributes
        self.current_return_type = None
        self.recursive_function_name = ""
        self.original_function_name_processed = False
        
        # Array processing
        self.is_array_processing = False
        self.array_data_type = ""
        self.array_identifier = ""
        self.array_length = 0
        
        # Variable declaration
        self.is_var_declaration_processing = False
        self.var_data_type = ""

        self.processing_loops=False
        self.processing_if_conditions=False

    def generate(self, count: int = 10) -> List[str]:
        """Generate smart code samples with error handling"""
        results = []
        attempts = 0
        max_attempts = count * 2  # Prevent infinite loops
        
        while len(results) < count and attempts < max_attempts:
            attempts += 1
            try:
                # Reset state for each generation
                self._reset_generator_state()
                
                result = self._generate_node(self.grammar)
                # print(f"result is {result}")
                if result and isinstance(result, str) and result.strip():
                    # Handling array data printing loop
                    if self.array_loop != "" and self.processing_loops is False and self.processing_if_conditions is False:
                        result = f"{result} \n {self.array_loop}"
                        self.array_loop = ""
                    results.append((result, grammar_parser_utils.ast_to_list(self.ast_root), 
                                 self.param_list, self.is_param_function, self.is_recursive_function))
                    # results.append(result)
                    # print(ast_utils.print_ast_tree(grammar_parser_utils.ast_to_list(self.ast_root)))
                    # print(ast_utils.save_ast(grammar_parser_utils.ast_to_list(self.ast_root),"Pakaya")) 
            except Exception as e:
                print(f"Generation warning: {str(e)}")
                continue
                
        return results

    def _reset_generator_state(self):
        """Reset the generator state for a new generation"""
        self.ast_root = ASTNode("root")
        self.current_ast_node = self.ast_root
        self.ast_stack = [self.ast_root]
        self.context = {}
        self.param_list = []
        self.is_function = False
        self.is_recursive_function = False
        self.recursive_function_name=""
        self.is_param_function = False
        self.array_loop = ""
        self.current_return_type = None
        self.recursive_function_name = ""
        self.original_function_name_processed = False
        self.processing_loops=False
        self.processing_if_conditions=False


    def _generate_node(self, node: Union[Dict, List, str]) -> Union[str, None]:
        """Core generation method with enhanced safety checks"""
        if isinstance(node, str):
            self._add_ast_node("terminal", node)
            return node
            
        if not isinstance(node, dict):
            return None
            
        element = node.get("element")

        # print(element)

        # Create rule node for non-terminal elements
        if element and element.startswith("<") and element.endswith(">"):
            rule_node = self._add_ast_node("rule", element)
            self.ast_stack.append(rule_node)

        # Handle terminal values
        if node.get("element") == "terminal":
            result = self._handle_terminal(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result
        
        if element and 'loop' in element:
            self.processing_loops=True
        
        if element and ('if_statement' in element or 'else' in element):
            self.processing_if_conditions = True


        if element and 'function_parameterised' in element:
            self.is_param_function = True
            
        if element and 'function' in element:
            self.is_function = True

        if element and 'function_recursive' in element:
            self.is_recursive_function = True
            

        if element and self.is_recursive_function and element=="<function_name>":
            result = self._handle_function_name(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result
        
        if element and self.is_function and element=="<return_type>":
            result = self._handle_function_return_type(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result

        if element and element=="<array>":
            self.is_array_processing = True

        if element == "<identifier_parameter>":
            result = self._handle_identifier_parameter(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result

        if element == "<parameter>":
            self.is_param_processing = True

        if element and element == '<var_declaration>':
            self.is_var_declaration_processing=True

        # Track current data type context
        if node.get("element") == "<data_type>":
            result = self._handle_data_type(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result
        
        if node.get("element") == "<array_size>":
            result = self._handle_array_size(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result
        
        if node.get("element") == "<identifier>":
            result = self._handle_identifier(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result
        
        
        if node.get("element") == "<rand_array_values>":
            data_type = self.context.get("current_type", "int")
            size = self.context.get("array_size", 10)
            current_var = self.context["current_identifier"]

            if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and data_type=="string":
                data_type=data_type.replace("string","char")
 
            data = grammar_parser_utils.generate_array_data(data_type, current_var, size, self.original_grammar)
            if isinstance(data, tuple) and len(data) == 2:
                self.array_loop = data[1]
                result = data[0]
            else:
                result = str(data)
            
            self._add_ast_node("array_values", result)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result

        # Handle sequences (without creating sequence nodes)
        if node.get("type") == "sequence":
            parts = []
            for element_item in node.get("elements", []):
                part = self._generate_node(element_item)
                if part and isinstance(part, str):
                    if part=="}" and (self.processing_loops or self.is_function or self.processing_if_conditions) and self.array_loop:
                        parts.append(self.array_loop)
                        self.processing_loops=False
                        self.processing_if_conditions=False
                        self.array_loop=""

                    if part=="}" and self.is_function and self.current_return_type:
                        if self.current_return_type!="void":
                            function_return_data=grammar_parser_utils.process_return_type(self.current_return_type,self.original_grammar)
                            parts.append(f"return {function_return_data};")

                    if self.is_var_declaration_processing:
                        if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and part=="string":
                           self.var_data_type="string"
                           part="char"

                        if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and self.var_data_type=="string" and part=="=":
                            parts.append("[]")
                            self.var_data_type=""

                    parts.append(part)
            
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return " ".join(parts) if parts else ""
            
        # Handle possible combinations
        if "possible_combinations" in node:
            result = self._handle_combinations(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result
            
        # Handle direct elements
        if "element" in node:
            result = self._generate_node(node)
            if element and element.startswith("<") and element.endswith(">"):
                self.ast_stack.pop()
            return result
            
        if element and element.startswith("<") and element.endswith(">"):
            self.ast_stack.pop()
        return None

    def _add_ast_node(self, node_type: str, value: str):
        """Add a node to the AST, skipping sequence nodes"""
        if node_type == "sequence":
            return None
            
        node = ASTNode(node_type, value)
        if self.ast_stack:
            parent = self.ast_stack[-1]
            parent.add_child(node)
        else:
            self.ast_root.add_child(node)
        return node

    def _handle_function_name(self, node: Dict) -> str:
        """Special handling for function names, particularly recursive functions"""
        options = self._collect_options(node)
        
        if not options:
            # Default function names if none are provided in the grammar
            prefixes = ["compute", "calculate", "process", "recursive"]
            suffixes = ["Factorial", "Sum", "Fibonacci", "Power"]
            options = [random.choice(prefixes) + random.choice(suffixes)]
        
        if self.is_recursive_function:
            if self.original_function_name_processed:
                # Reuse the stored recursive function name
                selected = self.recursive_function_name
            else:
                # First time processing this recursive function's name
                selected = random.choice(options)
                self.recursive_function_name = selected
                self.original_function_name_processed = True
        else:
            # For non-recursive functions, just pick a name
            selected = random.choice(options)
        
        self._add_ast_node("function_name", selected)
        return selected

    def _handle_function_return_type(self, node: Dict) -> str:
        """Special handling for function return types"""
        options = self._collect_options(node)
        
        if not options:
            data = ["bool","int","double","float","void"]
            options = random.choice(data)
            
        selected = random.choice(options)
        self.current_return_type = selected
        self._add_ast_node("return_type", selected)
        return selected
    
    def _handle_identifier_parameter(self, node: Dict) -> str:
        """Identifier selection with coverage guarantee for Greek-letter variables"""
        options = self._collect_options(node)
        
        if not options:
            options = ["alpha", "beta", "gamma", "delta"]
            
        min_usage = min(self.usage_stats["param_identifiers"].get(opt, 0) for opt in options)
        candidates = [opt for opt in options 
                     if self.usage_stats["param_identifiers"].get(opt, 0) == min_usage]
        
        selected = random.choice(candidates)
        self.usage_stats["param_identifiers"][selected] += 1
        self.context["current_param_identifiers"] = selected

        self.param_identifier = selected
        self.param_identifier_block = node.get("element")
        param_value = grammar_parser_utils.process_param_values(self.param_data_type)

        self.param_code += selected

        info = ParameterInfo(self.param_data_type_block, self.param_data_type,
                            self.param_identifier_block, self.param_identifier,
                            param_value, self.param_code)
        self.param_list.append(info)

        # Clearing values for the next parameter if there's any
        self.param_code = ""
        self.is_param_processing = False
        self.param_data_type = ""
        self.param_data_type_block = ""
        self.param_identifier_block = ""
        self.param_identifier = ""
        self.param_code = ""
        self.param_value = None
        
        self._add_ast_node("identifier_parameter", selected)
        return selected

    def _handle_terminal(self, node: Dict) -> str:
        """Safe terminal value handling"""
        value = str(node.get("value", ""))
        data_type = self.context.get("current_type", "int")

        if value == "<rand_var_values>":
            generated_value = grammar_parser_utils.process_random_data_values(data_type)
            self._add_ast_node("random_variable_value", generated_value)
            return generated_value
        elif value == "<rand>":
            generated_value = grammar_parser_utils.process_random_data_values("int")
            self._add_ast_node("random_value", generated_value)
            return generated_value
        elif value=="<rand_strings>":
            generated_value=grammar_parser_utils.process_rand_string()
            self._add_ast_node("random_string_value", generated_value)
            return generated_value
        
        self.usage_stats["terminals"][value] += 1
        self._add_ast_node("terminal", value)
        return value
    
    def _handle_identifier(self, node: Dict) -> str:
        """Identifier selection with coverage guarantee for Greek-letter variables"""
        options = self._collect_options(node)
        
        if not options:
            options = ["alpha", "beta", "gamma", "delta"]
            
        min_usage = min(self.usage_stats["identifiers"].get(opt, 0) for opt in options)
        candidates = [opt for opt in options 
                     if self.usage_stats["identifiers"].get(opt, 0) == min_usage]
        
        selected = random.choice(candidates)
        self.usage_stats["identifiers"][selected] += 1
        self.context["current_identifier"] = selected
        
        self._add_ast_node("identifier", selected)
        return selected
    
    def _handle_array_size(self, node: Dict) -> str:
        """Array size selection with coverage guarantee and special <rand> handling"""
        options = self._collect_options(node)
        
        if not options:
            options = ["10"]
        
        regular_sizes = [opt for opt in options if opt != "<rand>"]
        has_rand = "<rand>" in options
        
        if has_rand:
            rand_usage = self.usage_stats["array_sizes"].get("<rand>", 0)
            min_regular_usage = min(self.usage_stats["array_sizes"].get(opt, 0) for opt in regular_sizes) if regular_sizes else 0
            
            if (rand_usage > min_regular_usage and random.random() > 0.5) or not regular_sizes:
                selected = "<rand>"
            else:
                candidates = [opt for opt in regular_sizes 
                            if self.usage_stats["array_sizes"].get(opt, 0) == min_regular_usage]
                selected = random.choice(candidates) if candidates else "10"
        else:
            min_usage = min(self.usage_stats["array_sizes"].get(opt, 0) for opt in options)
            candidates = [opt for opt in options 
                        if self.usage_stats["array_sizes"].get(opt, 0) == min_usage]
            selected = random.choice(candidates) if candidates else "10"
        
        self.usage_stats["array_sizes"][selected] += 1
        
        if selected == "<rand>":
            rand_size = random.randint(1, 100)
            self.context["array_size"] = rand_size
            self._add_ast_node("array_size", str(rand_size))
            return str(rand_size)
        
        self.context["array_size"] = int(selected)
        self._add_ast_node("array_size", selected)
        return selected

    def _handle_data_type(self, node: Dict) -> str:
        """Data type selection with coverage guarantee"""
        options = self._collect_options(node)

        if not options:
            return "int"
            
        min_usage = min(self.usage_stats["data_types"][opt] for opt in options)
        candidates = [opt for opt in options 
                     if self.usage_stats["data_types"][opt] == min_usage]
        selected = random.choice(candidates)
        self.usage_stats["data_types"][selected] += 1
        self.context["current_type"] = selected

        if self.is_array_processing:
            if config.PROGRAM_GENERATION.programming_language.lower() == Constants.PROGRAMMING_LANGUAGE_C and selected=="string":
                selected="char"
                self.context["current_type"] = selected

        if self.is_param_function and self.is_param_processing:
            self.param_data_type = selected
            self.param_code += selected
            self.param_data_type_block = node.get("element")

        self._add_ast_node("data_type", selected)
        return selected

    def _collect_options(self, node: Union[Dict, List]) -> List[str]:
        """Safely collect all terminal options"""
        options = []
        
        if isinstance(node, dict):
            if node.get("element") == "terminal":
                value = str(node.get("value", ""))
                if value:
                    options.append(value)
            elif "possible_combinations" in node:
                for comb in node.get("possible_combinations", []):
                    options.extend(self._collect_options(comb))
            elif "elements" in node:
                for elem in node.get("elements", []):
                    options.extend(self._collect_options(elem))
        elif isinstance(node, list):
            for item in node:
                options.extend(self._collect_options(item))
                
        return options

    def _handle_combinations(self, node: Dict) -> str:
        """Robust combination selection"""
        choices = node.get("possible_combinations", [])
        if not choices:
            return ""
        
        weights = []
        for i in range(len(choices)):
            usage = self.usage_stats["choices"].get(str(i), 0)
            weights.append(1.0 / (usage + 1))
            
        try:
            selected_idx = random.choices(range(len(choices)), weights=weights, k=1)[0]
            self.usage_stats["choices"][str(selected_idx)] += 1
            return self._generate_node(choices[selected_idx])
        except:
            selected_idx = random.randint(0, len(choices) - 1)
            return self._generate_node(choices[selected_idx])
        
    #This is the code for the planned exstension to mege smart and random generation to a single    
 
 
    def _handle_combinations_extended(self, node: Dict, weighted: bool = True) -> str:
        """Select a combination, weighted or purely random based on flag."""
        choices = node.get("possible_combinations", [])
        if not choices:
            return ""

        try:
            if weighted:
                # Build weights based on usage stats
                weights = []
                for i in range(len(choices)):
                    usage = self.usage_stats["choices"].get(str(i), 0)
                    weights.append(1.0 / (usage + 1))

                selected_idx = random.choices(range(len(choices)), weights=weights, k=1)[0]
            else:
                # Pure random selection
                selected_idx = random.randint(0, len(choices) - 1)

            # Update usage stats only if weighted mode is used
            if weighted:
                self.usage_stats["choices"][str(selected_idx)] = \
                    self.usage_stats["choices"].get(str(selected_idx), 0) + 1

            return self._generate_node(choices[selected_idx])

        except Exception:
            # Fallback to pure random if something goes wrong
            selected_idx = random.randint(0, len(choices) - 1)
            return self._generate_node(choices[selected_idx])


    def _generate_context_value(self) -> str:
        """Context-aware value generation with fallbacks"""
        dtype = self.context.get("current_type", "int")
        value = grammar_parser_utils.process_random_data_values(dtype)
        self._add_ast_node("context_value", value)
        return value