"""Generate the code reference pages for mkdocstrings."""

from pathlib import Path

import mkdocs_gen_files

# This is the directory we'll scan for .py files
src_path = Path("src")

# This is the directory where we'll create the .md files
doc_path = Path("api_reference")

for path in sorted(src_path.rglob("*.py")):
    # Get the path relative to the src/ directory
    # e.g., 'src/aloegraph/graph.py' -> 'aloegraph/graph.py'
    module_path = path.relative_to(src_path)
    
    # Don't document __init__.py files directly, we'll do the package
    if module_path.name == "__init__.py":
        # Create an 'index.md' for the package
        doc_path_md = doc_path / module_path.parent / "index.md"
    else:
        # 'aloegraph/graph.py' -> 'aloegraph/graph.md'
        doc_path_md = doc_path / module_path.with_suffix(".md")

        # Get the full Python module "identifier"
        # 'aloegraph/graph.py' -> 'aloegraph.graph'
        # 'aloegraph/__init__.py' -> 'aloegraph'
    parts = list(module_path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
        
    # If it's an empty list (e.g. 'src/__init__.py'), skip
    if not parts:
        continue
        
    identifier = ".".join(parts)

    # Open the target .md file
    with mkdocs_gen_files.open(doc_path_md, "w") as f:
        # Write the mkdocstrings "identifier" to the file
        print(f"::: {identifier}", file=f)

    # We don't need add_doc_path(doc_path_md) because
    # the 'nav' in mkdocs.yml already points to the
    # 'api_reference/' directory, and MkDocs finds all
    # .md files in there automatically.