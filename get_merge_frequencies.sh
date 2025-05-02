# Record all merge frequencies to apply our attack in controlled experiments.
test_id=0
experiment_dir=experiments/mixed_languages/n_5/$test_id
lang_code=en
corpus_dir=../data/processed

python -m dump_frequencies \
    --experiment_dir $experiment_dir \
    --lang_code $lang_code \
    --corpus_dir $corpus_dir
