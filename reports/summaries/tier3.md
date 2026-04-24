# Tier 3 summary

- 6 of 25 cells are incorrect across ALL 3 models; 9 are correct across all 3.
- Among 36 incorrect cells, 9 contain a ground-truth fragment (e.g. ZIP, PO box number, email domain) - possible matcher strictness.
- Claude Opus 4.7: pass@1=74%, maj@5=76%, pass@5=76% -> oracle gap=+0%
- Gemma 4 26B: pass@1=42%, maj@5=44%, pass@5=48% -> oracle gap=+4%
- GPT-OSS 120B: pass@1=37%, maj@5=36%, pass@5=48% -> oracle gap=+12%
