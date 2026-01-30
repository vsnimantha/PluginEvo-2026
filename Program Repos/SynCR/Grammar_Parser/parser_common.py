from abc import ABC, abstractmethod
import os

# from construct_types import ConstructType

class GrammarParser(ABC):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, file_path):
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.grammar = self.read_files_from_folder(file_path,".bnf")
            self.rules = {}
            self.initialized = True
                
    
    @abstractmethod
    def parse(self): 
        pass   

    # def read_bnf_grammar(self,file_path):
    #         with open(file_path, 'r') as file:
    #             lines = file.readlines()
    #         grammar = {}
    #         for line in lines:
    #             if line.strip() == '' or line.strip().startswith('#'):
    #                 continue
    #             lhs, rhs = line.strip().split('::=')
    #             lhs = lhs.strip()
    #             rhs = [alt.strip().split() for alt in rhs.split('|')]
    #             grammar[lhs] = rhs

    #         print(grammar)    
    #         return grammar

    def read_bnf_grammar(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        grammar = {}
        for line in lines:
            if line.strip() == '' or line.strip().startswith('#'):
                continue
            lhs, rhs = line.strip().split('::=')
            lhs = lhs.strip()
            
            # Split alternatives while preserving quoted strings
            alternatives = []
            current_alt = []
            in_quote = False
            current_token = ''
            
            for char in rhs.strip():
                if char == '"':
                    if in_quote:
                        current_token += char
                        current_alt.append(current_token)
                        current_token = ''
                        in_quote = False
                    else:
                        if current_token:
                            current_alt.extend(current_token.split())
                            current_token = ''
                        current_token += char
                        in_quote = True
                elif char == '|' and not in_quote:
                    if current_token:
                        current_alt.extend(current_token.split())
                    if current_alt:
                        alternatives.append(current_alt)
                    current_alt = []
                    current_token = ''
                else:
                    current_token += char
            
            # Add the last alternative
            if current_token:
                current_alt.extend(current_token.split())
            if current_alt:
                alternatives.append(current_alt)
            
            grammar[lhs] = alternatives
        
        return grammar

    def read_files_from_folder(self,folder_path, file_extension=None):
        file_contents = []
        
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' does not exist.")
            return {}

        try:
            for filename in os.listdir(folder_path):
                if file_extension is not None and not filename.endswith(file_extension):
                    continue 

                file_path = os.path.join(folder_path, filename)
                file_contents.append(self.read_bnf_grammar(file_path))
                
        except Exception as e:
            print(f"Error listing directory '{folder_path}': {e}")

        return file_contents
