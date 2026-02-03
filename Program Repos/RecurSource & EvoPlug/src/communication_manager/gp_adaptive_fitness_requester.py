import requests
from src.communication_manager import gp_communication_constants

# SECTON COVERAGE GENERATION
def check_api_health(api_url=gp_communication_constants.COVERAGE_SERVER_URL, timeout=3):
    """
    Check if coverage API is available.
    
    Parameters
    ----------
    api_url : str
        API endpoint (e.g., "http://localhost:5000")
    timeout : int
        Request timeout in seconds
    
    Returns
    -------
    bool
        True if API is online, False otherwise
    """
    try:
        response = requests.get(f"{api_url}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def get_coverage_from_api(source_code, api_url=gp_communication_constants.COVERAGE_SERVER_URL, timeout=500):
    """
    Get coverage score from API.
    
    Parameters
    ----------
    source_code : str
        Program source code to analyze
    api_url : str
        API endpoint
    timeout : int
        Request timeout in seconds
    
    Returns
    -------
    dict or None
        Transformed metadata dict with coverage info, or None if failed
    """
    try:
        response = requests.post(
            f"{api_url}/analyze",
            json={"code": source_code},
            timeout=timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            # print(data)
            
            # Transform API response to your metadata format
            meta = transform_api_response(data)
            return meta
        else:
            return None
            
    except:
        return None


def transform_api_response(data):
    """
    Transform API response to metadata format.
    
    Parameters
    ----------
    data : dict
        API response with coverage data
    
    Returns
    -------
    dict
        Metadata dict with normalized coverage
    """
    cov = data.get("coverage", {})
    
    # Extract numeric coverage values
    values = [v for v in cov.values() if isinstance(v, (int, float))]
    avg_cov = sum(values) / len(values) if values else 0.0
    
    return {
        "filename": data.get("filename", "generated"),
        "folder": data.get("folder", "generated"),
        "coverage": round(avg_cov / 100.0, 2),  # Normalize to 0.0-1.0
        "line_coverage": cov.get("line_coverage"),
        "function_coverage": cov.get("function_coverage"),
        "branch_coverage": cov.get("branch_coverage"),
        "decision_coverage": cov.get("decision_coverage"),
        "call_coverage": cov.get("call_coverage"),
        "error": data.get("error"),
    }




# SECTION COMPILER TEST

def check_compiler_api_health(api_url=gp_communication_constants.COMPILER_TEST_SERVER_URL, timeout=15):
    """
    Check if compiler API is available.
    
    Parameters
    ----------
    api_url : str
        API endpoint (e.g., "http://localhost:5060")
    timeout : int
        Request timeout in seconds
    
    Returns
    -------
    bool
        True if API is online, False otherwise
    """
    try:
        response = requests.get(f"{api_url}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def get_compiler_result_from_api(source_code, filename="generated.cpp",
                                 api_url=gp_communication_constants.COMPILER_TEST_SERVER_URL,
                                 timeout=500):
    """
    Send source code to compiler API and get compilation/test results.
    
    Parameters
    ----------
    source_code : str
        Program source code to compile/test
    filename : str
        Filename to assign to the program
    api_url : str
        API endpoint
    timeout : int
        Request timeout in seconds
    
    Returns
    -------
    dict or None
        Transformed metadata dict with compiler info, or None if failed
    """
    try:
        response = requests.post(
            f"{api_url}/test_single_offspring",
            json={"code": source_code, "filename": filename},
            timeout=timeout
        )

        if response.status_code == 200:
            data = response.json()
            meta = transform_compiler_response(data)
            return meta
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
            
    except Exception as e: 
        print(f"Exception occurred while calling compiler API: {e}")
        return None


def transform_compiler_response(data):
    """
    Transform compiler API response to metadata format.
    
    Parameters
    ----------
    data : dict
        API response with compiler test summary
    
    Returns
    -------
    dict
        Metadata dict with normalized compiler info
    """
    summary = data.get("meta", data)  # sometimes returned directly, sometimes nested

    print("[DEBUG] Transforming compiler response")
    print("[DEBUG] Input data:", data)
    print("[DEBUG] Normalized summary:", summary)

    
    return {
        "filename": data.get("filename", "generated.cpp"),
        "compiled": summary.get("compiled", False),
        "success_count": summary.get("success_count"),
        "failure_count": summary.get("failure_count"),
        "ice_count": summary.get("ice_count"),
        "timeout_count": summary.get("timeout_count"),
        "differential_mismatches": summary.get("differential_mismatches"),
        "total_attempts": summary.get("total_attempts"),
        "logs": summary.get("logs", {}),
        "error": data.get("error")
    }
