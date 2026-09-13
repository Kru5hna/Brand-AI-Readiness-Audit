"""
Packaging Script for Adobe University Hackathon Round 3 Submission
Packages the marketplace root into brand-ai-readiness-audit.zip and validates contents.
"""

import os
import zipfile

WORKSPACE_DIR = os.path.abspath(os.path.dirname(__file__))
ZIP_OUTPUT = os.path.join(WORKSPACE_DIR, "brand-ai-readiness-audit.zip")

EXCLUDE_DIRS = {".git", ".system_generated", "__pycache__", ".pytest_cache", ".gemini", "scratch"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".zip"}


def create_submission_zip():
    print(f"Creating submission zip: {ZIP_OUTPUT}")
    file_count = 0
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORKSPACE_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, WORKSPACE_DIR)
                # Ensure archive root structure
                arcname = os.path.join("brand-ai-readiness-audit", rel_path)
                zf.write(full_path, arcname)
                file_count += 1

    size_bytes = os.path.getsize(ZIP_OUTPUT)
    size_mb = size_bytes / (1024 * 1024)
    print(f"Archived {file_count} files.")
    print(f"Zip size: {size_bytes} bytes ({size_mb:.2f} MB).")
    assert size_mb <= 50.0, f"Zip file exceeds 50 MB limit: {size_mb:.2f} MB"
    print("Verification: Zip size is well within the 50 MB limit.")

    # Inspect zip contents
    with zipfile.ZipFile(ZIP_OUTPUT, "r") as zf:
        names = zf.namelist()
        print(f"Sample archived files:\n" + "\n".join(f"  - {n}" for n in names[:15]))
        manifest_found = any("marketplace.json" in n for n in names)
        readme_found = any("README.md" in n for n in names)
        print(f"Contains marketplace.json: {manifest_found}")
        print(f"Contains README.md: {readme_found}")


if __name__ == "__main__":
    create_submission_zip()
