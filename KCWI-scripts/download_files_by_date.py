import argparse
import os
from pykoa.koa import Koa

def download_files_by_date(date, output_dir='.'): #por defecto, en el mismo directrorio
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata_path = os.path.join(output_dir, f'koa_metadata_{date}.tbl')

    Koa.query_date(instrument='kcwi', date=date, outpath=metadata_path, overwrite=True, format='ipac')

    if not os.path.isfile(metadata_path):
        print(f"No files found for {date}.")
    else:
        # science and calibration
        Koa.download(
            metapath = metadata_path,
            format = 'ipac',
            outdir = output_dir,
            calibfile = 1  # Include calibration files
        )

        print(f"files downloaded on directory: {output_dir}")


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