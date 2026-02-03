import requests
import json
from Config.global_config import config
from Utilities import file_management_utils

def request_programs(url):
    try:
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # print("Request successful!") #Debug print
            # print("Response:", response.text) #Debug print
            return response
        else:
            print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

    return None

def process_response(response_str):
    try:
        # Parse the JSON string
        data = json.loads(response_str)
        generated_programs=[]
        folder_path=""
        for index, item in enumerate(data):
            print(f"\n--- Processing item {index + 1} ---")
            
            # Extract status_code
            status_code = item.get("status_code", "N/A")
            print(f"Status Code: {status_code}")
            
            # Extract background (if any)
            background = item.get("background")
            print(f"Background: {background}")
            
            # Extract headers
            folder_path=""
            raw_headers = item.get("raw_headers", [])
            print("Headers:")
            for header in raw_headers:
                if header[0] !="" and header[0]=="folder_name":
                    folder_path=header[1]
                # print(f"  {header[0]}: {header[1]}") #Debug_Print

            # Extract body (assuming it's a C++ template in this case)
            body = item.get("body", "")
            print(f"Body:\n{body}")
      
            saved_path=save_to_cpp_file(body,folder_path=folder_path)
            generated_programs.append(saved_path)

        return generated_programs,folder_path
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# def save_to_cpp_file(response_body,folder_path="Generated_Programs"):
#     try:
#         file_path=""
#         folder_path=f"{config.PATHS.generated_program_save_path}/{folder_path}"
#         parsed_response = json.loads(response_body)
#         if len(parsed_response)>1:
#             print(f"Program Body: \n {parsed_response[0]}")
#             print(f"Program Filename: \n {parsed_response[1]}")

#             file_management_utils.create_folder(folder_path)
#             # Remove surrounding quotes if they exist
#             if parsed_response[0].startswith('"') and parsed_response[0].endswith('"'):
#                 parsed_response[0] = parsed_response[0][1:-1]
            
#             # Convert escape sequences to actual characters
#             parsed_response[0] = parsed_response[0].encode().decode('unicode_escape')
            
#             file_path=f"{folder_path}/{parsed_response[1]}"

#             with open(file_path, "w") as file:
#                 file.write(parsed_response[0])
#             print(f"Program successfully saved to {parsed_response[1]}")
#         else:
#             print("Invalid response.")
        
#         return file_path
#     except Exception as e:
#         print(f"An error occurred while saving the file: {e}")


def save_to_cpp_file(response_body, folder_path="Generated_Programs"):
    try:
        file_path = ""
        folder_path = f"{config.PATHS.generated_program_save_path}/{folder_path}"
        parsed_response = json.loads(response_body)
        
        if len(parsed_response) > 1:
            print(f"Program Body: \n {parsed_response[0]}")
            print(f"Program Filename: \n {parsed_response[1]}")
            
            file_management_utils.create_folder(folder_path)
            
            # Ensure the program body retains escape sequences
            if parsed_response[0].startswith('"') and parsed_response[0].endswith('"'):
                parsed_response[0] = parsed_response[0][1:-1]
            
            # Prevent decoding escape sequences
            program_body = parsed_response[0]
            
            file_path = f"{folder_path}/{parsed_response[1]}"
            with open(file_path, "w") as file:
                file.write(program_body)
            print(f"Program successfully saved to {parsed_response[1]}")
        else:
            print("Invalid response.")
        
        return file_path
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")


if __name__ == "__main__":
    # Replace 'https://example.com' with the URL you want to send the request to
    url = config.FEEDBACK_MANAGER.generate_url
    response=request_programs(url)


    # # Sample response (abbreviated for readability)
    # response = '[{"status_code":200,"background":null,"body":"...","raw_headers":[["content-length","917"],["content-type","application/json"]]},{"status_code":200,"background":null,"body":"...","raw_headers":[["content-length","606"],["content-type","application/json"]]}]'
    
    if response is not None:
        process_response(response.text)

# python3 -m Feedback_Manager.program_requester 