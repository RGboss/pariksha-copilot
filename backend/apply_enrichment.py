# -*- coding: utf-8 -*-
"""
Applies enriched chapters (10 through 21) to prep_platform/data/curriculum.json.
Ensures uniform textbook-grade quality, 3 checkpoints each, 5 calibrated quiz questions each,
and updates global curriculum stats.
"""

import os
import sys
import json

BASE_PLATFORM = os.path.dirname(os.path.dirname(__file__))
if BASE_PLATFORM not in sys.path:
    sys.path.insert(0, BASE_PLATFORM)

DATA_PATH = os.path.join(BASE_PLATFORM, 'data', 'curriculum.json')

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    curriculum = json.load(f)

# Import enrichment dictionaries
from backend.enrich_part1 import ENRICHED_CHAPTERS as PART1
from backend.enrich_part2 import ENRICHED_CHAPTERS as PART2
from backend.enrich_part3 import ENRICHED_CHAPTERS as PART3

ALL_ENRICHMENTS = {**PART1, **PART2, **PART3}

applied_count = 0
for stage in curriculum["stages"]:
    for ch in stage["chapters"]:
        ch_id = ch["id"]
        if ch_id in ALL_ENRICHMENTS:
            enrichment = ALL_ENRICHMENTS[ch_id]
            ch["summary"] = enrichment.get("summary", ch["summary"])
            ch["reading_time_mins"] = enrichment.get("reading_time_mins", ch["reading_time_mins"])
            ch["lecture_notes"] = enrichment["lecture_notes"].strip()
            ch["checkpoints"] = enrichment["checkpoints"]
            ch["quiz"] = enrichment["quiz"]
            applied_count += 1
            print(f"Applied enrichment to {ch_id}: length {len(ch['lecture_notes'])} chars, {len(ch['checkpoints'])} checkpoints, {len(ch['quiz'])} quizzes.")

# Recalculate stats
total_chapters = sum(len(s["chapters"]) for s in curriculum["stages"])
total_reading_mins = sum(ch["reading_time_mins"] for s in curriculum["stages"] for ch in s["chapters"])
total_checkpoints = sum(len(ch.get("checkpoints", [])) for s in curriculum["stages"] for ch in s["chapters"])
total_quiz_questions = sum(len(ch.get("quiz", [])) for s in curriculum["stages"] for ch in s["chapters"])

curriculum["stats"] = {
    "total_stages": len(curriculum["stages"]),
    "total_chapters": total_chapters,
    "total_reading_hours": round(total_reading_mins / 60, 1),
    "total_checkpoints": total_checkpoints,
    "total_quiz_questions": total_quiz_questions
}

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(curriculum, f, indent=2, ensure_ascii=False)

print(f"\nSUCCESS: Applied enrichment to {applied_count} chapters!")
print(f"Total Stages: {curriculum['stats']['total_stages']}")
print(f"Total Chapters: {curriculum['stats']['total_chapters']}")
print(f"Total Reading Hours: {curriculum['stats']['total_reading_hours']}")
print(f"Total Checkpoints: {curriculum['stats']['total_checkpoints']}")
print(f"Total Quiz Questions: {curriculum['stats']['total_quiz_questions']}")
