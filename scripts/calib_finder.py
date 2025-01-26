import os
import pandas as pd
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.coordinates import match_coordinates_sky
import astropy.units as u
from pykoa.koa import Koa
import scipy
import argparse

def check_calibrations(date, outpath='./downloads/', days_to_check=7, tolerance_arcsec=5):
    # Crear el directorio de salida si no existe
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    stars = [
        ("l870-2", "01 37 59.34", "-04 59 44.3"),
        ("feige15", "01 49 09.4819", "+13 33 11.761"),
        ("feige24", "02 35 07.59376", "+03 43 56.7993"),
        ("feige25", "02 38 37.78362", "+05 28 11.2842"),
        ("hd19445", "03 08 25.58962", "+26 19 51.3957"),
        ("gd50", "03 48 50.06", "-00 58 30.4"),
        ("sa95-42", "03 53 43.67", "-00 04 33.0"),
        ("hz4", "03 55 21.70", "+09 47 18.7"),
        ("lb1240", "04 04 34.126", "+25 08 51.76"),
        ("lb227", "04 09 28.76", "+17 07 54.4"),
        ("hz2", "04 12 43.51", "+11 51 50.4"),
        ("40erib", "04 15 21.786", "-07 39 29.22"),
        ("hz7", "04 33 44.95", "+12 42 40.4"),
        ("hz15", "04 40 39.32651", "+08 40 45.3375"),
        ("hz14", "04 41 01.74", "+10 59 40.0"),
        ("g191b2b", "05 05 30.62", "+52 49 54.0"),
        ("g99-37", "05 51 19.48", "-00 10 21.3"),
        ("hil600", "06 45 13.3706", "+02 08 14.697"),
        ("he3", "06 47 37.99365", "+37 30 57.0724"),
        ("l745-46a", "07 40 20.794", "-17 24 49.20"),
        ("g193-74", "07 53 27.40", "+52 29 35.7"),
        ("bd75d325", "08 10 49.31", "+74 57 57.5"),
        ("bd08d2015", "08 15 41.624", "+07 37 06.03"),
        ("g47-18", "08 59 14.76", "+32 57 12.1"),
        ("sa29-130", "09 46 39.076", "+43 54 52.37"),
        ("hd84937", "09 48 56.09801", "+13 44 39.3237"),
        ("gd108", "10 00 47.33", "-07 33 31.2"),
        ("feige34", "10 39 36.71", "+43 06 10.1"),
        ("hd93521", "10 48 23.51", "+37 34 12.8"),
        ("l970-30", "11 07 59.950", "-05 09 26.10"),
        ("ton573", "11 09 59.83", "+26 18 47.7"),
        ("ross627", "11 24 13.11", "+21 21 35.6"),
        ("gd140", "11 37 05.10419", "+29 47 58.3433"),
        ("feige56", "12 06 47.25", "+11 40 12.7"),
        ("hz21", "12 13 56.42", "+32 56 30.8"),
        ("hz29", "12 34 54.619", "+37 37 44.11"),
        ("feige66", "12 37 23.55", "+25 04 00.3"),
        ("feige67", "12 41 51.83", "+17 31 20.5"),
        ("g60-54", "13 00 09.53", "+03 28 55.7"),
        ("hz43", "13 16 21.99", "+29 05 57.0"),
        ("hz44", "13 23 35.37", "+36 08 00.0"),
        ("wolf485", "13 30 13.64025", "-08 34 29.4963"),
        ("grw70d5824", "13 38 51.77", "+70 17 08.5"),
        ("feige92", "14 11 31.87700", "+50 07 04.1359"),
        ("feige98", "14 38 15.7666", "+27 29 32.988"),
        ("bd26d2606", "14 49 02.35669", "+25 42 09.1572"),
        ("gd190", "15 44 19.456", "+18 06 43.21"),
        ("bd33d2642", "15 51 59.86", "+32 56 54.8"),
        ("g138-31", "16 27 53.59", "+09 12 24.5"),
        ("ross640", "16 28 25.03", "+36 46 15.4"),
        ("bd02d3375", "17 39 45.59", "+02 24 59.6"),
        ("kopff27", "17 43 55.840", "+05 24 48.23"),
        ("grw70d8247", "19 00 10.25", "+70 39 51.2"),
        ("bd25d3941", "19 44 26.1351", "+26 13 16.656"),
        ("bd40d4032", "20 08 24.1381", "+41 15 03.908"),
        ("wolf1346", "20 34 21.88303", "+25 03 49.7426"),
        ("grw73d8031", "21 26 57.659", "+73 38 44.53"),
        ("lds749b", "21 32 15.75", "+00 15 13.6"),
        ("l1363-3", "21 42 40.998", "+20 59 58.24"),
        ("l930-80", "21 47 37.292", "-07 44 12.20"),
        ("bd28d4211", "21 51 11.07", "+28 51 51.8"),
        ("g93-48", "21 52 25.33", "+02 23 24.3"),
        ("bd25d4655", "21 59 42.02", "+26 25 58.1"),
        ("bd17d4708", "22 11 31.37377", "+18 05 34.1730"),
        ("ngc7293", "22 29 38.46", "-20 50 13.3"),
        ("ltt9491", "23 19 34.98", "-17 05 29.8"),
        ("feige110", "23 19 58.39", "-05 09 55.8"),
        ("gd248", "23 26 06.69", "+16 00 21.4"),
        ("l1512-34b", "23 43 50.72545", "+32 32 46.6544")
    ]
    
    # convert star coordinates to SkyCoord objects
    star_coords = [(name, SkyCoord(ra, dec, frame='icrs', unit=(u.hourangle, u.deg))) for name, ra, dec in stars]

    # required calibrations list
    required_calibrations = ['BIAS', 'DARK', 'FLAT', 'DOMEFLAT', 'ARCLAMP', 'CONTBARS']
    found_dates = {cal: [] for cal in required_calibrations}
    found_dates['STANDARD'] = []

    def check_date_for_calibrations(check_date):
        metadata_path = os.path.join(outpath, f'koa_metadata_{check_date}.tbl')
        if not os.path.isfile(metadata_path):
            print(f"No metadata found for {check_date}.")
            return None, None

        table = Table.read(metadata_path, format='ascii.ipac')
        calibrations = list(set([str(row["koaimtyp"]).upper() for row in table]))
        ra_dec_coords = SkyCoord(ra=table['ra'] * u.deg, dec=table['dec'] * u.deg)
        return calibrations, ra_dec_coords, table

    # Verificar calibraciones y estrellas estándar para la fecha dada
    print(f"Checking calibrations for {date}...")
    calibrations, ra_dec_coords, table = check_date_for_calibrations(date)

    if calibrations is None:
        return

    # Determinar calibraciones faltantes
    missing_calibrations = [cal for cal in required_calibrations if cal not in calibrations]
    print(f"Missing calibrations: {missing_calibrations}")

    #Verify if standard stars are present
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
                try:
                    calibrations, ra_dec_coords, table = check_date_for_calibrations(check_date)
                except:
                    continue

                if calibrations is None:
                    print("No calibrations found.")
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

    # Report all dates where the missing calibrations were found
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

# Ejemplo de uso
check_calibrations('2020-05-20', outpath='./downloads/', days_to_check=30, tolerance_arcsec=5)

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