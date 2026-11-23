#!/usr/bin/env bash
# Runs every lab in order and saves the transcript to out/run_all.log
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
mkdir -p out
{
  for lab in lab1_document lab2_bias lab3_audit_trail lab4_hitl lab5_ci_gate; do
    python "labs/${lab}.py"
  done
} 2>&1 | tee out/run_all.log
