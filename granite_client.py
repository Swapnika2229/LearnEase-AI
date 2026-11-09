import os, requests
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# VERIFIED MODEL AVAILABILITY — au-syd (Sydney) region
# Queried live from https://au-syd.ml.cloud.ibm.com/ml/v1/foundation_model_specs
# on 2026-11-05 with filters=function_text_generation
#
# Only ONE model supports function_text_generation for direct inference
# (i.e. callable via /ml/v1/text/generation with model_id, no deployment step):
#
#   meta-llama/llama-3-3-70b-instruct  ✅  lifecycle: available
#
# All other models at au-syd either:
#   - Only support base_foundation_model_deployable (must be deployed first)
#   - Only support time_series_forecast or embedding (wrong task type)
#
# Previously attempted models and why they fail:
#   ibm/granite-4-h-small    → not in Sydney's spec list at all for direct inference
#   ibm/granite-3-8b-instruct → not in Sydney's spec list for direct inference
#   ibm/granite-3-1-8b-base  → only base_foundation_model_deployable (no instruct)
# ---------------------------------------------------------------------------

SYDNEY_URL = "https://au-syd.ml.cloud.ibm.com"
DEFAULT_MODEL = "meta-llama/llama-3-3-70b-instruct"


def get_iam_token(api_key):
    r = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def generate_learning_content(source, level, output_type):
    api_key = os.getenv("IBM_CLOUD_API_KEY", "").strip()
    project_id = os.getenv("WATSONX_PROJECT_ID", "").strip()
    service_url = os.getenv("WATSONX_URL", SYDNEY_URL).strip().rstrip("/")
    model_id = os.getenv("GRANITE_MODEL_ID", DEFAULT_MODEL).strip()

    # Validate credentials before making any network calls
    if not api_key or api_key.startswith("your_"):
        raise ValueError(
            "IBM Cloud API key is missing or still a placeholder. "
            "Open .env and set IBM_CLOUD_API_KEY to your real key."
        )
    if not project_id or project_id.startswith("your_"):
        raise ValueError(
            "watsonx.ai Project ID is missing or still a placeholder. "
            "Open .env and set WATSONX_PROJECT_ID to your real project ID."
        )

    # Per-output-type instructions — precise, structured, no waffle
    task_instructions = {
        "Complete study pack": """\
Produce a thorough and detailed complete study pack. Write ALL seven sections in full. Do not abbreviate, truncate, or skip any section.

## 1. Definition
Write one clear, accurate sentence that precisely defines the topic.

## 2. Simple Explanation
Explain the topic in plain language suitable for the specified level. Write at least 4-6 sentences, breaking the concept down step by step. Assume no prior knowledge for Beginner; moderate knowledge for Intermediate; strong knowledge for Exam-focused.

## 3. Key Points
List 6-8 of the most important facts, principles, or concepts as bullet points. Each bullet should be a complete, informative sentence, not just a label.

## 4. Important Terms
Provide a glossary of 5-8 key terms. Format each as:
**Term**: definition in one or two sentences.

## 5. Real-Life Examples
Give 3 concrete, specific, real-world examples that clearly illustrate the topic. For each example, write 2-3 sentences: name the example, explain what it is, and explain how it demonstrates the topic.

## 6. Exam Questions and Answers
Write exactly 5 exam-style questions with detailed model answers. Mix question types: include at least 2 short-answer questions and 2 descriptive questions. Format each as:
**Q1:** [question]
**A1:** [detailed answer — at least 3 sentences]

## 7. Revision Summary
Write 4-6 sentences summarising the most important concepts, terms, and takeaways. This section should serve as a final memory-aid for exam preparation.

Output all seven sections in order. Do not add any introduction before Section 1 or any sign-off after Section 7.""",

        "Simple explanation": """\
Write a plain-language explanation of the topic suitable for a student at the specified level.
Structure:
- One sentence defining the topic.
- Step-by-step explanation (3-6 numbered steps or short paragraphs).
- A brief note on why this topic matters.
Do not add greetings, sign-offs, or unrelated commentary. Output the explanation only.""",

        "Structured notes": """\
Produce structured revision notes using this layout:
- Definition: one sentence.
- Key Concepts: bullet points, one concept per bullet.
- Important Terms: term — definition, one per line.
- Key Facts to Remember: bullet list of critical points.
- Common Exam Pitfalls: bullet list (if applicable).
Use concise language. Do not add introductions or sign-offs.""",

        "Examples": """\
Provide 4-6 concrete, real-world examples of the topic.
For each example:
  - State the example clearly in one sentence.
  - Explain in 1-2 sentences how it illustrates the topic.
Number each example. Do not add greetings, sign-offs, or padding.""",

        "Practice questions and answers": """\
Generate exactly 10 exam-style practice questions with model answers.
- Questions 1-5: short-answer (1-3 sentences each answer).
- Questions 6-10: descriptive/essay-style (4-8 sentences each answer).
Format each as:
Q[n]: [question]
A[n]: [answer]
Do not add introductions, transitions between questions, or sign-offs.""",

        "Quick summary": """\
Write a concise revision summary of the topic in 5-8 bullet points.
Each bullet must capture one key concept, fact, or term.
End with a single sentence stating the overall significance of the topic.
Do not add introductions, greetings, or sign-offs.""",
    }

    # System-level rules applied to every output type
    system_rules = """\
Rules you must follow without exception:
- Output only the content requested. Do not include greetings, sign-offs, "let me know if you need more", "ask me anything", promotional language, or repeated disclaimers.
- Do not repeat the task instructions back to the user.
- Do not repeat the disclaimer more than once. Place it only at the very end as a single line: "Note: Verify all information against your course materials."
- Use plain, precise academic English appropriate for the specified level.
- Preserve technical accuracy. Do not invent facts, references, or examples.
- Use Markdown headings (##) and bullet points (-) for structure."""

    prompt = f"""{system_rules}

Level: {level}
Topic or source material:
{source}

Task:
{task_instructions[output_type]}"""

    token = get_iam_token(api_key)

    url = f"{service_url}/ml/v1/text/generation?version=2024-05-31"
    payload = {
        "model_id": model_id,
        "project_id": project_id,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 4000,
            "min_new_tokens": 50,
            "repetition_penalty": 1.05,
        },
    }
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=payload,
        timeout=120,
    )

    if not r.ok:
        raw = r.text[:1500]
        if "model_not_supported" in raw:
            raise RuntimeError(
                f"Model '{model_id}' is not supported for direct inference at {service_url}.\n\n"
                "Verified available model for Sydney (au-syd) direct text generation:\n"
                "  GRANITE_MODEL_ID=meta-llama/llama-3-3-70b-instruct\n\n"
                "To re-verify, query:\n"
                f"  {service_url}/ml/v1/foundation_model_specs"
                "?version=2024-05-31&filters=function_text_generation\n\n"
                f"IBM API response: {raw}"
            )
        if "model_no_support_for_function" in raw:
            raise RuntimeError(
                f"Model '{model_id}' does not support text generation.\n\n"
                "It may be a base or embedding model. "
                "Use the verified instruct model for Sydney:\n"
                "  GRANITE_MODEL_ID=meta-llama/llama-3-3-70b-instruct\n\n"
                f"IBM API response: {raw}"
            )
        if "no_associated_service_instance" in raw:
            raise RuntimeError(
                "No watsonx.ai Runtime service instance is associated with your project.\n\n"
                "Go to watsonx.ai → your project → Manage → Services & integrations "
                "and associate a Watson Machine Learning (WML) service instance.\n\n"
                f"IBM API response: {raw}"
            )
        raise RuntimeError(f"IBM API error {r.status_code}: {raw}")

    results = r.json().get("results", [])
    if not results:
        raise RuntimeError(
            f"IBM watsonx.ai returned no results. Raw response: {r.text[:900]}"
        )

    return results[0].get("generated_text", "").strip()
