import json
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

# Two Mistral variants: standard (Q4_0) and K-means quantized (Q4_K_M)
MODELS = {
    "mistral": "mistral",
    "mistral_quantized": "mistral:7b-instruct-q4_K_M",
}

# 5 selected requirements from the group project
REQUIREMENTS = [
    {
        "requirement_id": "REQ-117.130-001B",
        "description": "Identify known hazards",
        "source": "21 CFR 117.130",
    },
    {
        "requirement_id": "REQ-117.130-001F",
        "description": "Hazard analysis must be written",
        "source": "21 CFR 117.130",
    },
    {
        "requirement_id": "REQ-117.130-002A",
        "description": "Biological hazards",
        "source": "21 CFR 117.130",
    },
    {
        "requirement_id": "REQ-117.130-003A1",
        "description": "Assess severity and probability of hazard occurrence",
        "source": "21 CFR 117.130",
    },
    {
        "requirement_id": "REQ-117.130-003A2",
        "description": "Evaluate environmental pathogens for ready-to-eat foods",
        "source": "21 CFR 117.130",
    },
]


def build_prompt(req, tc_id):
    return f"""You are a software quality assurance engineer working with FDA food safety regulations (21 CFR 117.130).

Generate a structured test case for the following requirement:
  Requirement ID: {req['requirement_id']}
  Description: {req['description']}
  Source: {req['source']}

Respond ONLY with a valid JSON object in this exact format (no extra text):
{{
  "test_case_id": "{tc_id}",
  "requirement_id": "{req['requirement_id']}",
  "description": "<what this test verifies>",
  "input_data": "<what input the test uses>",
  "expected_output": "<what result is expected>",
  "steps": ["<step 1>", "<step 2>", "<step 3>"],
  "notes": "<any assumptions or special conditions>"
}}"""


def call_ollama(model, prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"].strip()


def extract_json(raw):
    # Find the first { and last } to extract JSON even if the model adds extra text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        return None
    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError:
        return None


def generate_for_model(label, model_name):
    print(f"\n--- Generating with {label} ({model_name}) ---")
    results = []
    for i, req in enumerate(REQUIREMENTS, 1):
        tc_id = f"TC-LLM-{label.upper()[:3]}-{i:03d}"
        prompt = build_prompt(req, tc_id)
        print(f"  [{i}/5] {req['requirement_id']} ... ", end="", flush=True)
        try:
            raw = call_ollama(model_name, prompt)
            parsed = extract_json(raw)
            if parsed:
                results.append(parsed)
                print("OK")
            else:
                print("PARSE ERROR — saving raw")
                results.append({
                    "test_case_id": tc_id,
                    "requirement_id": req["requirement_id"],
                    "raw_output": raw,
                    "error": "Could not parse JSON from model output",
                })
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "test_case_id": tc_id,
                "requirement_id": req["requirement_id"],
                "error": str(e),
            })
        time.sleep(1)
    return results


if __name__ == "__main__":
    all_results = {}

    for label, model_name in MODELS.items():
        results = generate_for_model(label, model_name)
        all_results[label] = results
        out_file = f"{label}_test_cases.json"
        with open(out_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"  Saved {out_file}")

    print("\nfinished!")
