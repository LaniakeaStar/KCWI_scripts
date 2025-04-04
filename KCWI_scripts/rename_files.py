import os
from astropy.table import Table
import argparse


def rename_fits_files(directory="."): 
    if directory != ".":  
        os.chdir(directory)

    # search for the metadata file
    metadata_file = None
    for file in os.listdir():
        if file.endswith("_filtered.tbl"):
            metadata_file = file
            break

    if metadata_file is None:
        print("No metadata file found.")
        return

    table = Table.read(metadata_file, format='ascii.ipac')

    # Check if the table has the required columns
    if 'koaid' not in table.colnames or 'ofname' not in table.colnames:
        print(f"Metadata file {metadata_file} is missing 'koaid' or 'ofname' columns.")
        return
    
    # Make dictonary with format {koaid: ofname}
    rename_map = {row['koaid']: row['ofname'] for row in table if row['ofname'].strip()}

    # Rename the files
    fits_files = [f for f in os.listdir() if f.endswith(".fits")]
    renamed_count = 0

    for fits in fits_files:
        if fits in rename_map:
            new_name = rename_map[fits]
            if not new_name.endswith(".fits"):
                new_name += ".fits"  # Asegurar que termine en .fits

            try:
                os.rename(fits, new_name)
                print(f"{fits} → {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"Failed to rename {fits}: {e}")

    if renamed_count == 0:
        print("No files found to rename.")
    else:
        print(f"\n {renamed_count} files were renamed.")

def main():
    parser = argparse.ArgumentParser(description="Rename KCWI FITS files according to the 'ofname' column in the metadata file.")
    parser.add_argument('--directory', type=str, default='.', help="Directory where the FITS files are located (default: current directory).")
    args = parser.parse_args()

    try:
        rename_fits_files(args.directory)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()