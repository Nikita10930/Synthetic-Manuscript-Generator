from pathlib import Path
import yaml
import os

from src.text_loader import load_text_from_config
from src.background import create_background
from src.renderer import render_manuscript


def load_config():
    config_path = Path("config/config.yaml")

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as f:
        return yaml.safe_load(f)


def main():

    config = load_config()

    output_dir = Path("samples")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    scripts = [
        "devanagari",
        "modi",
        "sharada"
    ]

    print()
    print("=" * 60)
    print("SYNTHETIC MANUSCRIPT RENDERER TEST")
    print("=" * 60)

    for script in scripts:

        print()
        print(f"Testing: {script}")

        # -------------------------------------------------
        # Load source text
        # -------------------------------------------------

        loader = load_text_from_config(
            config,
            script
        )

        text = loader.get_random_chunk(
            script,
            min_chars=500,
            max_chars=1800
        )

        print(
            f"Source file: {loader.source_file}"
        )

        print(
            f"Text length: {len(text)} characters"
        )

        # -------------------------------------------------
        # Background
        # -------------------------------------------------

        if script == "modi":
            manuscript_type = "aged_handmade_paper"
        else:
            manuscript_type = "palm_leaf"

        background = create_background(
            config=config,
            width=config["canvas"]["width"],
            height=config["canvas"]["height"],
            manuscript_type=manuscript_type,
            seed=config["randomness"]["seed"]
        )

        # -------------------------------------------------
        # Render manuscript
        # -------------------------------------------------

        result = render_manuscript(
            config=config,
            script=script,
            text=text,
            background=background,
            seed=config["randomness"]["seed"]
        )

        # -------------------------------------------------
        # Extract result
        # -------------------------------------------------

        image = result["image"]

        lines = result["lines"]

        transcription = result["transcription"]

        rendered_script = result["script"]

        # -------------------------------------------------
        # Save image
        # -------------------------------------------------

        output_path = (
            output_dir
            / f"renderer_{script}_test.png"
        )

        image.save(output_path)

        # -------------------------------------------------
        # Print test information
        # -------------------------------------------------

        print(
            f"Rendered script: {rendered_script}"
        )

        print(
            f"Rendered lines: {len(lines)}"
        )

        print(
            f"Transcription length: "
            f"{len(transcription)}"
        )

        print(
            f"Output: {output_path}"
        )

        print(
            "Status: SUCCESS"
        )

    print()
    print("=" * 60)
    print(
        "RENDERER TEST COMPLETED SUCCESSFULLY!"
    )
    print("=" * 60)

    print()
    print("Generated files:")

    for script in scripts:

        print(
            f"  samples/"
            f"renderer_{script}_test.png"
        )


if __name__ == "__main__":
    main()