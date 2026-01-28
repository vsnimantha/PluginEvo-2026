from abc import ABC, abstractmethod
import os
# from Grammar_Parser.parser_impl import GrammarParserImpl
from Grammar_Parser.parser_ast import GrammarParserAst
from Config.global_config import config


class ProgramGenerator(ABC):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.initialized = True
            # self.grammar_parser = GrammarParserImpl('Grammar/Program_Constructs')
            # self.grammar_parser = GrammarParserAst('Grammar/Program_Constructs')
            self.grammar_parser = GrammarParserAst(config.PATHS.grammar_path)

                
    @abstractmethod
    def generate_program(self,folder_path):
        pass