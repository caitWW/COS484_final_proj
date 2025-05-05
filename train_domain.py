"""
Train tokenizer on a mixture of data domains. Each domain is treated as a category.
"""

import os
import time
import json
import random
from pathlib import Path
from collections import Counter
from tqdm import tqdm
import click
from utils import ensure_dir, truncate_file


def sample_from_unit_simplex(n, M=10000):
    """
    Smith & Trombe algorithm to sample n nonnegative weights summing to 1.
    """
    cuts = random.sample(range(1, M), n - 1)
    cuts = [0] + sorted(cuts) + [M]
    weights = [(cuts[i] - cuts[i-1]) / M for i in range(1, len(cuts))]
    return weights


@click.command()
@click.option(
    '--domains_dir',
    type=str,
    required=True,
    help='Path to root folder containing one subdirectory per domain (e.g., Web, Code, Books).'
)
@click.option(
    '--output_dir',
    type=str,
    required=True,
    help='Where to save trained mixed-domain tokenizer.'
)
@click.option(
    '--total_bytes',
    type=int,
    default=10**10,
    help='Total bytes of text to sample across all domains.'
)
@click.option(
    '--num_categories',
    type=int,
    default=10,
    help='Number of languages to include in the mixed tokenizer training set. Weights will be sampled.'
)
@click.option(
    '--use_spm',
    type=bool,
    default=False,
    help='Whether to use SentencePiece for training instead of HF tokenizers.'
)
def main(domains_dir: str, output_dir: str, total_bytes: int, use_spm: bool, num_categories: int):
    domains_root = Path(domains_dir)
    out_root     = Path(output_dir)
    ensure_dir(out_root)

    # Identify domain categories
    domains = sorted([d.name for d in domains_root.iterdir() if d.is_dir()])
    if not domains:
        raise RuntimeError(f"No domain subdirectories found under {domains_root}")

    # Sample mixture weights
    weights = sample_from_unit_simplex(len(domains))
    print("Mixed-domain distribution:")
    for dom, w in zip(domains, weights):
        print(f"  {dom}: {w:.4f}")

    # Gather text files according to weights
    text_files = []
    byte_counts = {dom: 0 for dom in domains}
    pbar = tqdm(total=total_bytes, desc='Loading text data')

    for dom, w in zip(domains, weights):
        target = int(w * total_bytes)
        dom_dir = domains_root / dom
        files   = [f for f in dom_dir.iterdir() if f.suffix == '.txt' and 'trunc_' not in f.name]
        random.shuffle(files)
        idx = 0
        while byte_counts[dom] < target:
            fpath = files[idx % len(files)]
            sz = fpath.stat().st_size
            if byte_counts[dom] + sz <= target:
                text_files.append(str(fpath))
                byte_counts[dom] += sz
                pbar.update(sz)
            else:
                need = target - byte_counts[dom]
                trunc_name = f"{fpath.stem}_trunc_{need}.txt"
                trunc_path = dom_dir / trunc_name
                os.system(f"cp {fpath} {trunc_path}")
                truncate_file(str(trunc_path), need)
                text_files.append(str(trunc_path))
                byte_counts[dom] += need
                pbar.update(need)
            idx += 1
    pbar.close()

    # Save metadata
    meta = {
        'domains': domains,
        'weights': dict(zip(domains, weights)),
        'byte_count': byte_counts,
        'total_bytes': total_bytes,
        'train_files': Counter(text_files)
    }
    with open(out_root / 'meta.json', 'w') as fo:
        json.dump(meta, fo, indent=2)

    # Train tokenizer
    start_time = time.time()
    if not use_spm:
        from utils import train_tokenizer_or_dump_frequencies
        print('Training with HF tokenizers...')
        tokenizer = train_tokenizer_or_dump_frequencies(text_files)
        tokenizer.model.save(str(out_root))
        tokenizer.save(str(out_root / 'tokenizer.json'))
    else:
        from utils import train_tokenizer_spm
        print('Training with SentencePiece...')
        train_tokenizer_spm(text_files, out_root)
    print(f"Training completed in {time.time() - start_time:.1f}s")

    # Cleanup truncated files
    for f in text_files:
        if 'trunc_' in f:
            try:
                os.remove(f)
            except OSError:
                pass

    print(f"Mixed-domain tokenizer saved to {out_root}")

if __name__ == '__main__':
    main()
