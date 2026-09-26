from __future__ import annotations

import random
from typing import Tuple

import numpy as np
from PIL import Image, ImageFilter, ImageDraw


class ManuscriptEffects:
    """
    Manuscript ink and handwriting effects.

    Provides:
    - Natural ink colors
    - Ink opacity
    - Ink variation
    - Ink bleeding
    - Ink smudging
    - Faded strokes
    - Highlighting
    - Handwriting parameters
    """

    def __init__(self, config: dict, seed: int = 42):
        self.config = config
        self.seed = seed

        # Dedicated random generator for deterministic output.
        self.random = random.Random(seed)

        self.ink_config = config.get("ink", {})
        self.handwriting_config = config.get(
            "handwriting",
            {}
        )

    # =========================================================
    # RANDOM HELPERS
    # =========================================================

    def _random_float(
        self,
        minimum: float,
        maximum: float
    ) -> float:

        return self.random.uniform(
            minimum,
            maximum
        )

    def _random_int(
        self,
        minimum: int,
        maximum: int
    ) -> int:

        return self.random.randint(
            minimum,
            maximum
        )

    # =========================================================
    # INK COLOR
    # =========================================================

    def get_ink_color(
        self
    ) -> Tuple[int, int, int]:

        colors = self.ink_config.get(
            "colors",
            [
                [35, 25, 18],
                [48, 35, 25],
                [62, 45, 30],
                [75, 55, 38],
            ]
        )

        if not colors:
            return (45, 32, 22)

        color = self.random.choice(colors)

        variation_strength = float(
            self.ink_config.get(
                "variation_strength",
                0.18
            )
        )

        result = []

        for channel in color:

            variation = self.random.uniform(
                -variation_strength,
                variation_strength
            )

            value = int(
                channel * (1.0 + variation)
            )

            value = max(
                0,
                min(255, value)
            )

            result.append(value)

        return tuple(result)

    # =========================================================
    # INK OPACITY
    # =========================================================

    def get_ink_opacity(self) -> int:

        opacity_config = self.ink_config.get(
            "opacity",
            {}
        )

        minimum = float(
            opacity_config.get(
                "min",
                0.78
            )
        )

        maximum = float(
            opacity_config.get(
                "max",
                1.0
            )
        )

        opacity = self.random.uniform(
            minimum,
            maximum
        )

        opacity = max(
            0.0,
            min(1.0, opacity)
        )

        return int(
            opacity * 255
        )

    # =========================================================
    # HANDWRITING PARAMETERS
    # =========================================================

    def get_handwriting_parameters(
        self
    ) -> dict:

        slant_config = self.handwriting_config.get(
            "slant",
            {}
        )

        waviness_config = self.handwriting_config.get(
            "waviness",
            {}
        )

        spacing_config = self.handwriting_config.get(
            "character_spacing",
            {}
        )

        baseline_config = self.handwriting_config.get(
            "baseline_variation",
            {}
        )

        stroke_config = self.handwriting_config.get(
            "stroke_variation",
            {}
        )

        parameters = {

            "slant": self.random.uniform(
                float(
                    slant_config.get(
                        "min",
                        -3.0
                    )
                ),
                float(
                    slant_config.get(
                        "max",
                        3.0
                    )
                )
            ),

            "waviness": {

                "enabled": waviness_config.get(
                    "enabled",
                    True
                ),

                "amplitude": float(
                    waviness_config.get(
                        "amplitude",
                        2.5
                    )
                ),

                "frequency": float(
                    waviness_config.get(
                        "frequency",
                        0.035
                    )
                )
            },

            "character_spacing": self.random.uniform(
                float(
                    spacing_config.get(
                        "min",
                        -1
                    )
                ),
                float(
                    spacing_config.get(
                        "max",
                        3
                    )
                )
            ),

            "baseline_variation": self.random.uniform(
                float(
                    baseline_config.get(
                        "min",
                        -2
                    )
                ),
                float(
                    baseline_config.get(
                        "max",
                        2
                    )
                )
            ),

            "stroke_variation": self.random.uniform(
                float(
                    stroke_config.get(
                        "min",
                        0.85
                    )
                ),
                float(
                    stroke_config.get(
                        "max",
                        1.15
                    )
                )
            )
        }

        return parameters

    # =========================================================
    # BASELINE OFFSET
    # =========================================================

    def get_baseline_offset(self) -> int:

        baseline_config = self.handwriting_config.get(
            "baseline_variation",
            {}
        )

        minimum = int(
            baseline_config.get(
                "min",
                -2
            )
        )

        maximum = int(
            baseline_config.get(
                "max",
                2
            )
        )

        return self.random.randint(
            minimum,
            maximum
        )

    # =========================================================
    # CHARACTER SPACING
    # =========================================================

    def get_character_spacing(self) -> int:

        spacing_config = self.handwriting_config.get(
            "character_spacing",
            {}
        )

        minimum = int(
            spacing_config.get(
                "min",
                -1
            )
        )

        maximum = int(
            spacing_config.get(
                "max",
                3
            )
        )

        return self.random.randint(
            minimum,
            maximum
        )

    # =========================================================
    # WAVINESS
    # =========================================================

    def get_waviness(
        self,
        x: float
    ) -> float:

        waviness_config = self.handwriting_config.get(
            "waviness",
            {}
        )

        if not waviness_config.get(
            "enabled",
            True
        ):
            return 0.0

        amplitude = float(
            waviness_config.get(
                "amplitude",
                2.5
            )
        )

        frequency = float(
            waviness_config.get(
                "frequency",
                0.035
            )
        )

        return amplitude * np.sin(
            x * frequency
        )

    # =========================================================
    # INK VARIATION
    # =========================================================

    def apply_ink_variation(
        self,
        image: Image.Image,
        strength: float | None = None
    ) -> Image.Image:

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if strength is None:
            strength = float(
                self.ink_config.get(
                    "variation_strength",
                    0.18
                )
            )

        # Writable NumPy copy.
        array = np.array(
            image,
            copy=True
        ).astype(
            np.float32
        )

        alpha = array[:, :, 3]

        rng = np.random.default_rng(
            self.random.randint(
                0,
                2_000_000_000
            )
        )

        noise = rng.normal(
            loc=0.0,
            scale=255.0 * strength * 0.12,
            size=alpha.shape
        )

        alpha = np.clip(
            alpha + noise,
            0,
            255
        )

        array[:, :, 3] = alpha

        return Image.fromarray(
            array.astype(np.uint8),
            mode="RGBA"
        )

    # =========================================================
    # OPACITY PROCESSING
    # =========================================================

    def apply_opacity(
        self,
        image: Image.Image,
        minimum: float | None = None,
        maximum: float | None = None
    ) -> Image.Image:

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        opacity_config = self.ink_config.get(
            "opacity",
            {}
        )

        if minimum is None:
            minimum = float(
                opacity_config.get(
                    "min",
                    0.78
                )
            )

        if maximum is None:
            maximum = float(
                opacity_config.get(
                    "max",
                    1.0
                )
            )

        factor = self.random.uniform(
            minimum,
            maximum
        )

        array = np.array(
            image,
            copy=True
        ).astype(
            np.float32
        )

        array[:, :, 3] *= factor

        array[:, :, 3] = np.clip(
            array[:, :, 3],
            0,
            255
        )

        return Image.fromarray(
            array.astype(np.uint8),
            mode="RGBA"
        )

    # =========================================================
    # SMUDGE
    # =========================================================

    def apply_smudge(
        self,
        image: Image.Image,
        strength: float | None = None
    ) -> Image.Image:

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if strength is None:
            strength = float(
                self.ink_config.get(
                    "smudge_strength",
                    0.35
                )
            )

        if strength <= 0:
            return image

        radius = max(
            0.1,
            strength * 1.8
        )

        blurred = image.filter(
            ImageFilter.GaussianBlur(
                radius=radius
            )
        )

        blend_factor = min(
            0.35,
            strength * 0.35
        )

        return Image.blend(
            image,
            blurred,
            blend_factor
        )

    # =========================================================
    # BLEED
    # =========================================================

    def apply_bleed(
        self,
        image: Image.Image,
        strength: float | None = None
    ) -> Image.Image:

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if strength is None:
            strength = float(
                self.ink_config.get(
                    "bleed_strength",
                    0.25
                )
            )

        if strength <= 0:
            return image

        # IMPORTANT:
        # copy=True guarantees writable NumPy memory.
        array = np.array(
            image,
            copy=True
        ).astype(
            np.float32
        )

        alpha = array[:, :, 3]

        alpha_image = Image.fromarray(
            np.clip(
                alpha,
                0,
                255
            ).astype(
                np.uint8
            ),
            mode="L"
        )

        radius = max(
            0.2,
            strength * 1.5
        )

        blurred_alpha = alpha_image.filter(
            ImageFilter.GaussianBlur(
                radius=radius
            )
        )

        bleed_alpha = np.array(
            blurred_alpha,
            copy=True
        ).astype(
            np.float32
        )

        mix = min(
            0.5,
            strength
        )

        new_alpha = (
            alpha * (1.0 - mix)
            + bleed_alpha * mix
        )

        array[:, :, 3] = np.clip(
            new_alpha,
            0,
            255
        )

        return Image.fromarray(
            array.astype(np.uint8),
            mode="RGBA"
        )

    # =========================================================
    # FADE
    # =========================================================

    def apply_fade(
        self,
        image: Image.Image,
        strength: float | None = None
    ) -> Image.Image:

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if strength is None:
            strength = float(
                self.ink_config.get(
                    "fade_strength",
                    0.20
                )
            )

        strength = max(
            0.0,
            min(1.0, strength)
        )

        array = np.array(
            image,
            copy=True
        ).astype(
            np.float32
        )

        alpha = array[:, :, 3]

        rng = np.random.default_rng(
            self.random.randint(
                0,
                2_000_000_000
            )
        )

        noise = rng.uniform(
            0.0,
            1.0,
            size=alpha.shape
        )

        fade_mask = (
            noise < strength * 0.08
        )

        count = np.count_nonzero(
            fade_mask
        )

        if count > 0:

            fade_values = rng.uniform(
                0.25,
                0.75,
                size=count
            )

            alpha[fade_mask] *= fade_values

        array[:, :, 3] = np.clip(
            alpha,
            0,
            255
        )

        return Image.fromarray(
            array.astype(np.uint8),
            mode="RGBA"
        )

    # =========================================================
    # HIGHLIGHT
    # =========================================================

    def add_highlight(
        self,
        image: Image.Image,
        color: Tuple[int, int, int] = (
            155,
            125,
            55
        ),
        opacity: int = 55
    ) -> Image.Image:

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(
            overlay
        )

        width, height = image.size

        margin_x = max(
            2,
            int(width * 0.02)
        )

        margin_y = max(
            2,
            int(height * 0.02)
        )

        draw.rounded_rectangle(
            [
                margin_x,
                margin_y,
                width - margin_x,
                height - margin_y
            ],
            radius=5,
            fill=(
                color[0],
                color[1],
                color[2],
                opacity
            )
        )

        return Image.alpha_composite(
            image,
            overlay
        )

    # =========================================================
    # COMPLETE INK PIPELINE
    # =========================================================

    def process_ink(
        self,
        image: Image.Image,
        apply_smudge: bool = True,
        apply_bleed: bool = True,
        apply_fade: bool = True,
        apply_variation: bool = True
    ) -> Image.Image:

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        result = image

        # Opacity
        result = self.apply_opacity(
            result
        )

        # Natural variation
        if apply_variation:

            result = self.apply_ink_variation(
                result
            )

        # Bleeding
        bleed_probability = float(
            self.ink_config.get(
                "bleed_probability",
                0.20
            )
        )

        if (
            apply_bleed
            and self.random.random()
            < bleed_probability
        ):

            result = self.apply_bleed(
                result,
                strength=float(
                    self.ink_config.get(
                        "bleed_strength",
                        0.25
                    )
                )
            )

        # Smudging
        smudge_probability = float(
            self.ink_config.get(
                "smudge_probability",
                0.18
            )
        )

        if (
            apply_smudge
            and self.random.random()
            < smudge_probability
        ):

            result = self.apply_smudge(
                result,
                strength=float(
                    self.ink_config.get(
                        "smudge_strength",
                        0.35
                    )
                )
            )

        # Fading
        fade_probability = float(
            self.ink_config.get(
                "fade_probability",
                0.15
            )
        )

        if (
            apply_fade
            and self.random.random()
            < fade_probability
        ):

            result = self.apply_fade(
                result,
                strength=float(
                    self.ink_config.get(
                        "fade_strength",
                        0.20
                    )
                )
            )

        return result


# =============================================================
# FACTORY
# =============================================================

def create_effects(
    config: dict,
    seed: int = 42
) -> ManuscriptEffects:

    return ManuscriptEffects(
        config=config,
        seed=seed
    )