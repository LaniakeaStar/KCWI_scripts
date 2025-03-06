import argparse
import os
from pykoa.koa import Koa
import shutil
from astropy.table import Table

def download_files_by_date(date, output_dir='.', filename_type='all'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata_path = os.path.join(output_dir, f'koa_metadata_{date}.tbl')
    Koa.query_date(instrument='kcwi', date=date, outpath=metadata_path, overwrite=True, format='ipac')

    if not os.path.isfile(metadata_path):
        print(f"No se encontraron archivos para la fecha {date}.")
        return

    table = Table.read(metadata_path, format='ascii.ipac')

    # filter the table according to the filename type
    if filename_type == 'telescope':
        table = table[table['ofname'] != '']
    elif filename_type == 'archive':
        table = table[table['ofname'] == '']

    # save the filtered table
    filtered_metadata_path = os.path.join(output_dir, f'koa_metadata_{date}_filtered.tbl')
    table.write(filtered_metadata_path, format='ascii.ipac', overwrite=True)

    # download files according to the filtered table
    Koa.download(
        metapath=filtered_metadata_path,
        format='ipac',
        outdir=output_dir,
        calibfile=1
    )

    # move files to output_dir
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.fits'):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(output_dir, file)
                if source_path != destination_path:
                    shutil.move(source_path, destination_path)

    # remove not desired directories
    for folder in ["lev0","calib"]:
        folder_path = os.path.join(output_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    print(f"Files downloaded to {output_dir}.")



def main():
    parser = argparse.ArgumentParser(description="Download KCWI data from the Keck Observatory Archive (KOA) by date.")
    parser.add_argument('date', type=str, help="Fecha de la observación en formato 'YYYY-MM-DD'.")
    parser.add_argument('filename_type', type=str, default='all', choices=['all', 'telescope', 'archive'], help="Tipo de nombre de archivo para filtrar (por defecto, 'all').")
    parser.add_argument('--output_dir', type=str, default='.', help="Directorio de salida (por defecto, donde estás en la terminal).")
    

    args = parser.parse_args()

    try:
        download_files_by_date(date = args.date, output_dir = args.output_dir)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()