import os
import pandas as pd
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.coordinates import match_coordinates_sky
import astropy.units as u
from pykoa.koa import Koa
import scipy
import argparse
import csv

# load standard stars from csv file
def load_stars():
    script_dir = os.path.dirname(os.path.abspath("__file__"))  
    
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))  

    data_path = os.path.join(repo_root, "data", "standard_stars.csv")

    stars = []
    with open(data_path, mode="r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            stars.append((row[0], row[1], row[2]))  # (Name, RA, DEC)
    
    return stars


def check_calibrations(date, outpath='./downloads/', days_to_check=7, tolerance_arcsec=5):
    if not os.path.exists(outpath):
        os.makedirs(outpath) 

    stars = load_stars()

    # Convert coordinates to SkyCoord objectss
    star_coords = [(name, SkyCoord(ra, dec, frame='icrs', unit=(u.hourangle, u.deg))) for name, ra, dec in stars]

    # requierd calibrations list
    required_calibrations = ['BIAS', 'DOMEFLAT', 'TWIFLAT', 'FLATLAMP', 'ARCLAMP', 'CONTBARS', 'DARK']
    found_dates = {cal: [] for cal in required_calibrations}
    found_dates['STANDARD'] = []

    def check_date_for_calibrations(check_date):
        metadata_path = os.path.join(outpath, f'koa_metadata_{check_date}.tbl')

        # if metadata file doesn't exist, query metadata from KOA
        if not os.path.isfile(metadata_path):
            try:
                Koa.query_date(instrument='kcwi', date=check_date, outpath=metadata_path, overwrite=True)
            except Exception as e:
                print(f"Error querying metadata for {check_date}: {e}")
                return None, None, None

        if not os.path.isfile(metadata_path):
            print(f"No metadata found for {check_date}.")
            return None, None, None

        table = Table.read(metadata_path, format='ascii.ipac')
        calibrations = list(set([str(row['koaimtyp']).upper() for row in table]))
        ra_dec_coords = SkyCoord(ra=table['ra'] * u.deg, dec=table['dec'] * u.deg)
        return calibrations, ra_dec_coords, table

    # Verify calibrations and standard stars for the given date
    print(f"Checking calibrations for {date}...")
    calibrations, ra_dec_coords, table = check_date_for_calibrations(date)

    if calibrations is None:
        return

    # determine missing calibrations
    missing_calibrations = [cal for cal in required_calibrations if cal not in calibrations]
    if missing_calibrations:
        print(f"Missing calibrations: {missing_calibrations}")
    else:
        print("All calibrations are present :D")

    # Verify if standard stars are present
    found_star = False
    for name, coord in star_coords:
        idx, sep, _ = match_coordinates_sky(coord, ra_dec_coords)
        if sep.arcsecond <= tolerance_arcsec:
            found_dates['STANDARD'].append((date, name, table['koaid'][idx]))
            print(f"Standard star {name} found on {date}, file: {table['koaid'][idx]}")
            found_star = True

    # if there are missing calibrations or no standard star found, check previous and next days
    if missing_calibrations or not found_dates['STANDARD']:
        for offset in range(1, days_to_check + 1):
            for delta in [-offset, offset]:
                check_date = (pd.to_datetime(date) + pd.Timedelta(days=delta)).strftime('%Y-%m-%d')
                print(f"Checking calibrations for {check_date}...")
                calibrations, ra_dec_coords, table = check_date_for_calibrations(check_date)

                if calibrations is None:
                    continue

                for cal in missing_calibrations:
                    if cal in calibrations and check_date not in found_dates[cal]:
                        found_dates[cal].append(check_date)
                        print(f"Calibration {cal} found on {check_date}.")

                if not found_star:
                    for name, coord in star_coords:
                        idx, sep, _ = match_coordinates_sky(coord, ra_dec_coords)
                        if sep.arcsecond <= tolerance_arcsec and check_date not in [d[0] for d in found_dates['STANDARD']]:
                            found_dates['STANDARD'].append((check_date, name, table['koaid'][idx]))
                            print(f"Standard star {name} found on {check_date}, file: {table['koaid'][idx]}")

    # report all dates where the missing calibrations were found
    for cal, dates in found_dates.items():
        if dates:
            if cal == 'STANDARD':
                if not found_star:
                    for date, name, file_id in dates:
                        print(f"Standard star {name} found on {date}, file: {file_id}.")
            else:
                print(f"Calibration {cal} found on dates: {dates}")
        elif cal in missing_calibrations:
            print(f"Calibration {cal} not found in the checked range of dates.")

def main():
    parser = argparse.ArgumentParser(description = "Find missing calibrations and standard stars for a given date.")
    parser.add_argument('date', type=str, help="Fecha de la observación en formato 'YYYY-MM-DD'.")
    parser.add_argument('days_to_check', type=int, default=7, help="Número de días a revisar antes y después de la fecha dada.")
    parser.add_argument('tolerance_arcsec', type=int, default=5, help="Tolerancia en arco segundos para la coincidencia de coordenadas.")
    parser.add_argument('--output_dir', type=str, default='.', help="Directorio de salida para los archivos descargados.")
    

    args = parser.parse_args()

    try:
        check_calibrations(args.date, outpath=args.output_dir, days_to_check=args.days_to_check, tolerance_arcsec=args.tolerance_arcsec)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()