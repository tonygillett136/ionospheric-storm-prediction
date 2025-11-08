"""
Science Guide API endpoints
Serves educational content from SCIENCE_GUIDE.md
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import re

router = APIRouter(prefix="/science-guide", tags=["science-guide"])

# Path to the science guide markdown file
SCIENCE_GUIDE_PATH = Path(__file__).parent.parent.parent.parent / "docs" / "SCIENCE_GUIDE.md"

def parse_science_guide():
    """Parse SCIENCE_GUIDE.md into chapters"""
    try:
        with open(SCIENCE_GUIDE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by chapter headings
        # Chapters are marked with "## Chapter X: Title"
        chapter_pattern = r'## Chapter (\d+):'
        chapters = {}

        # Find all chapter start positions
        matches = list(re.finditer(chapter_pattern, content))

        for i, match in enumerate(matches):
            chapter_num = int(match.group(1))
            start_pos = match.start()

            # End position is either the next chapter or end of file
            if i < len(matches) - 1:
                end_pos = matches[i + 1].start()
            else:
                # Look for the glossary chapter
                glossary_match = re.search(r'## Chapter 15: Glossary', content)
                if glossary_match and chapter_num < 15:
                    end_pos = glossary_match.start()
                else:
                    end_pos = len(content)

            chapter_content = content[start_pos:end_pos].strip()
            chapters[chapter_num - 1] = chapter_content  # 0-indexed for frontend

        return chapters
    except Exception as e:
        print(f"Error parsing science guide: {e}")
        return {}

# Cache the parsed chapters
_chapters_cache = None

def get_chapters():
    """Get cached chapters or parse if not cached"""
    global _chapters_cache
    if _chapters_cache is None:
        _chapters_cache = parse_science_guide()
    return _chapters_cache

@router.get("/chapters")
async def get_all_chapters():
    """Get all chapter content"""
    chapters = get_chapters()
    return {
        "chapters": chapters,
        "count": len(chapters)
    }

@router.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: int):
    """Get specific chapter content"""
    chapters = get_chapters()

    if chapter_id not in chapters:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")

    return {
        "chapter_id": chapter_id,
        "content": chapters[chapter_id]
    }

@router.post("/refresh")
async def refresh_chapters():
    """Refresh the chapter cache (useful during development)"""
    global _chapters_cache
    _chapters_cache = None
    chapters = get_chapters()
    return {
        "message": "Chapters refreshed",
        "count": len(chapters)
    }
