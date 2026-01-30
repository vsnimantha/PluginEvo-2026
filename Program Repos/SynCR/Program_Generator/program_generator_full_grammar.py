from Program_Generator.program_generator_common import ProgramGenerator
#TODO::Idea is to implement a full program generator without using any templates but rather direct grammmar
class ProgramGeneratorFull(ProgramGenerator):
    
    def __init__(self, folder_path):
        if not hasattr(self, 'initialized'):  
            super().__init__()
            self.folder_path = folder_path
            self.initialized =True
            
    def generate_program(self):
        pass


    