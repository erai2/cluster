from saju_database import (
    parse_basic_theory_text,
    parse_terminology_text,
    parse_case_study_text,
)


def test_parse_terminology_text():
    text = (
        "단원: Part 1. 상법(象法)\n"
        "분류: 궁위의 상\n"
        "용어: 십신\n"
        "의미: 천간과 지지의 관계를 열 가지로 분류한 명리학 용어"
    )
    data = parse_terminology_text(text)
    assert data["term"] == "십신"
    assert data["part"] == "Part 1. 상법(象法)"
    assert data["category"] == "궁위의 상"


def test_parse_basic_theory_text():
    text = (
        "단원: Part 2. 象의 응용 - 실전 예문\n"
        "카테고리: 관인상생\n"
        "개념: 관인상생\n"
        "상세: 관인상생 구조는 학업운이 왕성함을 뜻한다"
    )
    data = parse_basic_theory_text(text)
    assert data["concept"] == "관인상생"
    assert data["category"] == "관인상생"


def test_parse_case_study_text():
    text = (
        "단원: Part 2. 象의 응용 - 실전 예문\n"
        "분류: 관인상생\n"
        "출생정보: 1990-01-01 12:00\n"
        "명식: 갑오년 병자월 정축일 경인시\n"
        "분석: 관인상생 구조로 학업운이 왕성\n"
        "결과: 국가고시 합격"
    )
    data = parse_case_study_text(text)
    assert data["birth_info"].startswith("1990-01-01")
    assert "관인상생" in data["analysis"]
