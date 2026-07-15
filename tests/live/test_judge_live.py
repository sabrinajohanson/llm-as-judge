from judge import evaluate_test_case

ALLOWED_VERDICTS = {"pass", "fail"}
REQUIRED_SCORE_KEYS = {"clarity", "step_validity", "verifiable_expected_result", "layer_correctness", "tbd_appropriateness"}


def test_evaluate_test_case_real_api_contract():
    # Arrange: a real test case to be judged
    test_case = {
        "id": "TC-001",
        "title": "Valid login with email and password",
        "description": "Verifies that a user can log in with valid email and password.",
        "type": "positive",
        "layer": "unit",
        "priority": "high",
        "steps": ["Enter a valid email.", "Enter a valid password.", "Submit the login form."],
        "expected_result": "User is successfully logged in."
    }

    # Act: calls the real OpenAI API, no mocking here
    result = evaluate_test_case(test_case)

    # Assert: validate the response structure and internal consistency, not exact content
    assert result["test_case_id"] == "TC-001"
    assert result["overall_verdict"] in ALLOWED_VERDICTS

    missing_keys = REQUIRED_SCORE_KEYS - result["scores"].keys()
    assert not missing_keys, f"Missing score fields: {missing_keys}"

    for score in result["scores"].values():
        assert isinstance(score, int)
        assert 1 <= score <= 5

    # Business rule check: if any score is 1 or 2, verdict must be "fail"
    has_low_score = any(score <= 2 for score in result["scores"].values())
    if has_low_score:
        assert result["overall_verdict"] == "fail"