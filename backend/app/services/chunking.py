from __future__ import annotations

import re


class TextChunker:
    def __init__(self, max_words: int = 220, overlap_words: int = 35) -> None:
        self.max_words = max_words
        self.overlap_words = overlap_words

    def chunk(self, text: str) -> list[str]:
        normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
        words = normalized.split()
        if not words:
            return []
        chunks: list[str] = []
        step = max(1, self.max_words - self.overlap_words)
        for start in range(0, len(words), step):
            window = words[start : start + self.max_words]
            if window:
                chunks.append(" ".join(window))
            if start + self.max_words >= len(words):
                break
        return chunks
