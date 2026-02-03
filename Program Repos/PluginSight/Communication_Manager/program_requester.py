import os, json, requests
from datetime import datetime
from Config.global_config import config
from Utilities import file_management_utils

# def request_programs(url,number_of_programs=2,programming_language="cpp",template="random"):
#     try:
#         response = requests.get(url)
#         # Check if the request was successful
#         if response.status_code == 200:
#             # print("Request successful!") #Debug print
#             # print("Response:", response.text) #Debug print
#             return response
#         else:
#             print(f"Request failed with status code: {response.status_code}")
#     except Exception as e:
#         print(f"\nAn error occurred: {e}")

#     return None


def request_programs(url, number_of_programs=50, programming_language="C++", template="random",time_out=1200):
    try:
        params = {
            "number_of_programs": number_of_programs,
            "programming_language": programming_language,
            "template": template
        }

        # print(f"[DEBUG] Sending request to: {url}")
        # print(f"[DEBUG] Params: {params}")

        response = requests.get(url, params=params,timeout=time_out)

        # print(f"[DEBUG] Full Request URL: {response.url}")
        # print(f"[DEBUG] Status Code: {response.status_code}")

        # Print raw text (may be JSON or error HTML)
        # print(f"[DEBUG] Raw Response Text: {response.text}") 

        if response.status_code == 200:
            # try:
            #     data = response.json()
                # print(f"[DEBUG] Parsed JSON keys: {list(data.keys())}")
            # except Exception as je:
            #     print(f"[DEBUG] Could not parse JSON: {je}")
            return response
        else:
            print(f"[ERROR] Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"[EXCEPTION] An error occurred: {e}")

    return None


def process_response(response, base_dir: str = "Generated_Seeds"):
    """
    Process the JSON response from the program generator.
    Saves all programs into a timestamped subfolder under base_dir.

    Args:
        response: dict or JSON string from the generator
        base_dir: root folder where all seeds are stored

    Returns:
        programs: list of (code, filename) tuples
        save_dir: the path where files were saved
    """
    # Parse if string
    if isinstance(response, str):
        data = json.loads(response)
    else:
        data = response

    # Create a unique subfolder for this batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = os.path.join(base_dir, f"batch_{timestamp}")
    os.makedirs(save_dir, exist_ok=True)

    programs = []
    for index, prog in enumerate(data.get("programs", [])):
        print(f"\n--- Processing program {index + 1} ---")

        code = prog.get("code", "")
        filename = prog.get("filename", f"program_{index+1}.cpp")

        # Save file locally in the batch folder
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"Saved: {file_path}")
        programs.append((code, file_path))

    return programs, save_dir



# def process_response(response_str):
#     try:
#         # Parse the JSON string
#         data = json.loads(response_str)
#         generated_programs=[]
#         folder_path=""
#         for index, item in enumerate(data):
#             print(f"\n--- Processing item {index + 1} ---")
            
#             # Extract status_code
#             status_code = item.get("status_code", "N/A")
#             print(f"Status Code: {status_code}")
            
#             # Extract background (if any)
#             background = item.get("background")
#             print(f"Background: {background}")
            
#             # Extract headers
#             folder_path=""
#             raw_headers = item.get("raw_headers", [])
#             print("Headers:")
#             for header in raw_headers:
#                 if header[0] !="" and header[0]=="folder_name":
#                     folder_path=header[1]
#                 # print(f"  {header[0]}: {header[1]}") #Debug_Print

#             # Extract body (assuming it's a C++ template in this case)
#             body = item.get("body", "")
#             print(f"Body:\n{body}")

#             saved_path=save_to_cpp_file(body,folder_path=folder_path)
#             generated_programs.append(saved_path)

#         return generated_programs,folder_path
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")

def save_to_cpp_file(response_body,folder_path="Generated_Programs"):
    try:
        file_path=""
        folder_path=f"{config.PATHS.generated_program_save_path}/{folder_path}"
        parsed_response = json.loads(response_body)
        if len(parsed_response)>1:
            print(f"Program Body: \n {parsed_response[0]}")
            print(f"Program Filename: \n {parsed_response[1]}")

            file_management_utils.create_folder(folder_path)
            # Remove surrounding quotes if they exist
            if parsed_response[0].startswith('"') and parsed_response[0].endswith('"'):
                parsed_response[0] = parsed_response[0][1:-1]
            
            # Convert escape sequences to actual characters
            parsed_response[0] = parsed_response[0].encode().decode('unicode_escape')
            
            file_path=f"{folder_path}/{parsed_response[1]}"

            with open(file_path, "w") as file:
                file.write(parsed_response[0])
            print(f"Program successfully saved to {parsed_response[1]}")
        else:
            print("Invalid response.")
        
        return file_path
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")


if __name__ == "__main__":
    # Replace 'https://example.com' with the URL you want to send the request to
    url = config.FEEDBACK_MANAGER.generate_url_gp
    response=request_programs(url)


    # # Sample response (abbreviated for readability)
    # response = '[{"status_code":200,"background":null,"body":"...","raw_headers":[["content-length","917"],["content-type","application/json"]]},{"status_code":200,"background":null,"body":"...","raw_headers":[["content-length","606"],["content-type","application/json"]]}]'
    
    if response is not None:
        process_response(response.text)

# python3 -m Communication_Manager.program_requester