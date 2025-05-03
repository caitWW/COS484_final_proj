#!/usr/bin/env bash
set -euo pipefail

# ─── CONFIGURE YOUR SWEEP ───────────────────────────────────────────────────────
# list of n values to try:
ns=(5 10 30 112)

# list of test_id values to try:
test_ids=(1 2 3 4 5)

# base dirs (you can tweak these if your layout changes)
corpus_dir="../data/processed"
base_exp_dir="../data/processed/experiments/mixed_languages"

# ─── SWEEP LOOP ─────────────────────────────────────────────────────────────────
for n in "${ns[@]}"; do
  for test_id in "${test_ids[@]}"; do
    echo
    echo "=== Running pipeline for n=$n, test_id=$test_id ==="

    output_dir="$base_exp_dir/n_${n}/${test_id}"
    mkdir -p "$output_dir"

    # Step 1: train tokenizer
    echo "→ Step 1: Training tokenizer on mix of $n categories"
    python -m train_mixed_tokenizer \
      --output_dir "$output_dir" \
      --num_categories "$n" \
      --corpus_dir "$corpus_dir"

    # Step 2: record merge frequencies
    echo "→ Step 2: Recording merge frequencies"
    python -m get_merge_frequencies \
      --meta_path "$output_dir/meta.json" \
      --exp_num "$test_id" \
      --n "$n"

    # Step 3: run solver
    echo "→ Step 3: Running solver to infer language mixture"
    python -m run_solver "$output_dir"

    echo "✔ Pipeline completed for n=$n, test_id=$test_id"
  done
done

echo
echo "All runs finished."
