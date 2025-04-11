import os
from astropy.table import Table
import argparse
import shutil


def rename_fits_files(output_dir = "./renamed_files", directory=".", metadata_file = None): 
    if metadata_file is not None and not os.path.isabs(metadata_file):
        metadata_file = os.path.join(directory, metadata_file)
    
    # Change to the specified directory
    if directory != ".":  
        os.chdir(directory)


    # search for the metadata file if not provided
    if metadata_file is None:
        for file in os.listdir():
            if file.endswith("_filtered.tbl"):
                metadata_file = file
                break

    if metadata_file is None:
        print("No metadata file found.")
        return
    
    elif not os.path.exists(metadata_file):
        print(f"Metadata file {metadata_file} does not exist.")
        return

    table = Table.read(metadata_file, format='ascii.ipac')

    # Check if the table has the required columns
    if 'koaid' not in table.colnames or 'ofname' not in table.colnames:
        print(f"Metadata file {metadata_file} is missing 'koaid' or 'ofname' columns.")
        return
    
    # Make dictonary with format {koaid: ofname}
    rename_map = {row['koaid']: row['ofname'] for row in table if row['ofname'].strip()}

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Rename the files
    fits_files = [f for f in os.listdir() if f.endswith(".fits")]
    renamed_count = 0

    for fits in fits_files:
        if fits in rename_map:
            new_name = rename_map[fits]
            if not new_name.endswith(".fits"):
                new_name += ".fits"  # Asegurar que termine en .fits

            src_path = os.path.join(directory, fits)
            dst_path = os.path.join(output_dir, new_name) 

            try:
                shutil.copy(src_path, dst_path)  # Copy the file to the new location
                print(f"{fits} → {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"Failed to rename {fits}: {e}")

    if renamed_count == 0:
        print("No files found to rename.")
    else:
        print(f"\n {renamed_count} files were copied and renamed into '{output_dir}'.")

def main():
    parser = argparse.ArgumentParser(description="Rename KCWI FITS files according to the 'ofname' column in the metadata file.")
    parser.add_argument('--output_dir', type=str, default='./renamed_files', help="Directory to save renamed files (default: ./renamed_files).")
    parser.add_argument('--directory', type=str, default='.', help="Directory where the FITS files are located (default: current directory).")
    parser.add_argument('--metadata_file', type=str, default=None, help="Path to the metadata file (default: search for *_filtered.tbl in the directory).")
    args = parser.parse_args()

    try:
        rename_fits_files(args.output_dir, args.directory, args.metadata_file)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()