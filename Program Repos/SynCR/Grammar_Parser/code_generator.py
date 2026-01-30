import random
import json
from typing import Dict, List, Union

#THIS IS A SAMPLE PROGRAM GENERATOR EXPERIMENTED FOR MULTIPLE PROGRAM GENERATOR
#THIS IS CURRENTLY NOT IN USE
#CODE MIGHT BE USEFUL FOR FUTURE WORK

class CodeGenerator:
    def __init__(self, grammar: Dict):
        self.grammar = grammar
        self.current_data_type = None
    
    def generate_value(self) -> str:
        """Generate appropriate random values based on current data type"""
        if self.current_data_type == "bool":
            return random.choice(["true", "false"])
        elif self.current_data_type == "int":
            return str(random.randint(0, 100))
        elif self.current_data_type == "double":
            return f"{random.uniform(0, 100):.4f}"
        elif self.current_data_type == "float":
            return f"{random.uniform(0, 100):.4f}f"
        elif self.current_data_type == "string":
            words = ["hello", "world", "foo", "bar", "example"]
            return f'"{random.choice(words)}"'
        return "0"  # fallback

    def generate_from_node(self, node: Union[Dict, List, str]) -> str:
        """Recursively generate code from grammar nodes"""
        # Handle string terminals (like "=" or ";")
        if isinstance(node, str):
            return node
        
        # Handle terminal values
        if isinstance(node, dict) and node.get("element") == "terminal":
            value = node["value"]
            if value == "<rand_var_values>":
                return self.generate_value()
            return value
        
        # Handle sequences
        if isinstance(node, dict) and node.get("type") == "sequence":
            parts = []
            for element in node.get("elements", []):
                part = self.generate_from_node(element)
                if part:  # Only add non-empty parts
                    parts.append(part)
            return " ".join(parts)
        
        # Handle possible combinations
        if isinstance(node, dict) and "possible_combinations" in node:
            choices = node["possible_combinations"]
            if choices:  # Ensure there are choices available
                chosen = random.choice(choices)
                return self.generate_from_node(chosen)
            return ""
        
        # Handle direct elements
        if isinstance(node, dict) and "element" in node:
            # Track data type when we see it
            if node["element"] == "<data_type>":
                self.current_data_type = self.generate_from_node(node)
                return self.current_data_type
            return self.generate_from_node(node)
        
        # Handle case where node is a list
        if isinstance(node, list):
            if node:  # Non-empty list
                chosen = random.choice(node)
                return self.generate_from_node(chosen)
            return ""
        
        return ""  # Fallback for unexpected cases

    def generate(self, count: int = 10) -> List[str]:
        """Generate multiple code samples"""
        results = []
        for _ in range(count):
            result = self.generate_from_node(self.grammar)
            if result:  # Only add non-empty results
                results.append(result)
        return results

# Example usage with your grammar
if __name__ == "__main__":
    # Your grammar JSON here
    grammar_json = """{
        "element": "<var_declaration>",
        "possible_combinations": [
            {
                "type": "sequence",
                "elements": [
                    {
                        "element": "<data_type>",
                        "possible_combinations": [
                            {"element": "terminal", "value": "bool"},
                            {"element": "terminal", "value": "int"},
                            {"element": "terminal", "value": "double"},
                            {"element": "terminal", "value": "float"},
                            {"element": "terminal", "value": "string"}
                        ]
                    },
                    {
                        "element": "<identifier>",
                        "possible_combinations": [
                            {"element": "terminal", "value": "alpha"},
                            {"element": "terminal", "value": "beta"}
                        ]
                    },
                    {"element": "=", "possible_combinations": ["="]},
                    {
                        "element": "<value>",
                        "possible_combinations": [
                            {"element": "terminal", "value": "<rand_var_values>"}
                        ]
                    },
                    {"element": ";", "possible_combinations": [";"]}
                ]
            }
        ]
    }"""

    grammar = json.loads(grammar_json)
    generator = CodeGenerator(grammar)
    
    # Generate and print 10 random variable declarations
    declarations = generator.generate(10)
    for i, decl in enumerate(declarations, 1):
        print(f"{i}. {decl}")