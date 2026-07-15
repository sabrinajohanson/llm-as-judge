import os
import json
from judge import read_test_cases, evaluate_all_test_cases

if __name__ == "__main__":
    test_cases_data = read_test_cases("examples/input_test_cases.json")
    test_cases = test_cases_data["test_cases"]

    results = evaluate_all_test_cases(test_cases)

    output_path = "output/evaluation_results.json"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Evaluation complete. Results saved to {output_path}")