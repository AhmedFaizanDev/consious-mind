#!/usr/bin/env bash
# Run from a machine with normal internet access. Saves PDFs next to this script.
cd "$(dirname "$0")"
for id in 2008.02275:ethics 2008.09094:scruples 2011.00620:social_chemistry_101 2307.14324:moralchoice 2410.02683:daily_dilemmas 2210.01478:moralexceptqa 2206.04615:bigbench; do
  curl -L -f -o "${id#*:}_${id%%:*}.pdf" "https://arxiv.org/pdf/${id%%:*}" || echo "failed: $id"
done
