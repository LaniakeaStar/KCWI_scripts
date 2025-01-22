import argparse
import os
from astropy.table import Table
from pykoa.koa import Koa

def obs_table_date(date, output_dir='./outputKC/', data_type='both'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    outpath = os.path.join(output_dir, f'koa_metadata_{date}.tbl')
    Koa.query_date(instrument='kcwi', date=date, outpath=outpath, overwrite=True) # Query by date
    table = Table.read(outpath, format='ascii.ipac')
    
    # filter by data type
    if data_type.lower() == 'science':
        table = table[[val == 'object' for val in table['koaimtyp']]]
    elif data_type.lower() == 'calibration':
        table = table[[val != 'object' for val in table['koaimtyp']]]
    
    # Relevant columns
    relevant_columns = ['koaid', 'ofname', 'targname', 'koaimtyp', 'ra', 'dec', 'date_obs', 'camera']
    table = table[relevant_columns]
    
    return table


def main():
    parser = argparse.ArgumentParser(description="Query KCWI observations by date.")
    parser.add_argument('date', type=str, help="Fecha de la observación en formato 'YYYY-MM-DD'.")
    parser.add_argument('--data_type', type=str, default='both', choices=['both', 'science', 'calibration'],
                        help="Tipo de datos: 'both', 'science' o 'calibration' (por defecto 'both').")
    parser.add_argument('--outpath', type=str, default='./outputKC/', help="Directorio de salida (por defecto './outputKC/').")

    args = parser.parse_args()

    try:
        table = obs_table_date(date = args.date, data_type = args.data_type, output_dir = args.outpath)
        print(table)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()