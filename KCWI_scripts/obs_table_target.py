import argparse
from astropy.table import Table
from pykoa.koa import Koa
import os

def obs_table_target(ra, dec, radius=30, output_dir='.', data_type='both'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pos = f'circle {ra} {dec} {radius / 3600}'  # Convert radius to degrees
    outpath = os.path.join(output_dir, f'position_search_{ra}_{dec}_{radius}.tbl')
    # Check if the file already exists
    if not os.path.isfile(outpath):
        try:
            Koa.query_position(instrument='kcwi', pos=pos, outpath=outpath, overwrite=True)
        except Exception as e:
            print(f"❌ Error querying metadata for position {pos}: {e}")
            return None, None, None

    table = Table.read(outpath, format='ascii.ipac')

    # Filter by data type
    if data_type.lower() == 'science':
        table = table[[val == 'object' for val in table['koaimtyp']]]
    elif data_type.lower() == 'calibration':
        table = table[[val != 'object' for val in table['koaimtyp']]]

    # Relevant columns
    relevant_columns = ['koaid', 'ofname', 'targname', 'koaimtyp', 'ra', 'dec', 'date_obs', 'camera']
    table = table[relevant_columns]
    
    return table


def main():
    parser = argparse.ArgumentParser(description="Query KCWI observations by target.")
    parser.add_argument('ra', type=float, help="Ascensión recta (RA) en grados.")
    parser.add_argument('dec', type=float, help="Declinación (DEC) en grados.")
    parser.add_argument('--data_type', type=str, default='both', choices=['both', 'science', 'calibration'],
                        help="Tipo de datos: 'both', 'science' o 'calibration' (por defecto 'both').")
    parser.add_argument('--radius', type=float, default=30, help="Radio de búsqueda en arcsec (por defecto 30'').")
    parser.add_argument('--outpath', type=str, default='.', help="Directorio de salida (por defecto './outputKC/').")

    args = parser.parse_args()

    try:
        table = obs_table_target(ra=args.ra, dec=args.dec, data_type=args.data_type, radius=args.radius)
        print(table)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
