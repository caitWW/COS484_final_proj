#!/usr/bin/env bash
set -euo pipefail

echo ">>> pipeline.sh sees GRB_LICENSE_FILE=$GRB_LICENSE_FILE"
ls -l $GRB_LICENSE_FILE || ( echo "License file missing!" && exit 1 )

# optionally re-export just to be absolutely sure:
export GRB_LICENSE_FILE=/home/qw3971/gurobi.lic

# ─── 0) LOAD AMD COMPILERS & MATH LIBRARIES ─────────────────────────────────────
# this makes clang/clang++ available as 'clang' and brings BLIS, libFLAME, FFTW, etc.
# if you have MPI steps that use C:
# module load openmpi/aocc-5.0.0/4.1.6

# ─── 1) CONFIGURE YOUR SWEEP ─────────────────────────────────────────────────────
ns=(5)
test_ids=(0 1 2 3 4 5 6 7 8 9 10)

corpus_dir="../RedPajama/domains"
base_exp_dir="../RedPajama/domains/experiments/domains"


# ─── 2) OPTIONAL: COMPILE ANY C/C++ EXTENSIONS ───────────────────────────────────
# If you have a C/C++ program you need to compile before the Python steps, do it here:
# clang++ -Ofast -march=native -o bin/my_extension src/my_extension.cpp

# ─── 3) SWEEP ────────────────────────────────────────────────────────────────────
for n in "${ns[@]}"; do
  for test_id in "${test_ids[@]}"; do
    echo
    echo "=== Running pipeline for n=$n, test_id=$test_id ==="
    output_dir="$base_exp_dir/n_${n}/${test_id}"
    mkdir -p "$output_dir"

    # Step 1: train tokenizer
    echo "→ Step 1: Training tokenizer on mix of $n categories"
    python -m train_domain \
      --output_dir "$output_dir" \
      --num_categories "$n" \
      --domains_dir "$corpus_dir"

    # Step 2: record merge frequencies
    echo "→ Step 2: Recording merge frequencies"
    python -m get_merge_frequencies_domain \
      --meta_path "$output_dir/meta.json" \
      --exp_num "$test_id" \
      --n "$n"

    # Step 3: run solver
    #echo "→ Step 3: Running solver to infer language mixture"
    #python -m run_solver "$output_dir"

    echo "✔ Pipeline completed for n=$n, test_id=$test_id"
  done
done

echo
echo "All runs finished."
