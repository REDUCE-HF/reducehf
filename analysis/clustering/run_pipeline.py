#!/usr/bin/env python3
"""
Run the clustering pipeline.

Usage:
    python analysis/clustering/run_pipeline.py              # Run with real data
    python analysis/clustering/run_pipeline.py --synthetic  # Run with synthetic data
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import config


def run(cmd, env=None):
    """Run a shell command, exit if it fails."""
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, env=env)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Run clustering pipeline.")
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic data instead of real data")
    args = parser.parse_args()

    # Set up environment to use synthetic paths if requested
    env = os.environ.copy()
    if args.synthetic:
        env["USE_SYNTHETIC_INPUTS"] = "1"

    # Create output directories
    Path(config.REAL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.SYNTHETIC_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Data preparation step
    if args.synthetic:
        print("\n" + "=" * 70)
        print("GENERATING SYNTHETIC DATA")
        print("=" * 70)
        run("python3 analysis/clustering/00_generate_synthetic_test_data.py", env=env)
    else:
        print("\n" + "=" * 70)
        print("PREPARING REAL DATA")
        print("=" * 70)
        run("python3 analysis/clustering/01_prepare_data.py", env=env)

    # Core pipeline (uses real or synthetic paths based on USE_SYNTHETIC_INPUTS env var)
    print("\n" + "=" * 70)
    print("RUNNING CORE PIPELINE")
    print("=" * 70)
    run("python3 analysis/clustering/02_find_optimal_k.py", env=env)
    run("python3 analysis/clustering/03_tune_optics.py", env=env)
    run("python3 analysis/clustering/04_validate_clusters.py", env=env)
    run("python3 analysis/clustering/05_visualize_clusters.py", env=env)
    run("python3 analysis/clustering/06_heatmaps.py", env=env)

    data_type = "SYNTHETIC" if args.synthetic else "REAL"
    print("\n" + "=" * 70)
    print(f"✅ PIPELINE COMPLETED ({data_type} DATA)")
    print("=" * 70)


if __name__ == "__main__":
    main()
