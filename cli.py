import argparse
import os
from splitter_core import write_split_files
from docgen import generate_doc

def main():
    parser = argparse.ArgumentParser(description="Script Splitter CLI")
    parser.add_argument("-i", "--input", required=True, help="Original .py script path")
    parser.add_argument("-o", "--output", default="output", help="Directory to hold split files")
    parser.add_argument("--doc", action="store_true", help="Include documentation generation")
    parser.add_argument("--config", help="Path to a configuration file")

    args = parser.parse_args()
    input_path = args.input.strip('"')
    if not os.path.isfile(input_path):
        print(f"Input not found: {input_path}")
        return
    os.makedirs(args.output, exist_ok=True)
    validation_success = write_split_files(input_path, args.output, args.config)
    
    if validation_success:
        print(f"\n✅ Splitting complete and validated! Files in {args.output}")
    else:
        print(f"\n⚠️ Splitting complete but validation found issues. Files in {args.output}")
        print("Check the validation output above for details.")
    if args.doc:
        generate_doc(input_path, args.output)

if __name__ == "__main__":
    main()
