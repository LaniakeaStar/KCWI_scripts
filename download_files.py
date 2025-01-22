import argparse
import os
from pykoa.koa import Koa
import shutil

def download_files_by_date(date, output_dir='.'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata_path = os.path.join(output_dir, f'koa_metadata_{date}.tbl')
    Koa.query_date(instrument='kcwi', date=date, outpath=metadata_path, overwrite=True, format='ipac')

    if not os.path.isfile(metadata_path):
        print(f"No files found for {date}.")
        return

    # Download files
    Koa.download(
        metapath=metadata_path,
        format='ipac',
        outdir=output_dir,
        calibfile=1  
    )

    # Move files to output_dir
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.fits'):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(output_dir, file)
                if source_path != destination_path:
                    shutil.move(source_path, destination_path)

    # delete empty directories
    for root, dirs, files in os.walk(output_dir, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rmdir(dir_path)
            except OSError:
                pass  # directory not empty

    print(f"Files downloaded to directory: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Download KCWI data from the Keck Observatory Archive (KOA) by date.")
    parser.add_argument('date', type=str, help="Fecha de la observación en formato 'YYYY-MM-DD'.")
    parser.add_argument('--output_dir', type=str, default='./outputKC/', help="Directorio de salida (por defecto, donde estás en la terminal).")

    args = parser.parse_args()

    try:
        download_files_by_date(date = args.date, output_dir = args.output_dir)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()