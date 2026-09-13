"""
Packaging Script for Adobe University Hackathon Round 3 Submission
Packages the marketplace root directory into brand-ai-readiness-audit.zip.

Per the submission spec:
  "a ZIP file of the marketplace root directory, containing marketplace.json
   and every skill folder, along with a short README.md at the root"

So the ZIP root should directly contain:
  marketplace.json
  README.md
  skills/
"""

import os
import zipfile

WORKSPACE_DIR = os.path.abspath(os.path.dirname(__file__))
ZIP_OUTPUT = os.path.join(WORKSPACE_DIR, "brand-ai-readiness-audit.zip")

# Only include what the submission spec requires
INCLUDE_FILES = {"marketplace.json", "README.md"}
INCLUDE_DIRS = {"skills"}

# Explicitly forbidden in submission archive
FORBIDDEN_FILES = {"imple.md", "impl.md", "PROJECT_CONTEXT.md", "package_submission.py"}
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", "tests"}
EXCLUDE_EXTS = {".pyc", ".pyo"}


def create_submission_zip():
    print(f"Creating submission zip: {ZIP_OUTPUT}")
    file_count = 0
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add root-level required files
        for fname in INCLUDE_FILES:
            fpath = os.path.join(WORKSPACE_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, fname)  # marketplace.json at ZIP root
                file_count += 1
                print(f"  + {fname}")

        # Add skill directories
        for dname in INCLUDE_DIRS:
            dpath = os.path.join(WORKSPACE_DIR, dname)
            if not os.path.isdir(dpath):
                continue
            for root, dirs, files in os.walk(dpath):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for file in files:
                    if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                        continue
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, WORKSPACE_DIR)
                    zf.write(full_path, rel_path)  # skills/... at ZIP root
                    file_count += 1

    size_bytes = os.path.getsize(ZIP_OUTPUT)
    size_mb = size_bytes / (1024 * 1024)
    print(f"\nArchived {file_count} files.")
    print(f"Zip size: {size_bytes:,} bytes ({size_mb:.2f} MB)")
    assert size_mb <= 50.0, f"Zip file exceeds 50 MB limit: {size_mb:.2f} MB"
    print("Size check PASSED (within 50 MB limit).")

    # Verify required contents
    with zipfile.ZipFile(ZIP_OUTPUT, "r") as zf:
        names = zf.namelist()
        print(f"\nAll archived files ({len(names)}):")
        for n in sorted(names):
            print(f"  {n}")

        # Validate structure
        checks = {
            "marketplace.json at root": "marketplace.json" in names,
            "README.md at root": "README.md" in names,
            "skills/ directory present": any(n.startswith("skills/") for n in names),
            "audit-orchestrator skill": any("audit-orchestrator/SKILL.md" in n for n in names),
            "crawler-access-audit skill": any("crawler-access-audit/SKILL.md" in n for n in names),
            "structured-data-entity-audit skill": any("structured-data-entity-audit/SKILL.md" in n for n in names),
            "content-extractability-audit skill": any("content-extractability-audit/SKILL.md" in n for n in names),
            "engagement-conversion-audit skill": any("engagement-conversion-audit/SKILL.md" in n for n in names),
            "imple.md NOT in zip": not any("imple.md" in n.lower() for n in names),
            "PROJECT_CONTEXT.md NOT in zip": not any("project_context.md" in n.lower() for n in names),
            "tests/ NOT in zip": not any(n.startswith("tests/") for n in names),
        }

        print("\nSubmission Checklist:")
        all_ok = True
        for check, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {check}")
            if not passed:
                all_ok = False

        if all_ok:
            print("\nALL CHECKS PASSED -- Ready to submit!")
        else:
            print("\nSOME CHECKS FAILED -- Fix before submitting!")


if __name__ == "__main__":
    create_submission_zip()
