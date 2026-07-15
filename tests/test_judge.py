import json
from unittest.mock import patch, MagicMock
import pytest
from judge import read_test_cases, build_judge_prompt, evaluate_test_case, evaluate_all_test_cases


def test_read_test_cases(tmp_path):
    # Arrange: create a temporary JSON file with known content
    test_cases_file = tmp_path / "input_test_cases.json"
    test_cases_file.write_text(
        json.dumps({"test_cases": [{"id": "TC-001", "title": "Sample test"}]}),
        encoding="utf-8"
    )

    # Act
    result = read_test_cases(str(test_cases_file))

    # Assert
    assert result["test_cases"][0]["id"] == "TC-001"


def test_build_judge_prompt_contains_test_case_id():

    test_case = {"id": "TC-002", "title": "Sample test", "layer": "unit"}

    prompt = build_judge_prompt(test_case)

    # Assert: confirm the test case id is embedded in the generated prompt
    assert "TC-002" in prompt


def test_evaluate_test_case_success():
    # Arrange: build a fake OpenAI response matching the real judge schema
    fake_json_response = json.dumps({
        "test_case_id": "TC-001",
        "scores": {
            "clarity": 5,
            "step_validity": 5,
            "verifiable_expected_result": 5,
            "layer_correctness": 5,
            "tbd_appropriateness": 5
        },
        "overall_verdict": "pass",
        "justification": "Well-written test case with clear expected results."
    })

    mock_response = MagicMock()
    mock_response.choices[0].message.content = fake_json_response

    # Act: patch only the API call
    with patch("judge.client.chat.completions.create", return_value=mock_response):
        result = evaluate_test_case({"id": "TC-001", "title": "Sample test"})

    # Assert
    assert result["test_case_id"] == "TC-001"
    assert result["overall_verdict"] == "pass"


def test_evaluate_test_case_invalid_json():
    # Arrange: simulate the API returning a malformed, non-JSON response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is not valid JSON"

    with patch("judge.client.chat.completions.create", return_value=mock_response):
        with pytest.raises(json.JSONDecodeError):
            evaluate_test_case({"id": "TC-001", "title": "Sample test"})


def test_evaluate_all_test_cases_aggregates_results():
    # Arrange: mock evaluate_test_case itself, since this function's own logic
    # (looping and aggregating) is what we want to test here, not the API call
    fake_evaluation = {
        "test_case_id": "TC-001",
        "scores": {"clarity": 5, "step_validity": 5, "verifiable_expected_result": 5,
                    "layer_correctness": 5, "tbd_appropriateness": 5},
        "overall_verdict": "pass",
        "justification": "Looks good."
    }

    with patch("judge.evaluate_test_case", return_value=fake_evaluation) as mock_evaluate:
        result = evaluate_all_test_cases([{"id": "TC-001"}, {"id": "TC-002"}])

    # Assert: confirm it looped over both test cases and aggregated correctly
    assert mock_evaluate.call_count == 2
    assert len(result["evaluations"]) == 2