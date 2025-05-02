import json
from pathlib import Path
import subprocess

def get_languages_from_meta(meta_path):
    meta_path = Path(meta_path)
    if not meta_path.exists():
        raise FileNotFoundError(f"No such file: {meta_path}")

    with open(meta_path, "r") as f:
        meta = json.load(f)

    byte_count = meta.get("byte_count", {})
    languages = list(byte_count.keys())
    return languages

def run_dump_frequencies(test_id, lang_list):
    corpus_dir = "../data/processed"
    experiment_dir = f"experiments/mixed_languages/n_5/{test_id}"

    for lang in lang_list:
        print(f"➡️  Running dump_frequencies for: {lang}")
        subprocess.run([
            "python", "-m", "dump_frequencies",
            "--experiment_dir", experiment_dir,
            "--lang_code", lang,
            "--corpus_dir", corpus_dir
        ], check=True)
        print(f"✅ Done with {lang}\n")


if __name__ == "__main__":
    meta_path = "../data/processed/experiments/mixed_languages/n_5/0/meta.json"
    langs = get_languages_from_meta(meta_path)
    print("Languages in byte_count:", langs)
    run_dump_frequencies(0, langs)