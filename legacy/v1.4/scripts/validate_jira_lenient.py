"""Validate a JIRA short-text screening decision, not the semantic truth of RCA claims."""
import json
import sys
from pathlib import Path

ANCHORS = {
    "specificity": {0, 15, 25, 35},
    "cause_or_condition": {0, 10, 18, 25},
    "actionability": {0, 10, 18, 25},
    "verifiability": {0, 5, 10, 15},
}

def validate_result(data):
    required = {"mode", "score", "level", "jira_pass", "technical_verification",
                "manual_review_required", "dimension_scores", "reason", "suggestion"}
    if set(data) != required:
        raise ValueError("missing or extra result keys")
    if data["mode"] != "jira_lenient_v1_4":
        raise ValueError("unexpected mode")
    if data["technical_verification"] != "unverified":
        raise ValueError("lenient text-only report cannot claim technical verification")
    for key in ("jira_pass", "manual_review_required"):
        if type(data[key]) is not bool:
            raise ValueError(f"{key} must be boolean")
    if set(data["dimension_scores"]) != set(ANCHORS):
        raise ValueError("wrong dimension keys")
    for name, allowed in ANCHORS.items():
        score = data["dimension_scores"][name]
        if type(score) is not int or score not in allowed:
            raise ValueError(f"{name}: invalid anchor")
    total = sum(data["dimension_scores"].values())
    level = "有效" if total >= 60 else "基本有效" if total >= 30 else "信息不足"
    passed = total >= 30 and not data["manual_review_required"]
    if data["score"] != total or data["level"] != level or data["jira_pass"] != passed:
        raise ValueError("inconsistent total, level, or pass status")
    for key in ("reason", "suggestion"):
        if not isinstance(data[key], str):
            raise ValueError(f"{key} must be text")
    return data

def main(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_result(data)
    print(f"VALID lenient score={data['score']} level={data['level']} pass={data['jira_pass']}")

if __name__ == "__main__":
    main(sys.argv[1])
