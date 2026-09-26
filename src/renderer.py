from pathlib import Path
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .effects import ManuscriptEffects
from .layout import ManuscriptLayout


class ManuscriptRenderer:
    """
    Renders Unicode manuscript text onto generated manuscript
    backgrounds.

    Supports:
        - Devanagari
        - Modi
        - Sharada

    The original Unicode transcription is preserved.
    """

    def __init__(self, config, seed=42):
        self.config = config
        self.seed = seed
        self.random = random.Random(seed)

        self.effects = ManuscriptEffects(
            config=config,
            seed=seed
        )

        self.layout_engine = ManuscriptLayout(
            config=config,
            seed=seed
        )

        self.font_cache = {}

    # ---------------------------------------------------------
    # Font loading
    # ---------------------------------------------------------

    def load_font(self, script, size):
        """
        Load the configured font for a script.
        """

        scripts = self.config.get(
            "scripts",
            {}
        )

        if script not in scripts:
            raise ValueError(
                f"Unsupported script: {script}"
            )

        font_path = Path(
            scripts[script]["font"]
        )

        if not font_path.exists():
            raise FileNotFoundError(
                f"Font not found: {font_path}"
            )

        key = (
            str(font_path.resolve()),
            int(size)
        )

        if key not in self.font_cache:

            self.font_cache[key] = ImageFont.truetype(
                str(font_path),
                int(size)
            )

        return self.font_cache[key]

    # ---------------------------------------------------------
    # Font size
    # ---------------------------------------------------------

    def get_font_size(self, script):
        """
        Determine a practical manuscript font size.
        """

        canvas = self.config.get(
            "canvas",
            {}
        )

        width = int(
            canvas.get(
                "width",
                1600
            )
        )

        # Keep the first implementation readable.
        if width >= 1800:
            return 44

        if width >= 1500:
            return 40

        if width >= 1200:
            return 36

        return 32

    # ---------------------------------------------------------
    # Text measurement
    # ---------------------------------------------------------

    def measure_text(
        self,
        text,
        font
    ):
        """
        Measure rendered text using the actual font.
        """

        if not text:
            return 0, 0

        bbox = font.getbbox(
            text
        )

        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        return (
            int(width),
            int(height)
        )

    # ---------------------------------------------------------
    # Renderer measurement adapter
    # ---------------------------------------------------------

    def create_measure_function(
        self,
        font
    ):
        """
        Return a function compatible with ManuscriptLayout.
        """

        def measure(text):
            return self.measure_text(
                text,
                font
            )

        return measure

    # ---------------------------------------------------------
    # Handwriting transform
    # ---------------------------------------------------------

    def apply_slant(
        self,
        text_layer,
        angle
    ):
        """
        Apply a very small affine slant.

        The angle is intentionally kept subtle because the
        manuscript should still remain readable.
        """

        if abs(angle) < 0.01:
            return text_layer

        return text_layer.transform(
            text_layer.size,
            Image.AFFINE,
            (
                1,
                np.tan(
                    np.radians(angle)
                ),
                0,
                0,
                1,
                0
            ),
            resample=Image.Resampling.BICUBIC
        )

    # ---------------------------------------------------------
    # Draw one line
    # ---------------------------------------------------------

    def render_line(
        self,
        canvas,
        line,
        font,
        ink_color,
        ink_opacity,
        handwriting_parameters
    ):
        """
        Render one manuscript line.
        """

        text = line.text

        if not text:
            return

        width, height = self.measure_text(
            text,
            font
        )

        padding = 20

        layer_width = max(
            50,
            width + padding * 2
        )

        layer_height = max(
            50,
            height + padding * 2
        )

        text_layer = Image.new(
            "RGBA",
            (
                layer_width,
                layer_height
            ),
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(
            text_layer
        )

        draw.text(
            (
                padding,
                padding
            ),
            text,
            font=font,
            fill=(
                ink_color[0],
                ink_color[1],
                ink_color[2],
                ink_opacity
            )
        )

        # Slight handwriting slant.
        slant = handwriting_parameters.get(
            "slant",
            0.0
        )

        text_layer = self.apply_slant(
            text_layer,
            slant
        )

        # Small natural blur.
        if self.random.random() < 0.35:

            text_layer = text_layer.filter(
                ImageFilter.GaussianBlur(
                    radius=self.random.uniform(
                        0.05,
                        0.30
                    )
                )
            )

        # Apply ink effects.
        text_layer = self.effects.process_ink(
            text_layer
        )

        paste_x = int(
            line.x - padding
        )

        paste_y = int(
            line.y - padding
        )

        # Strict canvas protection.
        paste_x = max(
            0,
            paste_x
        )

        paste_y = max(
            0,
            paste_y
        )

        canvas.alpha_composite(
            text_layer,
            (
                paste_x,
                paste_y
            )
        )

    # ---------------------------------------------------------
    # Highlight
    # ---------------------------------------------------------

    def render_highlight(
        self,
        canvas,
        line
    ):
        """
        Add highlight behind a selected line.
        """

        bbox = (
            line.x - 5,
            line.y - 3,
            line.x + line.width + 5,
            line.y + line.height + 4
        )

        return self.effects.add_highlight(
            canvas,
            bbox
        )

    # ---------------------------------------------------------
    # Render manuscript
    # ---------------------------------------------------------

    def render(
        self,
        background,
        text,
        script
    ):
        """
        Render text onto an existing manuscript background.

        Returns:
            {
                "image": PIL.Image,
                "lines": list,
                "transcription": original text
            }
        """

        if script not in self.config.get(
            "scripts",
            {}
        ):
            raise ValueError(
                f"Unsupported script: {script}"
            )

        canvas = background.convert(
            "RGBA"
        ).copy()

        font_size = self.get_font_size(
            script
        )

        font = self.load_font(
            script,
            font_size
        )

        measure_function = (
            self.create_measure_function(
                font
            )
        )

        width, height = canvas.size

        blocks = self.layout_engine.create_layout(
            text=text,
            canvas_width=width,
            canvas_height=height,
            measure_text=measure_function
        )

        handwriting_parameters = (
            self.effects.get_handwriting_parameters()
        )

        rendered_lines = []

        for block in blocks:

            for line in block.lines:

                # Highlight must go behind text.
                if line.is_highlighted:

                    canvas = (
                        self.render_highlight(
                            canvas,
                            line
                        ).convert("RGBA")
                    )

                ink_color = (
                    self.effects.get_ink_color()
                )

                ink_opacity = (
                    self.effects.get_ink_opacity()
                )

                self.render_line(
                    canvas=canvas,
                    line=line,
                    font=font,
                    ink_color=ink_color,
                    ink_opacity=ink_opacity,
                    handwriting_parameters=(
                        handwriting_parameters
                    )
                )

                rendered_lines.append(
                    {
                        "text": line.text,
                        "x": line.x,
                        "y": line.y,
                        "width": line.width,
                        "height": line.height,
                        "block_id": line.block_id,
                        "is_margin_text": (
                            line.is_margin_text
                        ),
                        "is_highlighted": (
                            line.is_highlighted
                        )
                    }
                )

        return {
            "image": canvas.convert("RGB"),
            "lines": rendered_lines,
            "transcription": text,
            "script": script
        }


# -------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------

def render_manuscript(
    config,
    background,
    text,
    script,
    seed=42
):
    """
    Convenience wrapper for the main generation pipeline.
    """

    renderer = ManuscriptRenderer(
        config=config,
        seed=seed
    )

    return renderer.render(
        background=background,
        text=text,
        script=script
    )