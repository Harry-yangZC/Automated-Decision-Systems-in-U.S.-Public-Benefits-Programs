import argparse
import json
import os
import re
import time
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv
from openai import APIStatusError, OpenAI

load_dotenv()

STATE_FULL_NAMES = {
    "MA": "Massachusetts",
    "RI": "Rhode Island",
    "CA": "California",
    "NY": "New York",
    "TX": "Texas",
}

DEFAULT_MODELS = [
    "google/gemma-4-26b-a4b-it",
    "openai/gpt-oss-120b:free",
    "anthropic/claude-opus-4.7",
]

SYSTEM_PROMPT = (
    "You are a research assistant helping document public benefits programs in the United States. "
    "Answer questions using only official U.S. state government websites and publicly available government sources. "
    "Respond with a JSON object containing exactly these fields:\n"
    '  "answer": your answer to the question (string),\n'
    '  "source": the URL or name of the official source you used (string),\n'
    '  "confidence": one of "high", "medium", or "low" indicating how confident you are in the answer (string).\n'
    "If you cannot find a reliable answer, set answer to null and confidence to \"low\"."
)


def extract_json(text: str) -> dict:
    """Extract a JSON object from model output that may contain extra text."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("No valid JSON object found", text, 0)


def build_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not found in environment. Check your .env file.")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def build_user_prompt(question_template: str, program: str, state_abbr: str) -> str:
    state_full = STATE_FULL_NAMES.get(state_abbr, state_abbr)
    return question_template.replace("{program}", program).replace("{state}", state_full)


UPSTREAM_RETRY_WAIT = 15.0
UPSTREAM_MAX_RETRIES = 2


def _is_upstream_throttle(exc: APIStatusError) -> bool:
    return exc.status_code == 429 and "Provider returned error" in str(exc)


def query_model(client: OpenAI, model_id: str, user_prompt: str) -> dict:
    """Send a single prompt to an OpenRouter model and return the parsed result."""
    last_exc = None

    for attempt in range(1, UPSTREAM_MAX_RETRIES + 1):
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_content = completion.choices[0].message.content or ""
            try:
                parsed = extract_json(raw_content)
            except json.JSONDecodeError:
                return {
                    "response_json": raw_content,
                    "answer_extracted": None,
                    "source": None,
                    "confidence": None,
                    "error": "JSON parse error",
                }
            return {
                "response_json": raw_content,
                "answer_extracted": parsed.get("answer"),
                "source": parsed.get("source"),
                "confidence": parsed.get("confidence"),
                "error": None,
            }
        except APIStatusError as exc:
            last_exc = exc
            if _is_upstream_throttle(exc) and attempt < UPSTREAM_MAX_RETRIES:
                print(f"  -> upstream throttled (attempt {attempt}/{UPSTREAM_MAX_RETRIES}), retrying in {UPSTREAM_RETRY_WAIT:.0f}s ...")
                time.sleep(UPSTREAM_RETRY_WAIT)
                continue
            break
        except Exception as exc:
            last_exc = exc
            break

    return {
        "response_json": None,
        "answer_extracted": None,
        "source": None,
        "confidence": None,
        "error": str(last_exc),
    }


def load_benchmark(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def get_state_columns(benchmark_df: pd.DataFrame) -> list[str]:
    """Return the state-abbreviation columns (everything after Questions and Programs)."""
    return [c for c in benchmark_df.columns if c not in ("Questions", "Programs")]


def run_experiment(
    benchmark_path: str,
    model_ids: list[str],
    output_path: str,
    delay: float = 3.0,
    num_runs: int = 5,
) -> None:
    client = build_client()
    benchmark = load_benchmark(benchmark_path)
    state_cols = get_state_columns(benchmark)

    existing_results = []
    completed_keys: set[tuple] = set()
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        try:
            existing_df = pd.read_csv(output_path)
            all_rows = existing_df.to_dict("records")
            for r in all_rows:
                err_val = r.get("error")
                has_error = err_val is not None and not (isinstance(err_val, float) and pd.isna(err_val))
                if not has_error:
                    existing_results.append(r)
                    completed_keys.add((
                        r.get("question_template"),
                        r.get("program"),
                        r.get("state"),
                        r.get("model"),
                        r.get("run_number"),
                    ))
            n_errors = len(all_rows) - len(existing_results)
            print(f"Loaded {len(existing_results)} successful result(s) from {output_path}"
                  f" ({n_errors} previous error(s) will be retried)")
        except Exception:
            pass

    results = list(existing_results)
    total_calls = len(benchmark) * len(state_cols) * len(model_ids) * num_runs
    completed = 0

    for _, row in benchmark.iterrows():
        question_template = row["Questions"]
        program = row["Programs"]

        for state_abbr in state_cols:
            for run_num in range(1, num_runs + 1):
                for model_id in model_ids:
                    completed += 1
                    user_prompt = build_user_prompt(question_template, program, state_abbr)

                    key = (question_template, program, state_abbr, model_id, run_num)
                    if key in completed_keys:
                        continue

                    if delay > 0:
                        time.sleep(delay)

                    print(f"[{completed}/{total_calls}] model={model_id}  program={program}  state={state_abbr}  run={run_num}")

                    result = query_model(client, model_id, user_prompt)
                    result.update({
                        "question_template": question_template,
                        "program": program,
                        "state": state_abbr,
                        "model": model_id,
                        "run_number": run_num,
                        "prompt_sent": user_prompt,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                    results.append(result)

    out_df = pd.DataFrame(results)
    column_order = [
        "question_template", "program", "state", "model", "run_number",
        "prompt_sent", "response_json", "answer_extracted",
        "source", "confidence", "timestamp", "error",
    ]
    for col in column_order:
        if col not in out_df.columns:
            out_df[col] = None
    out_df = out_df[column_order]

    out_df.to_csv(output_path, index=False)
    print(f"\nDone. {len(results)} total result(s) written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run LLM experiments on Benefits Decoded benchmark questions via OpenRouter."
    )
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated OpenRouter model IDs (default: 2 free models + claude-opus-4.7 (paid))",
    )
    parser.add_argument(
        "--benchmark",
        default="data/benchmark.csv",
        help="Path to the benchmark CSV (default: data/benchmark.csv)",
    )
    parser.add_argument(
        "--output",
        default="exp_results/LLM_experiments.csv",
        help="Path to the output experiment CSV (default: exp_results/LLM_experiments.csv)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Seconds to wait between API calls (default: 3.0)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of times to run each (question, model) combination (default: 5)",
    )
    args = parser.parse_args()

    model_ids = [m.strip() for m in args.models.split(",") if m.strip()]
    if not model_ids:
        parser.error("At least one model ID is required.")

    run_experiment(
        benchmark_path=args.benchmark,
        model_ids=model_ids,
        output_path=args.output,
        delay=args.delay,
        num_runs=args.runs,
    )


if __name__ == "__main__":
    main()
