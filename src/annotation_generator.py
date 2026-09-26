from pathlib import Path


class AnnotationGenerator:
    """
    Creates a Markdown annotation file for every generated
    manuscript image.
    """

    def __init__(self, config):
        self.config = config

        dataset_config = config.get("dataset", {})

        self.output_dir = Path(
            dataset_config.get(
                "output_dir",
                "data/output"
            )
        )

        annotation_config = config.get(
            "annotations",
            {}
        )

        self.enabled = annotation_config.get(
            "enabled",
            True
        )

        self.format = annotation_config.get(
            "format",
            "md"
        )

    # ---------------------------------------------------------
    # CREATE ANNOTATION CONTENT
    # ---------------------------------------------------------

    def create_annotation(
        self,
        script,
        split,
        image_filename,
        source_file,
        transcription,
    ):
        """
        Create the Markdown content for one image.
        """

        content = f"""# Manuscript Annotation

## Metadata

- **Script:** {script}
- **Split:** {split}
- **Image:** {image_filename}
- **Source file:** {source_file}

## Transcription

{transcription}

## Generation Details

- **Generator:** Synthetic Manuscript Generator
- **Format:** PNG
- **Annotation format:** Markdown
"""

        return content

    # ---------------------------------------------------------
    # SAVE ANNOTATION
    # ---------------------------------------------------------

    def save_annotation(
        self,
        script,
        split,
        image_filename,
        source_file,
        transcription,
    ):
        """
        Save one .md annotation beside its image.
        """

        if not self.enabled:
            return None

        image_path = (
            self.output_dir
            / script
            / split
            / image_filename
        )

        annotation_filename = (
            image_path.stem + ".md"
        )

        annotation_path = (
            image_path.parent
            / annotation_filename
        )

        content = self.create_annotation(
            script=script,
            split=split,
            image_filename=image_filename,
            source_file=source_file,
            transcription=transcription,
        )

        annotation_path.write_text(
            content,
            encoding="utf-8"
        )

        return annotation_path

    # ---------------------------------------------------------
    # GENERATE FOR ONE SCRIPT
    # ---------------------------------------------------------

    def generate_for_results(
        self,
        script,
        results,
    ):
        """
        Generate annotations for all rendered images
        returned by the dataset generator.
        """

        script_config = self.config["scripts"][script]

        source_file = script_config[
            "source_file"
        ]

        created = []

        for result in results:

            image_path = Path(
                result["image_path"]
            )

            image_filename = (
                image_path.name
            )

            split = result["split"]

            transcription = result.get(
                "transcription",
                ""
            )

            annotation_path = (
                self.save_annotation(
                    script=script,
                    split=split,
                    image_filename=image_filename,
                    source_file=source_file,
                    transcription=transcription,
                )
            )

            if annotation_path:
                created.append(
                    annotation_path
                )

        return created

    # ---------------------------------------------------------
    # GENERATE FOR COMPLETE DATASET
    # ---------------------------------------------------------

    def generate_all(
        self,
        generation_results,
    ):
        """
        Generate annotations for every script.
        """

        if not self.enabled:
            print(
                "Annotations are disabled in configuration."
            )
            return {}

        all_annotations = {}

        for script, results in (
            generation_results.items()
        ):

            print(
                f"\nGenerating annotations: "
                f"{script}"
            )

            annotations = (
                self.generate_for_results(
                    script=script,
                    results=results,
                )
            )

            all_annotations[script] = annotations

            print(
                f"Created {len(annotations)} "
                f"annotation files."
            )

        return all_annotations