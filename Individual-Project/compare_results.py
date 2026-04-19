import json

REQUIRED_FIELDS = ["test_case_id", "requirement_id", "description", "input_data", "expected_output"]
OPTIONAL_FIELDS = ["steps", "notes"]

REQUIREMENT_KEYWORDS = {
    "REQ-117.130-001B": ["known", "hazard"],
    "REQ-117.130-001F": ["written", "document", "record"],
    "REQ-117.130-002A": ["biological", "pathogen", "microbial"],
    "REQ-117.130-003A1": ["severity", "probability", "likelihood"],
    "REQ-117.130-003A2": ["environmental", "pathogen", "ready-to-eat", "rte"],
}

REQUIREMENT_IDS = list(REQUIREMENT_KEYWORDS.keys())


def load(path):
    with open(path) as f:
        return json.load(f)


def check_coverage(test_cases, label):
    covered = {tc["requirement_id"] for tc in test_cases if "requirement_id" in tc}
    print(f"\nCoverage - {label}")
    for rid in REQUIREMENT_IDS:
        status = "covered" if rid in covered else "missing"
        print(f"  {rid}: {status}")
    print(f"  total: {len(covered)}/{len(REQUIREMENT_IDS)}")
    return covered


def check_completeness(test_cases, label):
    print(f"\nCompleteness - {label}")
    scores = []
    for tc in test_cases:
        rid = tc.get("requirement_id", "unknown")
        missing = [f for f in REQUIRED_FIELDS if f not in tc or not tc[f]]
        has_optional = [f for f in OPTIONAL_FIELDS if f in tc and tc[f]]
        scores.append(len(REQUIRED_FIELDS) - len(missing))
        if missing:
            print(f"  {rid}: missing {missing}")
        else:
            optional_note = f", optional fields present: {has_optional}" if has_optional else ""
            print(f"  {rid}: all required fields present{optional_note}")
    avg = sum(scores) / len(scores) if scores else 0
    print(f"  avg: {avg:.1f}/{len(REQUIRED_FIELDS)}")
    return scores


def check_correctness(test_cases, label):
    print(f"\nCorrectness - {label}")
    results = []
    for tc in test_cases:
        rid = tc.get("requirement_id", "")
        desc = (tc.get("description", "") + " " + tc.get("input_data", "")).lower()
        keywords = REQUIREMENT_KEYWORDS.get(rid, [])
        matched = [kw for kw in keywords if kw in desc]
        correct = len(matched) > 0
        results.append(correct)
        if correct:
            print(f"  {rid}: ok (matched: {matched})")
        else:
            print(f"  {rid}: description may not match requirement (no keywords found)")
    return results


def summarize(label, coverage, completeness, correctness):
    cov_pct = len(coverage) / len(REQUIREMENT_IDS) * 100
    comp_pct = sum(completeness) / (len(completeness) * len(REQUIRED_FIELDS)) * 100 if completeness else 0
    corr_pct = sum(correctness) / len(correctness) * 100 if correctness else 0
    print(f"\nSummary - {label}")
    print(f"  coverage:     {cov_pct:.0f}%")
    print(f"  completeness: {comp_pct:.0f}%")
    print(f"  correctness:  {corr_pct:.0f}%")
    return {"coverage": cov_pct, "completeness": comp_pct, "correctness": corr_pct}


if __name__ == "__main__":
    mistral_tc = load("mistral_test_cases.json")
    quantized_tc = load("mistral_quantized_test_cases.json")

    print("Comparing Mistral 7B vs Mistral 7B Q4_K_M")

    cov_m = check_coverage(mistral_tc, "Mistral")
    cov_q = check_coverage(quantized_tc, "Mistral Quantized")

    comp_m = check_completeness(mistral_tc, "Mistral")
    comp_q = check_completeness(quantized_tc, "Mistral Quantized")

    corr_m = check_correctness(mistral_tc, "Mistral")
    corr_q = check_correctness(quantized_tc, "Mistral Quantized")

    summary_m = summarize("Mistral 7B", cov_m, comp_m, corr_m)
    summary_q = summarize("Mistral 7B Q4_K_M", cov_q, comp_q, corr_q)

    print("\nHead-to-head:")
    for metric in ["coverage", "completeness", "correctness"]:
        diff = summary_m[metric] - summary_q[metric]
        note = "tie" if diff == 0 else ("mistral higher" if diff > 0 else "quantized higher")
        print(f"  {metric}: mistral={summary_m[metric]:.0f}%  quantized={summary_q[metric]:.0f}%  ({note})")

    with open("comparison_summary.json", "w") as f:
        json.dump({"mistral": summary_m, "mistral_quantized": summary_q}, f, indent=2)
    print("\nSaved comparison_summary.json")
