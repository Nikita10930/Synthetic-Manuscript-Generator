from pathlib import Path
import re
import random


class TextLoader:
    """
    Loads and prepares manuscript source text.

    Supports:
        - Devanagari
        - Modi
        - Sharada

    The original Unicode characters are preserved.
    """

    SCRIPT_RANGES = {
        "devanagari": (0x0900, 0x097F),
        "modi": (0x11600, 0x1173F),
        "sharada": (0x11180, 0x111DF),
    }

    def __init__(self, source_file, seed=42):
        self.source_file = Path(source_file)
        self.seed = seed
        self.random = random.Random(seed)

    def load(self):
        """Read the complete source file as UTF-8 text."""
        if not self.source_file.exists():
            raise FileNotFoundError(
                f"Source file not found: {self.source_file}"
            )

        return self.source_file.read_text(encoding="utf-8")

    def clean_line(self, line):
        """
        Remove unnecessary Markdown formatting while preserving
        the manuscript text and Unicode characters.
        """
        line = line.strip()

        if not line:
            return ""

        # Remove common Markdown formatting characters.
        line = re.sub(r"[*_`>#]", "", line)

        # Normalize repeated spaces.
        line = re.sub(r"[ \t]+", " ", line)

        return line.strip()

    def get_lines(self):
        """
        Return cleaned non-empty source lines.
        """
        text = self.load()

        lines = []

        for line in text.splitlines():
            cleaned = self.clean_line(line)

            if cleaned:
                lines.append(cleaned)

        return lines

    def filter_script(self, text, script):
        """
        Keep characters belonging to the requested Indic script.

        Punctuation, spaces and numbers are also retained because
        they are useful for manuscript layout.
        """
        if script not in self.SCRIPT_RANGES:
            raise ValueError(
                f"Unsupported script: {script}. "
                f"Supported scripts: {list(self.SCRIPT_RANGES.keys())}"
            )

        start, end = self.SCRIPT_RANGES[script]

        result = []

        for char in text:
            code = ord(char)

            # Preserve requested script characters.
            if start <= code <= end:
                result.append(char)

            # Preserve whitespace.
            elif char.isspace():
                result.append(char)

            # Preserve punctuation / numbers / manuscript markers.
            elif not char.isalpha():
                result.append(char)

        return "".join(result)

    def get_script_lines(self, script):
        """
        Return source lines containing the requested script.
        """
        lines = self.get_lines()

        script_lines = []

        for line in lines:
            filtered = self.filter_script(line, script)

            # Require a reasonable amount of actual script content.
            script_char_count = sum(
                self.is_script_character(char, script)
                for char in filtered
            )

            if script_char_count >= 3:
                script_lines.append(filtered)

        return script_lines

    def is_script_character(self, char, script):
        """Check whether a character belongs to the selected script."""
        if script not in self.SCRIPT_RANGES:
            return False

        start, end = self.SCRIPT_RANGES[script]
        code = ord(char)

        return start <= code <= end

    def make_chunks(
        self,
        script,
        min_chars=80,
        max_chars=350
    ):
        """
        Create text chunks suitable for manuscript rendering.

        Chunks are created from source lines rather than randomly
        cutting Unicode characters.
        """
        lines = self.get_script_lines(script)

        if not lines:
            raise ValueError(
                f"No usable {script} text found in {self.source_file}"
            )

        chunks = []
        current = ""

        for line in lines:

            candidate = (
                line if not current
                else current + " " + line
            )

            if len(candidate) <= max_chars:
                current = candidate
                continue

            if current and len(current) >= min_chars:
                chunks.append(current)
                current = line
            else:
                current = candidate

        if current and len(current) >= min_chars:
            chunks.append(current)

        return chunks

    def get_random_chunk(
        self,
        script,
        min_chars=80,
        max_chars=350
    ):
        """Return one reproducible random text chunk."""
        chunks = self.make_chunks(
            script,
            min_chars=min_chars,
            max_chars=max_chars
        )

        return self.random.choice(chunks)

    def get_multiple_chunks(
        self,
        script,
        count,
        min_chars=80,
        max_chars=350
    ):
        """
        Return multiple text chunks.

        If the requested count is larger than the available unique
        chunks, chunks are sampled with replacement.
        """
        chunks = self.make_chunks(
            script,
            min_chars=min_chars,
            max_chars=max_chars
        )

        if not chunks:
            raise ValueError(
                f"No usable text chunks found for {script}"
            )

        if count <= len(chunks):
            return self.random.sample(chunks, count)

        return [
            self.random.choice(chunks)
            for _ in range(count)
        ]


def load_text_from_config(config, script):
    """
    Convenience function for loading a script using config.yaml.
    """
    scripts = config.get("scripts", {})

    if script not in scripts:
        raise ValueError(
            f"Script '{script}' is not present in configuration."
        )

    source_file = scripts[script]["source_file"]

    seed = config.get(
        "randomness",
        {}
    ).get("seed", 42)

    return TextLoader(
        source_file=source_file,
        seed=seed
    )