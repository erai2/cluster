from pathlib import Path
import pandas as pd

from classification import train_from_csv, answer_question


def test_train_and_answer(tmp_path: Path):
    data = pd.DataFrame(
        {
            "text": ["system error", "all good", "critical failure"],
            "label": ["issue", "ok", "issue"],
        }
    )
    csv = tmp_path / "data.csv"
    data.to_csv(csv, index=False)

    clf = train_from_csv(csv)
    response = answer_question(clf, "there is a system error")
    assert "issue" in response
