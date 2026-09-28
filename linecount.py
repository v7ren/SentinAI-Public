from pathlib import Path
from collections import defaultdict

root = Path(r"C:\Users\Ren-pc\Desktop\main\sentinai-v4\backend")
dir_totals = defaultdict(int)
grand_total = 0

for file in root.rglob("*.py"):
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        line_count = sum(1 for _ in f)

    rel_file = file.relative_to(root)
    rel_dir = rel_file.parent

    print(f"FILE  {rel_file}: {line_count}")

    dir_totals[rel_dir] += line_count
    grand_total += line_count

print("\nDirectory totals:")
for directory in sorted(dir_totals):
    print(f"DIR   {directory}: {dir_totals[directory]}")

print(f"\nGRAND TOTAL: {grand_total}")
