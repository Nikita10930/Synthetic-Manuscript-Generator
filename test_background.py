from pathlib import Path
import yaml

from src.background import create_background


# ---------------------------------------------------------
# Load configuration
# ---------------------------------------------------------

CONFIG_PATH = Path("config/config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


# ---------------------------------------------------------
# Output folder
# ---------------------------------------------------------

output_dir = Path("samples")
output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Generate test backgrounds
# ---------------------------------------------------------

width = config["canvas"]["width"]
height = config["canvas"]["height"]


# Aged handmade paper
paper = create_background(
    config=config,
    width=width,
    height=height,
    manuscript_type="aged_handmade_paper",
    seed=42
)

paper_path = output_dir / "background_paper_test.png"

paper.save(
    paper_path,
    "PNG"
)


# Palm leaf
palm_leaf = create_background(
    config=config,
    width=width,
    height=height,
    manuscript_type="palm_leaf",
    seed=43
)

palm_path = output_dir / "background_palm_leaf_test.png"

palm_leaf.save(
    palm_path,
    "PNG"
)


# ---------------------------------------------------------
# Result
# ---------------------------------------------------------

print("BACKGROUND TEST COMPLETED SUCCESSFULLY!")
print(f"Paper background: {paper_path}")
print(f"Palm-leaf background: {palm_path}")