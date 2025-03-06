import os
import pandas as pd
from astropy.table import Table
from astropy.coordinates import SkyCoord, match_coordinates_sky
import astropy.units as u
from pykoa.koa import Koa
import csv
import argparse

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

def find_calibrations(date, outpath='./downloads/', days_to_check=7, tolerance_arcsec=5, summary = False,
                          bias_min_nframes=7, flatlamp_min_nframes=6, domeflat_min_nframes=3, 
                          twiflat_min_nframes=1, dark_min_nframes=3, arc_min_nframes=1, contbars_min_nframes=1):

    if not os.path.exists(outpath):
        os.makedirs(outpath)

    # Dictionary with the minimum number of frames required for each calibration
    required_calibrations = {
        'BIAS': bias_min_nframes,
        'DOMEFLAT': domeflat_min_nframes,
        'TWIFLAT': twiflat_min_nframes,
        'FLATLAMP': flatlamp_min_nframes,
        'ARCLAMP': arc_min_nframes,
        'CONTBARS': contbars_min_nframes,
        'DARK': dark_min_nframes
    }

    found_calibrations = {cal: [] for cal in required_calibrations}
    missing_calibrations = {cal: required_calibrations[cal] for cal in required_calibrations}

    stars = load_stars()

    # Convert coordinates to SkyCoord objects
    star_skycoords = [(name, SkyCoord(ra, dec, frame='icrs', unit=(u.hourangle, u.deg))) for name, ra, dec in stars]
    
    found_star = None
    found_before = False
    download_list = []  

    def check_date_for_calibrations(check_date):
        metadata_path = os.path.join(outpath, f'koa_metadata_{check_date}.tbl')

        if not os.path.isfile(metadata_path):
            try:
                Koa.query_date(instrument='kcwi', date=check_date, outpath=metadata_path, overwrite=True)
            except Exception as e:
                print(f"❌ Error querying metadata for {check_date}: {e}")
                return None, None, None

        if not os.path.isfile(metadata_path):
            print(f"⚠️ No metadata found for {check_date}.")
            return None, None, None

        table = Table.read(metadata_path, format='ascii.ipac')

        calibrations = {row["koaimtyp"].upper(): row["koaid"] for row in table}
        ra_dec_coords = SkyCoord(ra=table['ra'] * u.deg, dec=table['dec'] * u.deg)

        return table, calibrations, ra_dec_coords

    print(f"Checking calibrations for {date}...")
    table, calibrations_koaid, ra_dec_coords = check_date_for_calibrations(date)

    if table is None:
        return

    for cal in required_calibrations:
        if cal in calibrations_koaid:
            found_calibrations[cal].append((date, calibrations_koaid[cal]))
            missing_calibrations[cal] -= 1

    for name, coord in star_skycoords:
        try:
            idx, sep, _ = match_coordinates_sky(coord, ra_dec_coords)
            if sep.arcsecond <= tolerance_arcsec:
                found_star = (date, name, table['koaid'][idx])
                found_before = True
                print(f"🌟 Standard star {name} found on {date}, file: {table['koaid'][idx]}")
                break 
        except:
            pass 

    if all(n <= 0 for n in missing_calibrations.values()) and found_star:
        print("\n✅ All required calibrations and a standard star are present.")
        return

    for offset in range(1, days_to_check + 1):
        if all(n <= 0 for n in missing_calibrations.values()) and found_star:
            break  

        for delta in [-offset, offset]:  
            check_date = (pd.to_datetime(date) + pd.Timedelta(days=delta)).strftime('%Y-%m-%d')
            print(f"Checking calibrations for {check_date}...")

            table, calibrations_koaid, ra_dec_coords = check_date_for_calibrations(check_date)

            if table is None:
                continue

            for cal in missing_calibrations:
                if missing_calibrations[cal] > 0 and cal in calibrations_koaid:
                    koaid = calibrations_koaid[cal]
                    print(f"📥 Adding {cal} from {check_date} (File: {koaid})...")
                    download_list.append(koaid)  
                    found_calibrations[cal].append((check_date, koaid))
                    missing_calibrations[cal] -= 1

            if not found_star:
                for name, coord in star_skycoords:
                    try:
                        idx, sep, _ = match_coordinates_sky(coord, ra_dec_coords)
                        if sep.arcsecond <= tolerance_arcsec:
                            found_star = (check_date, name, table['koaid'][idx])
                            print(f"🌟 Standard star {name} found on {check_date}, file: {table['koaid'][idx]}")
                            break  
                    except:
                        pass

            if all(n <= 0 for n in missing_calibrations.values()) and found_star:
                break  


    print("\n📊 ** Summary of all calibrations found **")
    for cal, found in found_calibrations.items():
        if found:
            print(f"✅ {cal}: {len(found)} frames found.")
            for fdate, ffile in found:
                print(f"   - {fdate}: {ffile}")
        else:
            print(f"❌ {cal}: No frames found.")

    if found_star and not found_before:
        print(f"\n🌟 Standard star {found_star[1]} found on {found_star[0]}, file: {found_star[2]}.")
    else:
        print("\n⚠️ No standard star found in the checked range.")

    if any(n > 0 for n in missing_calibrations.values()):
        print("\n⚠️ **Warning: Some calibrations are still missing:**")
        for cal, n in missing_calibrations.items():
            if n > 0:
                print(f"   - {cal}: {n} more needed.")
    else:
        print("\n🎉 **All required calibrations and a standard star were found successfully!**")

    if summary:
        summary_path = os.path.join(outpath, f"summary_{date}_with_{days_to_check*2}_days.txt")

        with open(summary_path, "w") as summary_file:
            summary_file.write(f"📊 **Summary of Calibration Search & Downloads for {date}:**\n\n")

            for cal, found in found_calibrations.items():
                if found:
                    summary_file.write(f"✅ {cal}: {len(found)} frames found.\n")
                    for fdate, ffile in found:
                        summary_file.write(f"   - {fdate}: {ffile}\n")
                else:
                    summary_file.write(f"❌ {cal}: No frames found.\n")

            if found_star:
                summary_file.write(f"\n🌟 Standard star {found_star[1]} found on {found_star[0]}, file: {found_star[2]}.\n")
            else:
                summary_file.write("\n⚠️ No standard star found in the checked range.\n")

            if any(n > 0 for n in missing_calibrations.values()):
                summary_file.write("\n⚠️ **Warning: Some calibrations are still missing:**\n")
                for cal, n in missing_calibrations.items():
                    if n > 0:
                        summary_file.write(f"   - {cal}: {n} more needed.\n")
            else:
                summary_file.write("\n🎉 **All required calibrations and a standard star were found successfully!**\n")
        print(f"\n📝 Summary file saved to: {summary_path}") 

def main():
    parser = argparse.ArgumentParser(description = "Search for a given number of calibrations and a standard star for a given date.")
    parser.add_argument('date', type=str, help = "Observation date in format: 'YYYY-MM-DD'.")
    parser.add_argument('days_to_check', type=int, default=7, help="Number of days to check before and after the given date.")
    parser.add_argument('tolerance_arcsec', type=int, default=5, help = "Tolerance in arcseconds for matching standard stars.")
    parser.add_argument('--summary', action = "store_true", help="Generate a summary file with the results. [y/n]")
    parser.add_argument('--output_dir', type=str, default='.', help = "Output directory for the metadata files.")
    parser.add_argument('--bias_min_nframes', type=int, default=7, help = "Minumun number of BIAS frames required.")
    parser.add_argument('--flatlamp_min_nframes', type=int, default=6, help = "Minumun number of FLATLAMP frames required.")
    parser.add_argument('--domeflat_min_nframes', type=int, default=3, help = "Minumun number of DOMEFLAT frames required.")
    parser.add_argument('--twiflat_min_nframes', type=int, default=1, help = "Minumun number of TWIFLAT frames required.")
    parser.add_argument('--dark_min_nframes', type=int, default=3, help = "Minumun number of DARK frames required.")
    parser.add_argument('--arc_min_nframes', type=int, default=1, help = "Minumun number of ARCLAMP frames required.")
    parser.add_argument('--contbars_min_nframes', type=int, default=1, help = "Minumun number of CONTBARS frames required.")    

    args = parser.parse_args()

    try:
        find_calibrations(args.date, outpath = args.output_dir, days_to_check = args.days_to_check, tolerance_arcsec = args.tolerance_arcsec, 
                          summary = args.summary,  bias_min_nframes = args.bias_min_nframes, flatlamp_min_nframes = args.flatlamp_min_nframes, 
                          domeflat_min_nframes = args.domeflat_min_nframes, twiflat_min_nframes = args.twiflat_min_nframes, 
                          dark_min_nframes = args.dark_min_nframes, arc_min_nframes = args.arc_min_nframes, contbars_min_nframes = args.contbars_min_nframes)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

# hola :D