# Train tokenizer on a randomly sampled mix of n data categories, saving the output in output_dir.
n=2
test_id=4
output_dir=../data/processed/experiments/mixed_languages/n_${n}/$test_id # where output saved
corpus_dir=../data/processed # where data is 

'''
echo "Training tokenizers on mixes of $num_categories languages"
python -m train_mixed_tokenizer \
    --output_dir $output_dir \
    --num_categories $n \
    --corpus_dir $corpus_dir
'''

# Step 2: Run get_merge_frequencies.py
echo "Recording merge frequencies for language $lang_code"
python -m get_merge_frequencies \
    --meta_path $output_dir/meta.json \
    --exp_num $test_id \
    --n $n \

# Step 3: Run solver
echo "Step 3: Running solver to infer language mixture"
python -m run_solver \
    $output_dir

echo "Pipeline completed. Results saved in $output_dir"
