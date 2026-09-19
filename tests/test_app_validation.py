import app


def test_rejects_non_list_questions():
    assert app._validate_query_inputs("not a list", None, None) is not None


def test_rejects_empty_questions():
    assert app._validate_query_inputs([], None, None) is not None


def test_rejects_blank_question_string():
    assert app._validate_query_inputs(["   "], None, None) is not None


def test_rejects_too_many_questions():
    questions = ["q"] * (app.MAX_QUESTIONS_PER_REQUEST + 1)
    assert app._validate_query_inputs(questions, None, None) is not None


def test_rejects_oversized_question():
    long_question = "a" * (app.MAX_QUESTION_LENGTH + 1)
    assert app._validate_query_inputs([long_question], None, None) is not None


def test_rejects_non_string_pdf_url():
    assert app._validate_query_inputs(["ok"], 12345, None) is not None


def test_rejects_non_list_policy_filter():
    assert app._validate_query_inputs(["ok"], None, "not-a-list") is not None


def test_accepts_valid_input():
    assert app._validate_query_inputs(["What is covered?"], "https://example.com/p.pdf", ["a.pdf"]) is None
