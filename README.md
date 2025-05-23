# Scripts to work with KCWI data yipiee #

**Description of scripts:**

### 1 **`obs_table_date`**  
For a given date, prints a table with the observations and/or observations of that day.

 **Arguments:**
- `date`: Date in format `'YYYY-MM-DD'`.

 **Optionals:**
- `--data-type`:Type of data to include in the table:
    - `"both"` → Science and calibrations.
    - `"science"` → Only science.
    - `"calibration"` → Only calibrations.
- `--outpath`: Output directory (by default: `"."`).

 **Usage example:**
obs_table_date 2024-01-01 --data-type both



### 2 **`obs_table_target`**
For a given object with coordinates (RA, DEC) and a tolerance radius in arcseconds, prints a table of all observations registered in that sky region.

 **Arguments:**
- `ra`: RA coordinate value.
- `dec`: DEC coordinate value.

 **Optionals:**
- `--radius`: Tolerance radius in arcsecondss (by default: `30`)
- `--outpath`: Output directory (by default: `"."`).

 **Usage example:**
obs_table_target 260.45 88.71



### 3 **`download_files`**
For a given date, downloads all FITS files from a query to KOA.

 **Arguments:**
- `date`: Date in format `'YYYY-MM-DD'`.
- `filename_type`: type of files you want to download (`all`, `telescope`, `archive`)

 **Optionals:**
- `--output_dir`: Output directory (by default: `"."`).

 **Usage example:**
download_files 2020-05-15 telescope --output_dir ./downloads/



### 4 **`rename_files`**
When downloading files using pykoa, they will be named by their `koaid`. With this script, all files will be copied to a new folder and renamed by their `ofname`, which are in the metadata table.

 **Optional arguments:**
 - `--output_dir`: Directory in which you want to save the new files (by default: `"./renamed_files"`).
 - `--directory`: Directory in which you want to execute the script (by default: `"."`).
 - `--metadata_file`: Table where the names of the files are found (by default: `None` (searchrs for *_filtered.tbl in the directory))

 **Usage example:**
rename_files 



### 5 **`calib_date_finder`**
For a given date and number of days to search, the script will look in anterior and posterior dates to identify missing calibratios. Prints a list of dates in which are those missing calibrations, incuding: bias, domeflats, twilight flats, flatlamps, arclamps, contbars, darks and standard stars.

 **Arguments:**
- `date`: Date in format `'YYYY-MM-DD'`.
- `days_to_check`: Number of days you want to search for (will be always twice of the given number).

- `tolerance_arcsec`: Tolerance radius in arcseconds to find matching standard stars.

 **Optionals**
- `--output_dir`: Output directory (by default: `"."`).

 **Usage example:**
calib_date_finder 2020-05-16 7 5



### 6 **`calib_finder`**
Similar to calib_date_finder, will search missing calibratios in anterior and posterior dates. This one will stop when the minimum number of all calibratios were found. for each one will show the date and name file.

 **Arguments:**
- `date`: Date in format `'YYYY-MM-DD'`.
- `days_to_check`: Number of days you want to search for (will be always twice of the given number).
- `tolerance_arcsec`: Tolerance radius in arcseconds to find matching standard stars

 **Optionals**
- `--max_workers`: Number of threads to use for parallel processing (by default `4`)
- `--summary`: Creates a .txt file of all calibrations found. 
- `--output_dir`: Directorio de salida (by default `"."`).
- `--bias_min_nframes`: number of *bias* frames needed (by default: `7`). 
- `--flatlamp_min_nframes`: number of *flatlamp* frames needed (by default: `6`).
- `--domeflat_min_nframes`: number of *domeflats* frames needed (by default: `3`).
- `--twiflats_min_nframes`: number of *twiflats* frames needed (by default: `1`).
- `--dark_min_nframes`: number of *darks* frames needed (by default: `3`).
- `--arc_min_nframes`: number of *arclapms* frames needed (by default: `1`).
- `--contbars_min_nframes`: number of *contbars* frames needed (by default: `1`).

 **Usage example:**

**Creates a txt file:**    calib_finder 2020-05-16 2 5 --summary

**Doesn't creates a txt file:**    calib_finder 2020-05-16 2 5


 **Notes:**
- All scripts (except for `rename_files`) will do a query to KOA, so they can take some time.
- Metadata files will be created, that's why the output directory is needed.
- If you don't delete the metadata files and use the script for the same date, will take less time, because in not doing again the query (**Except for `download_files` and `rename_files`**).
- **Don't delete 'koa_metadata_{date}_filtered.tbl' before running `rename_files`**.
