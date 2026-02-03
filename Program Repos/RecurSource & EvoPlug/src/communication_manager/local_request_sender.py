import requests
import json

def send_genetic_algorithm_request():
    url = "http://localhost:8008/run"
    headers = {"Content-Type": "application/json"}
    payload = {
        "pop_size": 100,
        "generations": 1000,
        "crossover_prob": 0.8,
        "mutation_prob": 0.8,
        "elitism": 1,
        "target_coverage": 95.0,
        "max_cycles": 1,
        "stagnation_patience":50,
        "enable_mutation": True
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print("Request successful!")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print("Request failed:")
        print(e)

def send_genetic_algorithm_request_compiler_test():
    url = "http://localhost:8028/run"
    headers = {"Content-Type": "application/json"}
    payload = {
        "pop_size": 100,
        "generations": 100,
        "crossover_prob": 0.8,
        "mutation_prob": 0.8,
        "elitism": 1,
        "target_coverage": 95.0,
        "max_cycles": 1,
        "stagnation_patience":50,
        "enable_mutation": True
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print("Request successful!")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print("Request failed:")
        print(e)


def send_genetic_algorithm_request_plugin_crash_test():
    url = "http://localhost:8128/run"
    headers = {"Content-Type": "application/json"}
    payload = {
        "pop_size": 10,
        "generations": 10,
        "crossover_prob": 0.8,
        "mutation_prob": 0.8,
        "elitism": 1,
        "target_coverage": 100.0,
        "max_cycles": 1,
        "stagnation_patience":50,
        "enable_mutation": True
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print("Request successful!")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print("Request failed:")
        print(e)


def main():
    print("Sending genetic algorithm configuration to server...")
    send_genetic_algorithm_request()
    # send_genetic_algorithm_request_compiler_test()
    # send_genetic_algorithm_request_plugin_crash_test()

if __name__ == "__main__":
    main()


# python3 -m src.communication_manager.local_request_sender 