#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import json
import glob
from pathlib import Path
from Config.global_config import config
import subprocess
import Utilities.file_management_utils as file_management_utils


def is_tool_installed(name):
    """Check if a tool is installed and available in PATH"""
    return shutil.which(name) is not None

def check_gcov_installation():
    """Verify gcov installation and version"""
    if not is_tool_installed("gcov"):
        print("Error: gcov is not installed or not in PATH")
        print("Please install gcov (usually comes with GCC)")
        return False
    
    try:
        result = subprocess.run(["gcov", "--version"], 
                              capture_output=True, 
                              text=True,
                              check=True)
        print(f"Found gcov: {result.stdout.splitlines()[0]}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking gcov version: {e.stderr}")
        return False

def find_source_files(source_dir, extensions=('.c', '.cc', '.cpp'), exclude_dirs=None):
    """Recursively find all source files in a directory with given extensions, excluding specified folders."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    source_files = []
    for ext in extensions:
        for file in Path(source_dir).rglob(f'*{ext}'):
            # Check if the file is not in excluded directories and is indeed a file
            if file.is_file() and not any(Path(source_dir, excluded) in file.parents for excluded in exclude_dirs):
                source_files.append(str(file))

    return sorted(source_files)


def generate_gcov_reports(plugin_output_path,plugin_name, source_files, gcov_reprt_path,json_output_dir,gcov_version="gcov"):
    """Generate gcov coverage reports"""
    # print("\nGenerating gcov coverage reports...")

    if config.COVERAGE_ANALYSER.gcov_version and config.COVERAGE_ANALYSER.gcov_version!="default":
        gcov_version=config.COVERAGE_ANALYSER.gcov_version

    
    for src_file in source_files:
        print(f"Processing {src_file}...")
        
        
        # Define the target directory
        gcov_report_path = Path(gcov_reprt_path)
        gcov_report_path.mkdir(parents=True, exist_ok=True)
        # Set permissions (read/write for user)
        os.chmod(gcov_report_path, 0o755)  # You can adjust permissions as needed
        
        #Generating .gcov report
        gcov_command = [gcov_version, "-o", src_file,"-b", "-c", "-f","-a","-d","-u", plugin_output_path]
        subprocess.run(gcov_command, check=True, cwd=gcov_reprt_path)

        #Generate Gcov report as Json
        gcov_command = [gcov_version, "-o", src_file, "-b", "-c", "-f","-a", "-j","-d","-u", plugin_output_path]
        subprocess.run(gcov_command, check=True,cwd=gcov_reprt_path) #This will generate the gcov file for reference

        # Saving Gcov output to the report file
        with open(f"{gcov_report_path}/coverage_report.txt", "w") as output_file:
            subprocess.run(gcov_command, check=True, cwd=gcov_reprt_path, stdout=output_file, text=True) #this will generate the coverage_report.txt
        
        print(f"Coverage report saved to {gcov_report_path}/Coverage_report.txt")

    #Moving and unzipping json files
    for gz_file in gcov_report_path.glob("*.json.gz"):
        output_dir = Path(json_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

        dest = output_dir / gz_file.name

        # Handle existing files or directories at the destination path
        if dest.exists():
            if dest.is_dir(): 
                shutil.rmtree(dest)
            else:  
                os.remove(dest)

        shutil.move(str(gz_file), str(dest))
        subprocess.run(["gunzip", "-f", str(dest)], check=True)

        # formatting the json output file
        if config.COVERAGE_ANALYSER.format_json_output:
            json_file_saved_path=f"{output_dir}/{gz_file.stem}"
            with open(json_file_saved_path, "r") as file:
                data = json.load(file)
                with open(json_file_saved_path, "w") as file:
                    json.dump(data, file, indent=4)

        print(f"Extracted {gz_file.stem} to {output_dir}")


def generate_html_report(output_dir,extra_flags=[]):
    """Generate HTML coverage report using gcovr"""
    if not is_tool_installed("gcovr"):
        print("gcovr is not installed. Skipping HTML report generation.")
        print("Install with: pip install gcovr")
        return
    
    print("\nGenerating HTML coverage report...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    gcovr_command = [
            "gcovr",
            *extra_flags,
            "--decisions",
            "--calls",
            "--html",
            "--html-details",
            "--exclude-unreachable-branches",
            "--exclude-throw-branches",
            "-o", 
            f"{output_dir}/coverage_report.html"
        ]

    subprocess.run(
        gcovr_command, 
        cwd=f"{config.PATHS.plugin_output_path}", 
        check=True
    )
    
    print(f"HTML report generated: {output_dir}/coverage_report.html")

def generate_json_report(output_dir,extra_flags=[]):
    """Generate JSON coverage report using gcovr"""
    if not is_tool_installed("gcovr"):
        print("gcovr is not installed. Skipping JSON report generation.")
        print("Install with: pip install gcovr")
        return
    
    print("\nGenerating JSON coverage report...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    gcovr_command = [
        "gcovr",
        *extra_flags,
        "--decisions",
        "--calls",
        "--json",
        "--json-pretty",
        "--exclude-unreachable-branches",
        "--exclude-throw-branches",
        "-o", f"{output_dir}/coverage_report.json"
    ]


    subprocess.run(
        gcovr_command, 
        cwd=f"{config.PATHS.plugin_output_path}", 
        check=True
    )

    print(f"JSON report generated: {output_dir}/coverage_report.json")

    return f"{output_dir}/coverage_report.json"



def generate_jacoco_xml_report(output_dir,extra_flags=[]):
    """Generate JSON and JaCoCo XML coverage reports using gcovr"""
    if not is_tool_installed("gcovr"):
        print("gcovr is not installed. Skipping report generation.")
        print("Install with: pip install gcovr")
        return
    
    print("\nGenerating JSON and JaCoCo XML coverage reports...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    gcovr_command = [
        "gcovr",
        *extra_flags,
        "--decisions",
        "--calls",
        "--jacoco",
        "--jacoco-pretty",
        "--exclude-unreachable-branches",
        "--exclude-throw-branches",
        "-o", f"{output_dir}/coverage_report.json",
        "--jacoco", f"{output_dir}/coverage_report.xml"
    ]

    subprocess.run(
        gcovr_command, 
        cwd=f"{config.PATHS.plugin_output_path}", 
        check=True
    )
    
    print(f"Reports generated:\n - JSON: {output_dir}/coverage_report.json\n - JaCoCo XML: {output_dir}/coverage_report.xml")

def print_gcovr_summary(output_dir,extra_flags=[]):
    """Run gcovr with print-summary and all analysis flags"""
    gcovr_command = [
        "gcovr",
        *extra_flags,
        "--decisions",
        "--calls",
        "--exclude-unreachable-branches",
        "--exclude-throw-branches",
        "--print-summary"
    ]
    
    result = subprocess.run(
        gcovr_command, 
        cwd=f"{config.PATHS.plugin_output_path}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True, 
        check=True
    )

    # Print the output to the console
    print(result.stdout)

    file_management_utils.create_folder(output_dir)
    full_file_path=f'{output_dir}/gcovr_summary.txt'
    with open(full_file_path, "w") as f:
        f.write(result.stdout)

    print(f"Gcovr summary saved to {full_file_path}")

    return result.stdout


def clean_up(folder_path):
   for file_type in ["*.gcda", "*.gcno"]:
    for file in glob.iglob(os.path.join(folder_path, "**", file_type), recursive=True):
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}") 

def main():
    # Verify gcov is installed
    if not check_gcov_installation():
        sys.exit(1)
    
    # Find source files automatically
    try:
        exclude_dirs=[]
        if config.PLUGIN_FOLDER_EXCLUDES:
            excluded_items = config._config['PLUGIN_FOLDER_EXCLUDES'].items()
            for key,value in excluded_items:
                    exclude_dirs.append(value)

        source_files = find_source_files(config.PATHS.plugin_output_path,config.COVERAGE_ANALYSER.source_extensions,exclude_dirs=exclude_dirs)

        if not source_files:
            print(f"No source files found in {config.PATHS.plugin_output_path} with extensions {config.COVERAGE_ANALYSER.source_extensions}")
            sys.exit(1)
            
        print(f"Found {len(source_files)} source files:")
        for src in source_files:
            print(f"  - {src}")
    
    except Exception as e:
        print(f"Error finding source files: {str(e)}")
        sys.exit(1)
    
    # Generate reports
    try:
        if config.COVERAGE_ANALYSER.generate_gcovr_data:
            generate_gcov_reports(config.PATHS.plugin_output_path,config.PATHS.plugin_output_name,source_files,f"{config.PATHS.main_report_path}/{config.PATHS.gcov_json_output_path}")
        
        if config.COVERAGE_ANALYSER.generate_html_report:
            generate_html_report(f"{os.getcwd()}/{config.PATHS.main_report_path}/{config.PATHS.html_report_path}")
            
    except subprocess.CalledProcessError as e:
        print(f"\nError during coverage generation: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("Starting coverage generation...")
    main()


# python3 -m Plugin_Manager.coverage_generator