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

def run_dump_frequencies(test_id, n, lang_list):
    corpus_dir = "../data/processed/"
    experiment_dir = f"experiments/mixed_languages/n_{n}/{test_id}"

    for lang in lang_list:
        print(f"➡️  Running dump_frequencies for: {lang}")
        subprocess.run([
            "python", "-m", "dump_frequencies",
            "--experiment_dir", experiment_dir,
            "--lang_code", lang,
            "--corpus_dir", corpus_dir
        ], check=True)
        print(f"✅ Done with {lang}\n")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    )
    parser.add_argument("--meta_path")
    parser.add_argument("--exp_num")
    parser.add_argument("--n")
    args = parser.parse_args()
    meta_path = args.meta_path # change this!!!
    langs = get_languages_from_meta(meta_path)
    print("Languages in byte_count:", langs)
    run_dump_frequencies(args.exp_num, args.n, langs) # change this!!!