import re
import os
import sys
import requests
from concurrent.futures import ThreadPoolExecutor

def test_proxy(proxy):
    """
    Test a single proxy by making a request and returning the HTTP status code.
    """
    url = 'http://httpbin.org/ip'  # A simple URL to check proxy functionality
    proxies = {'http': proxy, 'https': proxy}

    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        if response.status_code in {200, 403, 503}:
            return response.status_code
        else:
            return None
    except requests.RequestException:
        return None

def process_proxy(proxy, output_file):
    """
    Process a single proxy: test it, and save the result to the output file.
    """
    status_code = test_proxy(proxy)
    with open(output_file, 'a') as outfile:
        if status_code:
            outfile.write(f"{proxy}: HTTP_CODE={status_code}\n")
            print(f"{proxy}: HTTP_CODE={status_code}")
        else:
            outfile.write(f"{proxy}: ✗\n")
            #print(f"{proxy}: ✗")

def check_proxies_and_save(input_file_path, output_file_path):
    """
    Read a list of proxies from the input file, test each proxy in parallel,
    and save the results to an output file.
    """
    if not os.path.exists(input_file_path):
        print(f"Input file '{input_file_path}' does not exist.")
        sys.exit(1)
    
    with open(input_file_path, 'r') as infile:
        proxies = [proxy.strip() for proxy in infile.readlines() if proxy.strip()]

    if not proxies:
        print("There are no proxies in the input file. Please enter some.")
        sys.exit(1)
    else:
        print("Proxies found, starting filter.")


    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust the number of workers as needed
        for proxy in proxies:
            executor.submit(process_proxy, proxy, output_file_path)

def filter_and_check_proxies(input_file_path, output_file_path):
    """
    Filter the tested proxies from the input file and save the usable ones to the output file.
    """
    if not os.path.exists(input_file_path):
        print(f"File '{input_file_path}' not found. No proxies to filter.")
        sys.exit(1)
    
    usable_pattern = re.compile(r'HTTP_CODE=(200|403|407|503)')

    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        lines = infile.readlines()
        for line in lines:
            if usable_pattern.search(line):
                proxy = line.split(':')[0]  # Extract proxy address
                outfile.write(f"Usable Proxy: {line.split(':')[0]}:{line.split(':')[1]}\n")

def clear_output_files(*file_paths):
    """
    Clear the content of output files or delete them if they exist.
    """
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    input_proxies_file = 'proxies.txt'
    proxy_test_output_file = 'proxy_output.txt'
    filtered_proxies_file = 'filtered_proxies.txt'

    # Clear previous output files
    clear_output_files(proxy_test_output_file, filtered_proxies_file)

    # Step 1: Test the proxies and save the results
    check_proxies_and_save(input_proxies_file, proxy_test_output_file)

    # Step 2: Filter the tested proxies to keep only usable ones
    filter_and_check_proxies(proxy_test_output_file, filtered_proxies_file)

    print(f"Filtering complete. Check '{filtered_proxies_file}' for results.")

    print(f"Check '{proxy_test_output_file}' for complete results.")

if __name__ == '__main__':
    main()

