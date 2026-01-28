from Program_Generator.program_generator_common import ProgramGenerator

class ProgramGeneratorFull(ProgramGenerator):
    
    def __init__(self, folder_path):
        if not hasattr(self, 'initialized'):  
            super().__init__()
            self.folder_path = folder_path
            self.initialized =True
            
    def generate_program(self):
        pass


    