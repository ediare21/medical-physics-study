import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SYLLABUS = ROOT / "syllabus-checklist.md"

TOTAL_WEEKS = 104

def count_completed_weeks(syllabus_path: Path) -> int:
    if not syllabus_path.exists():
        return 0
    text = syllabus_path.read_text(encoding="utf-8", errors="ignore")
    # Count checklist lines like "- [x] Week N" (case-insensitive)
    done = len(re.findall(r"^- \[[xX]\] \s*Week\s+\d+", text, flags=re.MULTILINE))
    return done

def count_completed_artifacts_from_readme(readme_path: Path) -> tuple[int, int]:
    if not readme_path.exists():
        return 0, 0
    text = readme_path.read_text(encoding="utf-8", errors="ignore")
    # Only count inside markers to avoid false positives
    m = re.search(r"<!--ARTIFACTS_START-->(.*?)<!--ARTIFACTS_END-->", text, flags=re.S)
    if not m:
        return 0, 0
    section = m.group(1)
    total = len(re.findall(r"^- \[[ \]xX]\] ", section, flags=re.MULTILINE))
    done = len(re.findall(r"^- \[[xX]\] ", section, flags=re.MULTILINE))
    return done, total

def render_badges(weeks_done: int, total_weeks: int, arts_done: int, arts_total: int) -> str:
    # Avoid division by zero for artifacts
    arts_total = arts_total if arts_total else 8  # default planned artifacts
    weeks_pct = int(round(100 * weeks_done / max(1, total_weeks)))
    arts_pct = int(round(100 * arts_done / max(1, arts_total)))

    weeks_badge = f"https://img.shields.io/badge/Weeks_Completed-{weeks_done}%2F{total_weeks}-blue"
    arts_badge = f"https://img.shields.io/badge/Artifacts_Completed-{arts_done}%2F{arts_total}-informational"
    progress_badge = f"https://img.shields.io/badge/Overall_Progress-{weeks_pct}%25-brightgreen"

    return (
        f"![Weeks Completed]({weeks_badge}) "
        f"![Artifacts Completed]({arts_badge}) "
        f"![Overall Progress]({progress_badge})"
    )

def update_readme_badge_block(readme_path: Path, badge_md: str) -> bool:
    text = readme_path.read_text(encoding="utf-8", errors="ignore")
    if "<!--PROGRESS_BADGES_START-->" not in text or "<!--PROGRESS_BADGES_END-->" not in text:
        # Insert a block near the top if missing
        insert_block = "\n\n<!--PROGRESS_BADGES_START-->\n" + badge_md + "\n<!--PROGRESS_BADGES_END-->\n\n"
        # place after the first heading if possible
        text = re.sub(r"(^# .*$)", r"\1" + insert_block, text, count=1, flags=re.M) or (insert_block + text)
        readme_path.write_text(text, encoding="utf-8")
        return True
    # Replace content inside the markers
    new_text = re.sub(
        r"<!--PROGRESS_BADGES_START-->.*?<!--PROGRESS_BADGES_END-->",
        f"<!--PROGRESS_BADGES_START-->\n{badge_md}\n<!--PROGRESS_BADGES_END-->",
        text,
        flags=re.S
    )
    if new_text != text:
        readme_path.write_text(new_text, encoding="utf-8")
        return True
    return False

def main():
    weeks_done = count_completed_weeks(SYLLABUS)
    arts_done, arts_total = count_completed_artifacts_from_readme(README)
    badge_md = render_badges(weeks_done, TOTAL_WEEKS, arts_done, arts_total)
    changed = update_readme_badge_block(README, badge_md)
    print(f"Weeks: {weeks_done}/{TOTAL_WEEKS}, Artifacts: {arts_done}/{arts_total}. Updated README: {changed}")

if __name__ == "__main__":
    main()
