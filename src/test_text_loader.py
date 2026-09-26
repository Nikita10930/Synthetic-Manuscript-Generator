from text_loader import TextLoader


def test_script(script, source_file):
    print("\n" + "=" * 60)
    print(f"TESTING: {script.upper()}")
    print("=" * 60)

    loader = TextLoader(
        source_file=source_file,
        seed=42
    )

    # Load complete source
    text = loader.load()

    print(f"Source size: {len(text):,} characters")

    # Get script-specific lines
    lines = loader.get_script_lines(script)

    print(f"Usable lines: {len(lines):,}")

    # Create chunks
    chunks = loader.make_chunks(
        script=script,
        min_chars=80,
        max_chars=350
    )

    print(f"Generated chunks: {len(chunks):,}")

    # Display one sample
    if chunks:
        print("\nSample chunk:")
        print("-" * 60)
        print(chunks[0])
        print("-" * 60)

    return len(text), len(lines), len(chunks)


def main():

    results = {}

    results["devanagari"] = test_script(
        "devanagari",
        "data/source/devanagari.md"
    )

    results["modi"] = test_script(
        "modi",
        "data/source/modi.md"
    )

    results["sharada"] = test_script(
        "sharada",
        "data/source/sharada.md"
    )

    print("\n")
    print("=" * 60)
    print("TEXT LOADER TEST SUMMARY")
    print("=" * 60)

    for script, values in results.items():
        text_size, lines, chunks = values

        print(
            f"{script.capitalize():12} | "
            f"Characters: {text_size:,} | "
            f"Lines: {lines:,} | "
            f"Chunks: {chunks:,}"
        )

    print("=" * 60)
    print("TEXT LOADER TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()