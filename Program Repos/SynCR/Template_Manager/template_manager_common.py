from abc import ABC, abstractmethod
import os
import Utilities.utils as utils
import re
from Config.global_config import config

class TemplateManager(ABC):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, folder_path):
        if not hasattr(self, 'initialized'):  # Prevent reinitialization
            self.templates = self.read_files_from_folder(folder_path)
            self.initialized = True

    @abstractmethod           
    def build_custom_template(self):
        pass

    def read_template(self,file_path):
        #this need to be later configured to read from the config file
        file_path = os.path.join(config.PATHS.template_path,file_path)
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")
            return ""

    
    def read_files_from_folder(self,folder_path, file_extension='.tmpl'):
        templates = []
        
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' does not exist.")
            return {}

        try:
            for filename in os.listdir(folder_path):
                if file_extension is not None and not filename.endswith(file_extension):
                    continue 

                templates.append(filename)

        except Exception as e:
            print(f"Error listing directory '{folder_path}': {e}")

        return templates
    
    # def process_templates_with_uids(self, template_path):
    #     template_content = self.read_template(template_path)
    #     modified_template = template_content
    #     placeholder_map = {}

    #     for item in utils.extract_template_placeholders(template_content):
    #         unique_id = utils.generate_unique_id()
    #         placeholder_map[unique_id] = item
    #         modified_template = modified_template.replace(f"{{{{{item}}}}}", f"{{{{{unique_id}_{item}}}}}")

    #     return modified_template
    
    def process_templates_with_uids(self, template_path):
        template_content = self.read_template(template_path)
        modified_template = template_content
        placeholder_map = {}
        id_map = {}

        # Regular expression to match all placeholders
        pattern = r'\{\{([a-z]+_\d+):([A-Z_]+)\}\}'

        matches = list(re.finditer(pattern, template_content))
        
        for match in reversed(matches):  # Process in reverse to avoid index issues
            prefix, item = match.groups()
            placeholder = match.group()
            
            if prefix not in id_map:
                id_map[prefix] = utils.generate_unique_id()
            unique_id = id_map[prefix]
            
            replacement = f"{{{{{unique_id}_{prefix}:{item}}}}}"
            placeholder_map[f"{unique_id}_{prefix}"] = item
            
            modified_template = (
                modified_template[:match.start()] 
                + replacement 
                + modified_template[match.end():]
            )

        # Add missing FUNCTION_PROTOTYPE_DEFINITION for fid_2
        # for prefix, unique_id in id_map.items():
        #     if f"{unique_id}_{prefix}:FUNCTION_PROTOTYPE_DEFINITION" not in modified_template:
        #         prototype_def = f"{{{{{unique_id}_{prefix}:FUNCTION_PROTOTYPE_DEFINITION}}}}\n"
        #         insert_pos = modified_template.index("using namespace std;") + len("using namespace std;")
        #         modified_template = modified_template[:insert_pos] + "\n" + prototype_def + modified_template[insert_pos:]

        # Handle placeholders without prefixes (like {{INCLUDES}})
        simple_pattern = r'\{\{([A-Z_]+)\}\}'
        simple_matches = list(re.finditer(simple_pattern, modified_template))
        
        for match in reversed(simple_matches):
            item = match.group(1)
            unique_id = utils.generate_unique_id()
            placeholder = match.group()
            replacement = f"{{{{{unique_id}_{item}}}}}"
            
            placeholder_map[unique_id] = item
            modified_template = (
                modified_template[:match.start()] 
                + replacement 
                + modified_template[match.end():]
            )

        return modified_template, placeholder_map

    
    def group_placeholders_by_id(self,placeholders):
        grouped = {}
        non_grouped = []
        
        for item in placeholders:
            parts = item.split(':')
            if len(parts) == 1:
                # No identifier, add to non_grouped list
                non_grouped.append(parts[0])
            else:
                # Use the identifier as the key
                id = parts[0]
                placeholder = parts[1]
                if id not in grouped:
                    grouped[id] = []
                grouped[id].append(placeholder)
        
        return grouped, non_grouped

    def save_proceesed_template_with_uid(self, template_content, output_path):
        """
        Writes the processed template to the output file.
        """
        with open(output_path, "w") as output_file:
            output_file.write(template_content)

    def save_rendered_template(self, template_content, output_path):
        """
        Writes the rendered template to the output file.
        """
        with open(output_path, "w") as output_file:
            output_file.write(template_content)


