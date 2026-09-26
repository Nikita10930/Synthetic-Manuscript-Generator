from pathlib import Path
import random

from src.text_loader import TextLoader
from src.renderer import render_manuscript
from src.background import create_background


class ManuscriptDatasetGenerator:
    """
    Generates the complete synthetic manuscript dataset.

    For each script:
        100 images total
        85 train
        10 validation
        5 test

    Old generated PNG/MD files are removed before regeneration
    so repeated runs always produce an exact dataset.
    """

    def __init__(self, config):
        self.config = config

        # -----------------------------------------------------
        # DATASET CONFIGURATION
        # -----------------------------------------------------

        dataset_config = config.get("dataset", {})

        self.images_per_script = int(
            dataset_config.get("images_per_script", 100)
        )

        self.seed = int(
            dataset_config.get("seed", 42)
        )

        self.output_dir = Path(
            dataset_config.get(
                "output_dir",
                "data/output"
            )
        )

        # -----------------------------------------------------
        # SPLIT CONFIGURATION
        # -----------------------------------------------------

        split_config = dataset_config.get(
            "split",
            {}
        )

        self.train_count = int(
            split_config.get("train", 85)
        )

        self.validation_count = int(
            split_config.get("validation", 10)
        )

        self.test_count = int(
            split_config.get("test", 5)
        )

        # -----------------------------------------------------
        # SCRIPT CONFIGURATION
        # -----------------------------------------------------

        self.scripts = config.get(
            "scripts",
            {}
        )

        # -----------------------------------------------------
        # RANDOM GENERATOR
        # -----------------------------------------------------

        self.random = random.Random(
            self.seed
        )

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        expected_total = (
            self.train_count
            + self.validation_count
            + self.test_count
        )

        if expected_total != self.images_per_script:
            raise ValueError(
                "Dataset split counts do not match "
                "images_per_script. "
                f"Expected {self.images_per_script}, "
                f"but got {expected_total}."
            )

    # =========================================================
    # OUTPUT DIRECTORIES
    # =========================================================

    def create_output_directories(self):
        """
        Create train/validation/test directories
        for every configured script.
        """

        for script in self.scripts:

            for split in [
                "train",
                "validation",
                "test"
            ]:

                directory = (
                    self.output_dir
                    / script
                    / split
                )

                directory.mkdir(
                    parents=True,
                    exist_ok=True
                )

    # =========================================================
    # CLEAN OLD GENERATED DATA
    # =========================================================

    def clean_script_output(self, script):
        """
        Remove old generated PNG and Markdown files
        for one script.

        This prevents duplicate IDs when the generator
        is executed multiple times.
        """

        script_dir = (
            self.output_dir
            / script
        )

        if not script_dir.exists():
            return

        removed_png = 0
        removed_md = 0

        for split in [
            "train",
            "validation",
            "test"
        ]:

            split_dir = (
                script_dir
                / split
            )

            if not split_dir.exists():
                continue

            # Remove PNG files
            for file in split_dir.glob("*.png"):

                try:
                    file.unlink()
                    removed_png += 1

                except OSError as error:

                    print(
                        f"Warning: Could not remove "
                        f"{file}: {error}"
                    )

            # Remove Markdown files
            for file in split_dir.glob("*.md"):

                try:
                    file.unlink()
                    removed_md += 1

                except OSError as error:

                    print(
                        f"Warning: Could not remove "
                        f"{file}: {error}"
                    )

        if removed_png or removed_md:

            print(
                f"Cleaned {script}: "
                f"{removed_png} PNG + "
                f"{removed_md} MD"
            )

    # =========================================================
    # CREATE SPLIT LIST
    # =========================================================

    def create_split_list(self):
        """
        Create deterministic 85/10/5 split list.
        """

        split_list = (
            ["train"] * self.train_count
            + ["validation"] * self.validation_count
            + ["test"] * self.test_count
        )

        # Use a fresh deterministic random generator
        # so every script receives a reproducible split.
        local_random = random.Random(
            self.seed
        )

        local_random.shuffle(
            split_list
        )

        return split_list

    # =========================================================
    # TEXT LOADER
    # =========================================================

    def get_text_loader(self, script):

        script_config = self.scripts[script]

        source_file = script_config[
            "source_file"
        ]

        return TextLoader(
            source_file
        )

    # =========================================================
    # RENDER CONFIG
    # =========================================================

    def get_render_config(self):

        return self.config

    # =========================================================
    # MANUSCRIPT TYPE
    # =========================================================

    def choose_manuscript_type(
        self,
        script_random
    ):
        """
        Select palm-leaf or aged handmade paper
        according to configuration probabilities.
        """

        manuscript_config = self.config.get(
            "manuscript",
            {}
        )

        palm_probability = float(
            manuscript_config.get(
                "palm_leaf_probability",
                0.50
            )
        )

        handmade_probability = float(
            manuscript_config.get(
                "handmade_paper_probability",
                0.50
            )
        )

        total_probability = (
            palm_probability
            + handmade_probability
        )

        if total_probability <= 0:
            return "aged_handmade_paper"

        palm_probability = (
            palm_probability
            / total_probability
        )

        if script_random.random() < palm_probability:

            return "palm_leaf"

        return "aged_handmade_paper"

    # =========================================================
    # GENERATE ONE IMAGE
    # =========================================================

    def generate_single_image(
        self,
        script,
        index,
        split,
        text_loader
    ):
        """
        Generate one manuscript image.
        """

        # -----------------------------------------------------
        # Deterministic image seed
        # -----------------------------------------------------

        image_seed = (
            self.seed
            + index * 1009
            + len(script) * 37
            + len(split) * 101
        )

        image_random = random.Random(
            image_seed
        )

        # -----------------------------------------------------
        # Canvas configuration
        # -----------------------------------------------------

        canvas_config = self.config.get(
            "canvas",
            {}
        )

        width = int(
            canvas_config.get(
                "width",
                1600
            )
        )

        height = int(
            canvas_config.get(
                "height",
                1000
            )
        )

        # -----------------------------------------------------
        # Manuscript type
        # -----------------------------------------------------

        manuscript_type = (
            self.choose_manuscript_type(
                image_random
            )
        )

        # -----------------------------------------------------
        # Background
        # -----------------------------------------------------

        background = create_background(
            width=width,
            height=height,
            manuscript_type=manuscript_type,
            config=self.config,
            seed=image_seed
        )

        # -----------------------------------------------------
        # Select source text
        # -----------------------------------------------------

        
        text = text_loader.get_random_chunk(script)
        

        # -----------------------------------------------------
        # Render manuscript
        # -----------------------------------------------------

        render_result = render_manuscript(
            text=text,
            script=script,
            config=self.get_render_config(),
            background=background,
            seed=image_seed
        )

        # -----------------------------------------------------
        # Image filename
        # -----------------------------------------------------

        image_filename = (
            f"{script}_{index:04d}.png"
        )

        image_path = (
            self.output_dir
            / script
            / split
            / image_filename
        )

        image_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # -----------------------------------------------------
        # Save image
        # -----------------------------------------------------

        image = render_result["image"]

        image.save(
            image_path,
            format="PNG"
        )

        # -----------------------------------------------------
        # Return metadata for annotations
        # -----------------------------------------------------

        return {
            "image_path": str(
                image_path
            ),
            "script": script,
            "split": split,
            "index": index,
            "transcription": render_result.get(
                "transcription",
                text
            ),
            "manuscript_type": manuscript_type,
            "seed": image_seed,
        }

    # =========================================================
    # GENERATE ONE SCRIPT
    # =========================================================

    def generate_script(self, script):
        """
        Generate exactly images_per_script images
        for one script.
        """

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"Generating script: "
            f"{script}"
        )

        print(
            "=" * 70
        )

        # -----------------------------------------------------
        # Clean previous generated files FIRST
        # -----------------------------------------------------

        self.clean_script_output(
            script
        )

        # -----------------------------------------------------
        # Create directories again
        # -----------------------------------------------------

        for split in [
            "train",
            "validation",
            "test"
        ]:

            (
                self.output_dir
                / script
                / split
            ).mkdir(
                parents=True,
                exist_ok=True
            )

        # -----------------------------------------------------
        # Text loader
        # -----------------------------------------------------

        text_loader = self.get_text_loader(
            script
        )

        # -----------------------------------------------------
        # Create exact split list
        # -----------------------------------------------------

        split_list = self.create_split_list()

        if len(split_list) != self.images_per_script:

            raise RuntimeError(
                "Invalid split list length: "
                f"{len(split_list)}"
            )

        results = []

        # -----------------------------------------------------
        # Generate images
        # -----------------------------------------------------

        for index in range(
            1,
            self.images_per_script + 1
        ):

            split = split_list[
                index - 1
            ]

            result = (
                self.generate_single_image(
                    script=script,
                    index=index,
                    split=split,
                    text_loader=text_loader
                )
            )

            results.append(
                result
            )

            # Progress
            if (
                index == 1
                or index % 10 == 0
                or index == self.images_per_script
            ):

                print(
                    f"[{index:03d}/"
                    f"{self.images_per_script}] "
                    f"{split:<10} "
                    f"{Path(result['image_path']).name}"
                )

        # -----------------------------------------------------
        # Verify split counts
        # -----------------------------------------------------

        train_count = sum(
            1
            for item in results
            if item["split"] == "train"
        )

        validation_count = sum(
            1
            for item in results
            if item["split"] == "validation"
        )

        test_count = sum(
            1
            for item in results
            if item["split"] == "test"
        )

        print(
            "\nSplit summary:"
        )

        print(
            f"  Train:      {train_count}"
        )

        print(
            f"  Validation: {validation_count}"
        )

        print(
            f"  Test:       {test_count}"
        )

        # -----------------------------------------------------
        # Strict validation
        # -----------------------------------------------------

        if train_count != self.train_count:
            raise RuntimeError(
                f"Train count incorrect: "
                f"{train_count}"
            )

        if validation_count != self.validation_count:
            raise RuntimeError(
                f"Validation count incorrect: "
                f"{validation_count}"
            )

        if test_count != self.test_count:
            raise RuntimeError(
                f"Test count incorrect: "
                f"{test_count}"
            )

        if len(results) != self.images_per_script:
            raise RuntimeError(
                f"Total generated images incorrect: "
                f"{len(results)}"
            )

        print(
            f"Successfully generated "
            f"{len(results)} images for {script}."
        )

        return results

    # =========================================================
    # GENERATE COMPLETE DATASET
    # =========================================================

    def generate_all(self):
        """
        Generate the complete dataset
        for all configured scripts.
        """

        print(
            "\n"
            + "=" * 70
        )

        print(
            "STARTING DATASET GENERATION"
        )

        print(
            "=" * 70
        )

        self.create_output_directories()

        all_results = {}

        for script in self.scripts:

            results = (
                self.generate_script(
                    script
                )
            )

            all_results[
                script
            ] = results

        print(
            "\n"
            + "=" * 70
        )

        print(
            "ALL SCRIPTS GENERATED"
        )

        print(
            "=" * 70
        )

        return all_results

    # =========================================================
    # SUMMARY
    # =========================================================

    def get_summary(self):
        """
        Count generated PNG files
        in every split.
        """

        summary = {}

        for script in self.scripts:

            summary[script] = {}

            for split in [
                "train",
                "validation",
                "test"
            ]:

                split_dir = (
                    self.output_dir
                    / script
                    / split
                )

                png_count = len(
                    list(
                        split_dir.glob(
                            "*.png"
                        )
                    )
                )

                md_count = len(
                    list(
                        split_dir.glob(
                            "*.md"
                        )
                    )
                )

                summary[script][
                    split
                ] = {
                    "png": png_count,
                    "md": md_count,
                }

        return summary

    # =========================================================
    # PRINT SUMMARY
    # =========================================================

    def print_summary(self):
        """
        Print final dataset summary.
        """

        summary = self.get_summary()

        print(
            "\n"
            + "=" * 70
        )

        print(
            "FINAL DATASET SUMMARY"
        )

        print(
            "=" * 70
        )

        total_png = 0
        total_md = 0

        for script, splits in summary.items():

            print(
                f"\n{script.upper()}"
            )

            for split, counts in splits.items():

                png_count = counts["png"]
                md_count = counts["md"]

                total_png += png_count
                total_md += md_count

                print(
                    f"  {split:<12} "
                    f"PNG: {png_count:<4} "
                    f"MD: {md_count:<4}"
                )

        print(
            "\n"
            + "-" * 70
        )

        print(
            f"TOTAL PNG: {total_png}"
        )

        print(
            f"TOTAL MD : {total_md}"
        )

        print(
            "-" * 70
        )

        # -----------------------------------------------------
        # Expected totals
        # -----------------------------------------------------

        expected_png = (
            len(self.scripts)
            * self.images_per_script
        )

        expected_md = expected_png

        if total_png == expected_png:

            print(
                "✓ PNG count is correct."
            )

        else:

            print(
                f"⚠ Expected {expected_png} PNG "
                f"but found {total_png}."
            )

        if total_md == expected_md:

            print(
                "✓ MD count is correct."
            )

        else:

            print(
                f"⚠ Expected {expected_md} MD "
                f"but found {total_md}."
            )

        print(
            "=" * 70
        )