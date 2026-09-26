from dataclasses import dataclass
from typing import List
import random


# =========================================================
# DATA STRUCTURES
# =========================================================

@dataclass
class TextLine:
    text: str
    x: int
    y: int
    width: int
    height: int
    block_id: int = 0
    is_margin_text: bool = False
    is_highlighted: bool = False


@dataclass
class TextBlock:
    lines: List[TextLine]
    x: int
    y: int
    width: int
    height: int
    block_id: int


# =========================================================
# MANUSCRIPT LAYOUT
# =========================================================

class ManuscriptLayout:
    """
    Creates historically-inspired manuscript layouts.

    Features:
        - safe manuscript margins
        - multiple text blocks
        - controlled line wrapping
        - natural baseline variation
        - horizontal jitter
        - vertical jitter
        - dedicated marginal-note area
        - highlighted passages
        - overflow prevention
        - Unicode-safe text handling
    """

    def __init__(self, config, seed=42):
        self.config = config
        self.seed = seed
        self.random = random.Random(seed)

    # =====================================================
    # PUBLIC API
    # =====================================================

    def create_layout(
        self,
        text,
        canvas_width,
        canvas_height,
        measure_text
    ):
        """
        Create the complete manuscript layout.
        """

        layout_config = self.config.get(
            "layout",
            {}
        )

        canvas_config = self.config.get(
            "canvas",
            {}
        )

        margin_config = canvas_config.get(
            "margin",
            {}
        )

        # -------------------------------------------------
        # Canvas margins
        # -------------------------------------------------

        margin_left = int(
            margin_config.get("left", 100)
        )

        margin_right = int(
            margin_config.get("right", 100)
        )

        margin_top = int(
            margin_config.get("top", 90)
        )

        margin_bottom = int(
            margin_config.get("bottom", 90)
        )

        # -------------------------------------------------
        # Dedicated marginal-note lane
        # -------------------------------------------------

        marginal_probability = float(
            layout_config.get(
                "marginal_note_probability",
                0.20
            )
        )

        side_text_probability = float(
            layout_config.get(
                "side_text_probability",
                0.25
            )
        )

        use_margin_lane = (
            self.random.random()
            < max(
                marginal_probability,
                side_text_probability
            )
        )

        # Reserve a dedicated lane on the right.
        # This prevents marginal text from entering
        # the main manuscript text area.
        margin_lane_width = 0

        if use_margin_lane:
            margin_lane_width = min(
                230,
                max(
                    160,
                    int(canvas_width * 0.13)
                )
            )

        main_left = margin_left

        main_right = (
            canvas_width
            - margin_right
            - margin_lane_width
        )

        main_width = (
            main_right
            - main_left
        )

        # Safety fallback
        if main_width < 500:
            margin_lane_width = 0

            main_right = (
                canvas_width
                - margin_right
            )

            main_width = (
                main_right
                - main_left
            )

        available_height = (
            canvas_height
            - margin_top
            - margin_bottom
        )

        # -------------------------------------------------
        # Number of blocks
        # -------------------------------------------------

        min_blocks = int(
            layout_config.get(
                "min_blocks",
                1
            )
        )

        max_blocks = int(
            layout_config.get(
                "max_blocks",
                3
            )
        )

        min_blocks = max(
            1,
            min_blocks
        )

        max_blocks = max(
            min_blocks,
            max_blocks
        )

        block_count = self.random.randint(
            min_blocks,
            max_blocks
        )

        # Do not create too many blocks for a short text.
        word_count = len(
            text.split()
        )

        if word_count < 80:
            block_count = 1
        elif word_count < 180:
            block_count = min(
                block_count,
                2
            )

        block_count = min(
            block_count,
            3
        )

        # -------------------------------------------------
        # Split source text
        # -------------------------------------------------

        text_blocks = self._split_into_blocks(
            text,
            block_count
        )

        if not text_blocks:
            return []

        # -------------------------------------------------
        # Main text widths
        # -------------------------------------------------

        block_widths = (
            self._calculate_block_widths(
                main_width,
                len(text_blocks)
            )
        )

        blocks = []

        current_y = margin_top

        # -------------------------------------------------
        # Generate main blocks
        # -------------------------------------------------

        for block_id, block_text in enumerate(
            text_blocks
        ):

            block_width = block_widths[
                block_id
            ]

            lines = self._wrap_text(
                text=block_text,
                max_width=block_width,
                measure_text=measure_text
            )

            if not lines:
                continue

            block_lines = []

            line_spacing = int(
                layout_config.get(
                    "line_spacing",
                    18
                )
            )

            horizontal_jitter = int(
                layout_config.get(
                    "horizontal_jitter",
                    3
                )
            )

            vertical_jitter = int(
                layout_config.get(
                    "vertical_jitter",
                    3
                )
            )

            # Keep a reasonable gap between blocks.
            block_gap = self.random.randint(
                35,
                65
            )

            line_y = current_y

            for line_index, line_text in enumerate(
                lines
            ):

                line_width, line_height = (
                    measure_text(line_text)
                )

                # -------------------------------------------------
                # Final horizontal protection
                # -------------------------------------------------

                if line_width > block_width:

                    line_text = self._shrink_line(
                        line_text,
                        block_width,
                        measure_text
                    )

                    line_width, line_height = (
                        measure_text(line_text)
                    )

                # -------------------------------------------------
                # Natural handwriting irregularity
                # -------------------------------------------------

                jitter_x = self.random.randint(
                    -horizontal_jitter,
                    horizontal_jitter
                )

                jitter_y = self.random.randint(
                    -vertical_jitter,
                    vertical_jitter
                )

                # Slightly vary every few lines.
                if line_index % 4 == 0:
                    jitter_x += self.random.choice(
                        [-2, -1, 0, 1, 2]
                    )

                # -------------------------------------------------
                # Main text X position
                # -------------------------------------------------

                line_x = (
                    main_left
                    + jitter_x
                )

                # -------------------------------------------------
                # Strict horizontal boundary
                # -------------------------------------------------

                max_x = (
                    main_right
                    - line_width
                )

                line_x = max(
                    main_left,
                    min(
                        line_x,
                        max_x
                    )
                )

                # -------------------------------------------------
                # Y position
                # -------------------------------------------------

                line_y_with_jitter = (
                    line_y
                    + jitter_y
                )

                line_y_with_jitter = max(
                    margin_top,
                    line_y_with_jitter
                )

                # -------------------------------------------------
                # Vertical overflow protection
                # -------------------------------------------------

                if (
                    line_y_with_jitter
                    + line_height
                    > canvas_height
                    - margin_bottom
                ):
                    break

                block_lines.append(
                    TextLine(
                        text=line_text,
                        x=int(line_x),
                        y=int(
                            line_y_with_jitter
                        ),
                        width=int(
                            line_width
                        ),
                        height=int(
                            line_height
                        ),
                        block_id=block_id
                    )
                )

                # -------------------------------------------------
                # Controlled line spacing
                # -------------------------------------------------

                natural_spacing = (
                    line_height
                    + line_spacing
                )

                # Tiny natural variation
                spacing_variation = (
                    self.random.choice(
                        [-1, 0, 0, 1]
                    )
                )

                line_y += (
                    natural_spacing
                    + spacing_variation
                )

            # -----------------------------------------------------
            # Build TextBlock
            # -----------------------------------------------------

            if block_lines:

                block_x = min(
                    line.x
                    for line in block_lines
                )

                block_y = min(
                    line.y
                    for line in block_lines
                )

                block_right = max(
                    line.x + line.width
                    for line in block_lines
                )

                block_bottom = max(
                    line.y + line.height
                    for line in block_lines
                )

                block = TextBlock(
                    lines=block_lines,
                    x=block_x,
                    y=block_y,
                    width=(
                        block_right
                        - block_x
                    ),
                    height=(
                        block_bottom
                        - block_y
                    ),
                    block_id=block_id
                )

                blocks.append(block)

                # -------------------------------------------------
                # Next block starts BELOW current block
                # -------------------------------------------------

                current_y = (
                    block_bottom
                    + block_gap
                )

                # Prevent next block from being pushed
                # outside the manuscript.
                if current_y >= (
                    canvas_height
                    - margin_bottom
                ):
                    break

        # =========================================================
        # MARGINAL ANNOTATION
        # =========================================================

        if (
            use_margin_lane
            and self._probability(
                "marginal_note_probability"
            )
        ):

            self._add_marginal_text(
                blocks=blocks,
                source_text=text,
                canvas_width=canvas_width,
                canvas_height=canvas_height,
                measure_text=measure_text,
                margin_left=margin_left,
                margin_right=margin_right,
                margin_top=margin_top,
                margin_bottom=margin_bottom,
                main_right=main_right,
                margin_lane_width=margin_lane_width
            )

        # =========================================================
        # HIGHLIGHTED PASSAGE
        # =========================================================

        if self._probability(
            "highlighted_text_probability"
        ):

            self._mark_highlighted_line(
                blocks
            )

        return blocks

    # =========================================================
    # TEXT SPLITTING
    # =========================================================

    def _split_into_blocks(
        self,
        text,
        block_count
    ):
        """
        Split manuscript text into balanced blocks.
        """

        words = text.split()

        if not words:
            return []

        block_count = max(
            1,
            min(
                block_count,
                len(words)
            )
        )

        total_words = len(words)

        base_size = (
            total_words
            // block_count
        )

        remainder = (
            total_words
            % block_count
        )

        blocks = []

        start = 0

        for index in range(
            block_count
        ):

            size = base_size

            if index < remainder:
                size += 1

            end = start + size

            block_text = " ".join(
                words[start:end]
            )

            if block_text.strip():
                blocks.append(
                    block_text
                )

            start = end

        return blocks

    # =========================================================
    # WIDTH CALCULATION
    # =========================================================

    def _calculate_block_widths(
        self,
        available_width,
        block_count
    ):
        """
        Calculate safe widths for manuscript blocks.

        Blocks are primarily vertical sections rather than
        narrow columns. This produces a much more natural
        folio layout and avoids the narrow-left-column
        appearance seen in the previous output.
        """

        if block_count <= 1:
            return [
                available_width
            ]

        # Keep all blocks comfortably wide.
        # Use almost the complete manuscript width.
        widths = []

        for _ in range(
            block_count
        ):

            variation = self.random.uniform(
                0.96,
                1.00
            )

            widths.append(
                max(
                    400,
                    int(
                        available_width
                        * variation
                    )
                )
            )

        # All blocks use the same safe width.
        # They are stacked vertically.
        safe_width = min(
            widths
        )

        return [
            safe_width
            for _ in range(
                block_count
            )
        ]

    # =========================================================
    # TEXT WRAPPING
    # =========================================================

    def _wrap_text(
        self,
        text,
        max_width,
        measure_text
    ):
        """
        Wrap text according to actual rendered width.
        """

        words = text.split()

        if not words:
            return []

        lines = []

        current = ""

        for word in words:

            candidate = (
                word
                if not current
                else current + " " + word
            )

            width, _ = measure_text(
                candidate
            )

            if width <= max_width:

                current = candidate

                continue

            # Current line is complete.
            if current:

                lines.append(
                    current
                )

            # Check individual word.
            word_width, _ = (
                measure_text(word)
            )

            if word_width <= max_width:

                current = word

            else:

                pieces = (
                    self._break_long_word(
                        word,
                        max_width,
                        measure_text
                    )
                )

                if pieces:

                    lines.extend(
                        pieces[:-1]
                    )

                    current = pieces[-1]

                else:

                    current = ""

        if current:
            lines.append(
                current
            )

        return lines

    # =========================================================
    # BREAK LONG WORD
    # =========================================================

    def _break_long_word(
        self,
        word,
        max_width,
        measure_text
    ):
        """
        Break an unusually long token safely.

        Unicode code points are preserved.
        """

        pieces = []

        current = ""

        for char in word:

            candidate = (
                current + char
            )

            width, _ = measure_text(
                candidate
            )

            if width <= max_width:

                current = candidate

            else:

                if current:

                    pieces.append(
                        current
                    )

                current = char

        if current:

            pieces.append(
                current
            )

        return pieces

    # =========================================================
    # SHRINK LINE
    # =========================================================

    def _shrink_line(
        self,
        text,
        max_width,
        measure_text
    ):
        """
        Final horizontal overflow protection.
        """

        if (
            measure_text(text)[0]
            <= max_width
        ):
            return text

        chars = []

        for char in text:

            candidate = (
                "".join(chars)
                + char
            )

            if (
                measure_text(
                    candidate
                )[0]
                <= max_width
            ):

                chars.append(
                    char
                )

            else:

                break

        return "".join(chars)

    # =========================================================
    # MARGINAL ANNOTATION
    # =========================================================

    def _add_marginal_text(
        self,
        blocks,
        source_text,
        canvas_width,
        canvas_height,
        measure_text,
        margin_left,
        margin_right,
        margin_top,
        margin_bottom,
        main_right,
        margin_lane_width
    ):
        """
        Add marginal annotation ONLY inside the dedicated
        right-side lane.

        Important:
            It never falls back to the main text area.
        """

        if not blocks:
            return

        words = source_text.split()

        if not words:
            return

        # -----------------------------------------------------
        # Select short annotation
        # -----------------------------------------------------

        count = min(
            len(words),
            self.random.randint(
                3,
                8
            )
        )

        # Use text from the manuscript itself.
        note_text = " ".join(
            words[:count]
        )

        # -----------------------------------------------------
        # Dedicated lane
        # -----------------------------------------------------

        lane_left = (
            main_right
            + 20
        )

        lane_right = (
            canvas_width
            - margin_right
        )

        lane_width = (
            lane_right
            - lane_left
        )

        if lane_width < 80:
            return

        # -----------------------------------------------------
        # Wrap marginal text
        # -----------------------------------------------------

        note_lines = self._wrap_text(
            note_text,
            lane_width,
            measure_text
        )

        if not note_lines:
            return

        # Keep only a few lines.
        note_lines = note_lines[:4]

        line_objects = []

        current_y = self.random.randint(
            margin_top + 20,
            max(
                margin_top + 20,
                canvas_height
                - margin_bottom
                - 150
            )
        )

        for note_line in note_lines:

            note_width, note_height = (
                measure_text(
                    note_line
                )
            )

            # Absolute protection.
            if (
                note_width
                > lane_width
            ):

                note_line = (
                    self._shrink_line(
                        note_line,
                        lane_width,
                        measure_text
                    )
                )

                note_width, note_height = (
                    measure_text(
                        note_line
                    )
                )

            x = (
                lane_left
                + self.random.randint(
                    -3,
                    3
                )
            )

            # Never enter main text.
            x = max(
                lane_left,
                min(
                    x,
                    lane_right
                    - note_width
                )
            )

            y = (
                current_y
                + self.random.randint(
                    -2,
                    2
                )
            )

            # Vertical safety.
            if (
                y + note_height
                > canvas_height
                - margin_bottom
            ):
                break

            line_objects.append(
                TextLine(
                    text=note_line,
                    x=int(x),
                    y=int(y),
                    width=int(note_width),
                    height=int(note_height),
                    block_id=-1,
                    is_margin_text=True
                )
            )

            current_y += (
                note_height
                + 12
            )

        if not line_objects:
            return

        block_x = min(
            line.x
            for line in line_objects
        )

        block_y = min(
            line.y
            for line in line_objects
        )

        block_right = max(
            line.x + line.width
            for line in line_objects
        )

        block_bottom = max(
            line.y + line.height
            for line in line_objects
        )

        blocks.append(
            TextBlock(
                lines=line_objects,
                x=int(block_x),
                y=int(block_y),
                width=int(
                    block_right
                    - block_x
                ),
                height=int(
                    block_bottom
                    - block_y
                ),
                block_id=-1
            )
        )

    # =========================================================
    # HIGHLIGHT
    # =========================================================

    def _mark_highlighted_line(
        self,
        blocks
    ):
        """
        Mark one existing manuscript line as highlighted.
        """

        normal_blocks = [
            block
            for block in blocks
            if block.block_id >= 0
        ]

        if not normal_blocks:
            return

        block = self.random.choice(
            normal_blocks
        )

        if not block.lines:
            return

        line = self.random.choice(
            block.lines
        )

        line.is_highlighted = True

    # =========================================================
    # PROBABILITY
    # =========================================================

    def _probability(
        self,
        key
    ):
        """
        Read probability from layout configuration.
        """

        value = float(
            self.config.get(
                "layout",
                {}
            ).get(
                key,
                0.0
            )
        )

        value = max(
            0.0,
            min(
                1.0,
                value
            )
        )

        return (
            self.random.random()
            < value
        )


# =========================================================
# CONVENIENCE FUNCTION
# =========================================================

def create_layout(
    config,
    text,
    canvas_width,
    canvas_height,
    measure_text,
    seed=42
):
    """
    Convenience function used by the main renderer.
    """

    layout = ManuscriptLayout(
        config=config,
        seed=seed
    )

    return layout.create_layout(
        text=text,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        measure_text=measure_text
    )