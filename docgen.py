import ast
import os


def extract_docstrings(tree):
    docs = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            docs.append(
                ("Class", node.name, ast.get_docstring(node) or "No docstring.")
            )
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    docs.append(
                        (
                            "Method",
                            f"{node.name}.{sub.name}",
                            ast.get_docstring(sub) or "No docstring.",
                        )
                    )
        elif isinstance(node, ast.FunctionDef):
            docs.append(
                ("Function", node.name, ast.get_docstring(node) or "No docstring.")
            )
    return docs


def generate_doc(input_file, output_dir):
    base = os.path.splitext(os.path.basename(input_file))[0]
    folder = os.path.join(output_dir, base)
    docs_md = os.path.join(folder, "DOCS.md")
    with open(input_file, "r", encoding="utf‑8") as f:
        tree = ast.parse(f.read())
    entries = extract_docstrings(tree)
    with open(docs_md, "w", encoding="utf‑8") as f:
        f.write(f"# Documentation for `{base}`\n\n")
        for kind, name, doc in entries:
            f.write(f"## {kind}: `{name}`\n\n{doc}\n\n")
    print(f"📄 DOCS.md written to {folder}")
