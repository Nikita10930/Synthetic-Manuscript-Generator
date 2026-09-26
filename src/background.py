# src/background.py

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import random


class ManuscriptBackgroundGenerator:
    """
    Generates realistic historical manuscript backgrounds.

    Supports:
        - aged_handmade_paper
        - palm_leaf

    Features:
        - visible paper grain
        - natural fibers
        - stains
        - age spots
        - darkened edges
        - folds and creases
        - palm-leaf longitudinal fibers
        - sharp final texture
    """

    def __init__(self, width, height, config=None, seed=None):
        self.width = width
        self.height = height
        self.config = config or {}

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    # =========================================================
    # MAIN GENERATOR
    # =========================================================

    def generate(self, manuscript_type="aged_handmade_paper"):

        if manuscript_type == "palm_leaf":
            return self._palm_leaf()

        return self._handmade_paper()

    # =========================================================
    # HANDMADE PAPER
    # =========================================================

    def _handmade_paper(self):

        w = self.width
        h = self.height

        # -----------------------------------------------------
        # Base parchment color
        # -----------------------------------------------------

        base = np.zeros((h, w, 3), dtype=np.float32)

        base_color = np.array(
            [202, 177, 133],
            dtype=np.float32
        )

        base[:, :, :] = base_color

        # -----------------------------------------------------
        # Fine paper grain
        # -----------------------------------------------------

        fine_noise = np.random.normal(
            0,
            7,
            (h, w)
        )

        # -----------------------------------------------------
        # Medium-scale texture
        # -----------------------------------------------------

        small_h = max(2, h // 12)
        small_w = max(2, w // 12)

        medium_noise = np.random.normal(
            0,
            1,
            (small_h, small_w)
        )

        medium_img = Image.fromarray(
            np.uint8(
                np.clip(
                    medium_noise * 35 + 128,
                    0,
                    255
                )
            ),
            "L"
        )

        medium_img = medium_img.resize(
            (w, h),
            Image.Resampling.BICUBIC
        )

        medium_noise = (
            np.asarray(medium_img).astype(np.float32)
            - 128
        )

        # -----------------------------------------------------
        # Large paper variation
        # -----------------------------------------------------

        large_h = max(2, h // 35)
        large_w = max(2, w // 35)

        large_noise = np.random.normal(
            0,
            1,
            (large_h, large_w)
        )

        large_img = Image.fromarray(
            np.uint8(
                np.clip(
                    large_noise * 40 + 128,
                    0,
                    255
                )
            ),
            "L"
        )

        large_img = large_img.resize(
            (w, h),
            Image.Resampling.BICUBIC
        )

        large_noise = (
            np.asarray(large_img).astype(np.float32)
            - 128
        )

        # -----------------------------------------------------
        # Combine textures
        # -----------------------------------------------------

        texture = (
            fine_noise * 0.65
            + medium_noise * 0.30
            + large_noise * 0.45
        )

        base[:, :, 0] += texture * 1.00
        base[:, :, 1] += texture * 0.78
        base[:, :, 2] += texture * 0.52

        # -----------------------------------------------------
        # Natural edge aging
        # -----------------------------------------------------

        yy, xx = np.mgrid[0:h, 0:w]

        center_x = w / 2
        center_y = h / 2

        distance = np.sqrt(
            ((xx - center_x) / center_x) ** 2
            + ((yy - center_y) / center_y) ** 2
        )

        edge_strength = np.clip(
            distance,
            0,
            1
        )

        base[:, :, 0] -= edge_strength * 20
        base[:, :, 1] -= edge_strength * 23
        base[:, :, 2] -= edge_strength * 27

        # -----------------------------------------------------
        # Convert to image
        # -----------------------------------------------------

        image = Image.fromarray(
            np.uint8(
                np.clip(base, 0, 255)
            ),
            "RGB"
        )

        # -----------------------------------------------------
        # PAPER FIBERS
        # -----------------------------------------------------

        draw = ImageDraw.Draw(
            image,
            "RGBA"
        )

        fiber_count = int(
            w * h * 0.000025
        )

        for _ in range(fiber_count):

            x = random.randint(
                0,
                w - 1
            )

            y = random.randint(
                0,
                h - 1
            )

            length = random.randint(
                8,
                45
            )

            angle = random.uniform(
                -0.25,
                0.25
            )

            x2 = min(
                w - 1,
                x + length
            )

            y2 = max(
                0,
                min(
                    h - 1,
                    int(y + length * angle)
                )
            )

            fiber_color = random.choice([
                (92, 67, 39, 45),
                (120, 91, 55, 38),
                (75, 55, 35, 30),
                (235, 215, 175, 40)
            ])

            draw.line(
                (x, y, x2, y2),
                fill=fiber_color,
                width=random.choice([
                    1,
                    1,
                    1,
                    2
                ])
            )

        # -----------------------------------------------------
        # NATURAL STAINS
        # -----------------------------------------------------

        stain_layer = Image.new(
            "RGBA",
            (w, h),
            (0, 0, 0, 0)
        )

        stain_draw = ImageDraw.Draw(
            stain_layer,
            "RGBA"
        )

        stain_count = random.randint(
            12,
            25
        )

        for _ in range(stain_count):

            x = random.randint(
                -100,
                w + 100
            )

            y = random.randint(
                -100,
                h + 100
            )

            radius_x = random.randint(
                25,
                130
            )

            radius_y = random.randint(
                15,
                90
            )

            stain_color = random.choice([
                (92, 61, 30, 18),
                (112, 76, 39, 20),
                (73, 49, 25, 15),
                (145, 105, 60, 18)
            ])

            stain_draw.ellipse(
                (
                    x - radius_x,
                    y - radius_y,
                    x + radius_x,
                    y + radius_y
                ),
                fill=stain_color
            )

        # Only stains are softened.
        stain_layer = stain_layer.filter(
            ImageFilter.GaussianBlur(
                radius=2.0
            )
        )

        image = Image.alpha_composite(
            image.convert("RGBA"),
            stain_layer
        ).convert("RGB")

        # -----------------------------------------------------
        # SMALL AGE SPOTS
        # -----------------------------------------------------

        draw = ImageDraw.Draw(
            image,
            "RGBA"
        )

        for _ in range(100):

            x = random.randint(
                0,
                w - 1
            )

            y = random.randint(
                0,
                h - 1
            )

            radius = random.choice([
                1,
                1,
                2,
                2,
                3,
                4
            ])

            spot_color = random.choice([
                (75, 50, 27, 32),
                (105, 72, 35, 30),
                (55, 40, 25, 25)
            ])

            draw.ellipse(
                (
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius
                ),
                fill=spot_color
            )

        # -----------------------------------------------------
        # DARK AGED EDGES
        # -----------------------------------------------------

        edge = np.zeros(
            (h, w),
            dtype=np.float32
        )

        left = np.arange(w)
        right = np.arange(w)[::-1]

        top = np.arange(h)
        bottom = np.arange(h)[::-1]

        horizontal_distance = np.minimum(
            left,
            right
        )

        vertical_distance = np.minimum(
            top,
            bottom
        )

        distance_from_edge = np.minimum(
            vertical_distance[:, None],
            horizontal_distance[None, :]
        )

        edge_strength = np.clip(
            1 -
            distance_from_edge / 150,
            0,
            1
        )

        edge[:, :] = edge_strength

        edge_rgba = np.zeros(
            (h, w, 4),
            dtype=np.uint8
        )

        edge_rgba[:, :, 0] = 55
        edge_rgba[:, :, 1] = 38
        edge_rgba[:, :, 2] = 22

        edge_rgba[:, :, 3] = np.uint8(
            edge * 95
        )

        edge_layer = Image.fromarray(
            edge_rgba,
            "RGBA"
        )

        image = Image.alpha_composite(
            image.convert("RGBA"),
            edge_layer
        ).convert("RGB")

        # -----------------------------------------------------
        # FOLDS / CREASES
        # -----------------------------------------------------

        fold_layer = Image.new(
            "RGBA",
            (w, h),
            (0, 0, 0, 0)
        )

        fold_draw = ImageDraw.Draw(
            fold_layer,
            "RGBA"
        )

        # Vertical folds
        for _ in range(
            random.randint(1, 3)
        ):

            x = random.randint(
                int(w * 0.15),
                int(w * 0.85)
            )

            points = []

            for y in range(
                0,
                h,
                20
            ):

                offset = random.randint(
                    -3,
                    3
                )

                points.append(
                    (x + offset, y)
                )

            # Dark crease
            fold_draw.line(
                points,
                fill=(75, 53, 30, 45),
                width=2
            )

            # Light side of crease
            fold_draw.line(
                [
                    (px + 2, py)
                    for px, py in points
                ],
                fill=(245, 225, 185, 35),
                width=1
            )

        # Horizontal folds
        for _ in range(
            random.randint(1, 2)
        ):

            y = random.randint(
                int(h * 0.15),
                int(h * 0.85)
            )

            points = []

            for x in range(
                0,
                w,
                20
            ):

                offset = random.randint(
                    -2,
                    2
                )

                points.append(
                    (x, y + offset)
                )

            fold_draw.line(
                points,
                fill=(75, 53, 30, 38),
                width=1
            )

        image = Image.alpha_composite(
            image.convert("RGBA"),
            fold_layer
        ).convert("RGB")

        # -----------------------------------------------------
        # FINAL SHARPNESS
        # -----------------------------------------------------

        image = ImageEnhance.Contrast(
            image
        ).enhance(1.08)

        # Important:
        # Do NOT blur the final image.
        # This keeps fibers and texture sharp.

        return image

    # =========================================================
    # PALM LEAF
    # =========================================================

    def _palm_leaf(self):

        w = self.width
        h = self.height

        base = np.zeros(
            (h, w, 3),
            dtype=np.float32
        )

        base_color = np.array(
            [181, 151, 92],
            dtype=np.float32
        )

        base[:, :, :] = base_color

        # -----------------------------------------------------
        # Fine palm-leaf grain
        # -----------------------------------------------------

        fine_noise = np.random.normal(
            0,
            6,
            (h, w)
        )

        base[:, :, 0] += fine_noise * 0.90
        base[:, :, 1] += fine_noise * 0.70
        base[:, :, 2] += fine_noise * 0.45

        image = Image.fromarray(
            np.uint8(
                np.clip(
                    base,
                    0,
                    255
                )
            ),
            "RGB"
        )

        draw = ImageDraw.Draw(
            image,
            "RGBA"
        )

        # -----------------------------------------------------
        # Long palm-leaf fibers
        # -----------------------------------------------------

        for _ in range(130):

            y = random.randint(
                0,
                h - 1
            )

            points = []

            amplitude = random.uniform(
                1.0,
                4.0
            )

            phase = random.random()

            for x in range(
                0,
                w,
                30
            ):

                yy = y + int(
                    np.sin(
                        x * 0.015 + phase
                    ) * amplitude
                )

                yy = max(
                    0,
                    min(
                        h - 1,
                        yy
                    )
                )

                points.append(
                    (x, yy)
                )

            fiber_color = random.choice([
                (73, 52, 26, 50),
                (105, 76, 35, 42),
                (126, 91, 43, 32),
                (230, 205, 145, 30)
            ])

            draw.line(
                points,
                fill=fiber_color,
                width=random.choice([
                    1,
                    1,
                    2
                ])
            )

        # -----------------------------------------------------
        # Small natural marks
        # -----------------------------------------------------

        for _ in range(120):

            x = random.randint(
                0,
                w - 1
            )

            y = random.randint(
                0,
                h - 1
            )

            length = random.randint(
                3,
                15
            )

            draw.line(
                (
                    x,
                    y,
                    min(w - 1, x + length),
                    max(
                        0,
                        min(
                            h - 1,
                            y + random.randint(-2, 2)
                        )
                    )
                ),
                fill=(
                    70,
                    50,
                    25,
                    random.randint(20, 50)
                ),
                width=1
            )

        # -----------------------------------------------------
        # Edge aging
        # -----------------------------------------------------

        yy, xx = np.mgrid[
            0:h,
            0:w
        ]

        center_x = w / 2
        center_y = h / 2

        distance = np.sqrt(
            ((xx - center_x) / center_x) ** 2
            +
            ((yy - center_y) / center_y) ** 2
        )

        edge_strength = np.clip(
            distance,
            0,
            1
        )

        arr = np.asarray(
            image
        ).astype(
            np.float32
        )

        arr[:, :, 0] -= edge_strength * 20
        arr[:, :, 1] -= edge_strength * 18
        arr[:, :, 2] -= edge_strength * 12

        image = Image.fromarray(
            np.uint8(
                np.clip(
                    arr,
                    0,
                    255
                )
            ),
            "RGB"
        )

        # -----------------------------------------------------
        # Palm-leaf stains
        # -----------------------------------------------------

        stain_layer = Image.new(
            "RGBA",
            (w, h),
            (0, 0, 0, 0)
        )

        stain_draw = ImageDraw.Draw(
            stain_layer,
            "RGBA"
        )

        for _ in range(20):

            x = random.randint(
                0,
                w
            )

            y = random.randint(
                0,
                h
            )

            rx = random.randint(
                20,
                100
            )

            ry = random.randint(
                5,
                30
            )

            stain_draw.ellipse(
                (
                    x - rx,
                    y - ry,
                    x + rx,
                    y + ry
                ),
                fill=(
                    70,
                    48,
                    22,
                    random.randint(
                        10,
                        25
                    )
                )
            )

        stain_layer = stain_layer.filter(
            ImageFilter.GaussianBlur(
                radius=1.5
            )
        )

        image = Image.alpha_composite(
            image.convert("RGBA"),
            stain_layer
        ).convert("RGB")

        image = ImageEnhance.Contrast(
            image
        ).enhance(1.10)

        # No final blur.
        return image


# =============================================================
# MAIN FUNCTION USED BY TEST + DATASET GENERATOR
# =============================================================

def create_background(
    width,
    height,
    manuscript_type="aged_handmade_paper",
    config=None,
    seed=None
):
    """
    Create a manuscript background.

    Parameters
    ----------
    width : int
        Image width.

    height : int
        Image height.

    manuscript_type : str
        Either:
            aged_handmade_paper
            palm_leaf

    config : dict
        Optional configuration dictionary.

    seed : int
        Optional random seed.

    Returns
    -------
    PIL.Image
        RGB manuscript background.
    """

    generator = ManuscriptBackgroundGenerator(
        width=width,
        height=height,
        config=config,
        seed=seed
    )

    return generator.generate(
        manuscript_type
    )