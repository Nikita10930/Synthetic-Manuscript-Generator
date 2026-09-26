from pathlib import Path
import yaml

from src.dataset_generator import ManuscriptDatasetGenerator
from src.annotation_generator import AnnotationGenerator


def load_config():
    """Load project configuration."""

    config_path = Path("config/config.yaml")

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with config_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return yaml.safe_load(file)


def main():
    print("=" * 70)
    print("SYNTHETIC MANUSCRIPT GENERATOR")
    print("=" * 70)

    # -----------------------------------------------------
    # LOAD CONFIG
    # -----------------------------------------------------

    config = load_config()

    print("\nConfiguration loaded successfully.")

    # -----------------------------------------------------
    # CREATE DATASET GENERATOR
    # -----------------------------------------------------

    dataset_generator = (
        ManuscriptDatasetGenerator(config)
    )

    # -----------------------------------------------------
    # GENERATE IMAGES
    # -----------------------------------------------------

    generation_results = (
        dataset_generator.generate_all()
    )

    # -----------------------------------------------------
    # CREATE ANNOTATIONS
    # -----------------------------------------------------

    annotation_generator = (
        AnnotationGenerator(config)
    )

    annotation_results = (
        annotation_generator.generate_all(
            generation_results
        )
    )

    # -----------------------------------------------------
    # PRINT SUMMARY
    # -----------------------------------------------------

    dataset_generator.print_summary()

    total_annotations = sum(
        len(items)
        for items in annotation_results.values()
    )

    print("\n" + "=" * 70)
    print("ANNOTATION SUMMARY")
    print("=" * 70)

    print(
        f"Total annotation files: "
        f"{total_annotations}"
    )

    print("\n" + "=" * 70)
    print("GENERATION FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()