#!/usr/bin/env python3
"""
Third-Party License Report Generator

This script generates a comprehensive license report for all third-party Python
dependencies used in this project.

Usage:
    python generate_licenses.py              # Generate license report
    python generate_licenses.py -y           # Skip confirmation prompt

Requirements:
    - Python 3.11+
    - uv (Python package manager)
    - pip-licenses (installed automatically via uv --with flag)

Output File:
    - databao-cli-third-party-list.csv - CSV report with all Python dependencies

The CSV includes columns for Name, Version, License, Author, and URL.
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path | None = None, description: str = "") -> bool:
    """Run a shell command and return success status."""
    if description:
        print(f"📦 {description}...")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False


def generate_python_licenses(output_file: Path, no_confirm: bool = False) -> bool:
    """
    Generate Python license report using uv and pip-licenses.

    This command:
    1. Syncs production dependencies only (--no-dev)
    2. Runs pip-licenses in the project environment (uv run --with pip-licenses)
    3. Generates a CSV with package names, versions, licenses, authors, and URLs
    4. Filters out the project itself from the final output (see read_python_licenses)

    Note: We can't use --no-install-project or uv tool run because:
    - uv run --with reinstalls the project regardless of --no-install-project
    - uv tool run runs in isolation and can't see the synced dependencies
    - Solution: Install everything including the project, then filter it out in post-processing

    Args:
        output_file: Path to write the CSV output
        no_confirm: Skip confirmation prompt if True
    """
    # Warn user about environment modification
    if not no_confirm:
        print("⚠️  WARNING: This will modify your current Python environment!")
        print("   The environment will be synced to PRODUCTION dependencies only.")
        print("   - Development dependencies will be removed (--no-dev)")
        print("   You'll need to run 'uv sync' after this to restore dev dependencies.")
        print()
        response = input("Do you want to proceed? [y/N]: ").strip().lower()

        if response not in ("y", "yes"):
            print("❌ Cancelled by user.")
            return False
        print()

    # Determine paths
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent if script_dir.name == "scripts" else script_dir

    # Temporary intermediate file
    temp_file = base_dir / ".databao-cli-third-party-list-temp.csv"

    # First sync dependencies
    sync_cmd = [
        "uv",
        "sync",
        "--no-dev",
    ]

    if not run_command(sync_cmd, description="Syncing Python production dependencies"):
        return False

    # Then generate license report to temp file
    license_cmd = [
        "uv",
        "run",
        "--with",
        "pip-licenses",
        "pip-licenses",
        "--format=csv",
        "--with-urls",
        "--with-authors",
        f"--output-file={temp_file}",
    ]

    if not run_command(license_cmd, description=f"Generating Python licenses to {temp_file}"):
        return False

    # Read and filter the temporary file
    print("🔄 Filtering dependencies...")
    try:
        filtered_licenses = []

        with open(temp_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filter out the project itself - only include actual third-party dependencies
                if row["Name"].lower() == "databao-cli":
                    continue

                filtered_licenses.append(row)

        # Write filtered results to final output file
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            fieldnames = ["Name", "Version", "License", "Author", "URL"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_licenses)

        print(f"✅ Successfully created {output_file}")
        print(f"   Total: {len(filtered_licenses)} third-party packages")

        # Clean up temporary file
        if temp_file.exists():
            temp_file.unlink()
            print(f"🧹 Cleaned up temporary file: {temp_file.name}")

        return True

    except Exception as e:
        print(f"❌ Error processing licenses: {e}", file=sys.stderr)
        # Clean up on error
        if temp_file.exists():
            temp_file.unlink()
        return False


def main() -> int:
    """Main entry point for the license report generator."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-y",
        "--yes",
        "--no-confirm",
        dest="no_confirm",
        action="store_true",
        help="Skip confirmation prompts (auto-accept environment modifications)",
    )

    args = parser.parse_args()

    # Determine paths
    # Script is in scripts/, but outputs go to project root
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent if script_dir.name == "scripts" else script_dir

    # Final output file
    output_file = base_dir / "databao-cli-third-party-list.csv"

    # Generate Python licenses
    if not generate_python_licenses(output_file, no_confirm=args.no_confirm):
        return 1

    print("\n🎉 License report generation complete!")
    print(f"📄 Output: {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
