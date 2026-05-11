import sys
import os

def concatenate_jsonl(input_files, output_file):
    """
    Concatenates multiple JSONL files into a single JSONL file, preserving the order.
    
    Args:
        input_files (list): List of input JSONL file paths.
        output_file (str): Path to the output JSONL file.
    """
    with open(output_file, "w", encoding="utf-8") as outfile:
        for file in input_files:
            if not os.path.isfile(file):
                print(f"Warning: File {file} does not exist. Skipping.")
                continue
            
            with open(file, "r", encoding="utf-8") as infile:
                for line in infile:
                    outfile.write(line)  # Write each line as-is
            
            print(f"Finished processing: {file}")

    print(f"\nAll files concatenated into {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python concat_jsonl.py output.jsonl input1.jsonl input2.jsonl ...")
        sys.exit(1)

    output_file = sys.argv[1]
    input_files = sys.argv[2:]

    concatenate_jsonl(input_files, output_file)
