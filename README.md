# Scripts para trabajar con datos del KCWI yipiee #

**Descripción de los scripts:**

### 1 **`obs_table_date`**  
Dada una fecha, imprime una tabla con las observaciones y/o calibraciones de esa fecha.  

 **Argumentos:**
- `date`: Fecha en formato `'YYYY-MM-DD'`.

 **Opcionales:**
- `--data-type`: Define qué tipo de datos incluir en la tabla:
    - `"both"` → Ciencia y calibraciones.
    - `"science"` → Solo objetos de ciencia.
    - `"calibration"` → Solo calibraciones.
- `--outpath`: Directorio de salida (por defecto `"."`).

 **Ejemplo de uso:**
obs_table_date 2024-01-01 --data-type both



### 2 **`obs_table_target`**
Dado un objeto con coordenadas (RA, DEC) y un radio de tolerancia en arcosegundos, filtra y muestra en una tabla todas las observaciones registradas dentro de esa región del cielo.

 **Argumentos:**
- `ra`: valor de la coordenada RA
- `dec`: valor de la coordenada DEC

 **Opcionales:**
- `--radius`: Radio de tolerancia en arcosegundos (por defecto: `30`)
- `--outpath`: Directorio de salida (por defecto `"."`).

 **Ejemplo de uso:**
obs_table_target 260.45 88.71



### 3 **`download_files`**
Dada una fecha de observación, descarga los archivos FITS correspondientes desde el KOA.

 **Argumentos:**
- `date`: Fecha en formato `'YYYY-MM-DD'`.
- `filename_type`: tipos de archivos que se quieren descargar (`all`, `telescope`, `archive`)

 **Opcionales:**
- `--output_dir`: Directorio de salida (por defecto `"."`).

 **Ejemplo de uso:**
download_files 2020-05-15 telescope --output_dir ./downloads/



### 4 **`rename_files`**
Al descargar archivos usando pykoa, estos se descargan con el nombre dado por el `koaid`. Mediante este script, a todos los archivos descargados se les cambiará su nombre según su `ofname` correspondiente, el cual se encuentra en la tabla de metadata.

 **Argumento opcional:**
 - `directory`: Directorio en el que quieres que se ejecute este script (por defecto `"."`). 

 **Ejemplo de uso:**
rename_files



### 5 **`calib_date_finder`**
Dado una fecha y un número de días a revisar, este script busca en fechas anteriores y posteriores para identificar calibraciones faltantes. Imprime una lista de las fechas en las que se encuentran dichas calibraciones, incluyendo: bias, domeflats, twilight flats, flatlamps, arclamps, contbars, darks y estrellas estándar.

 **Argumentos:**
- `date`: Fecha en formato `'YYYY-MM-DD'`.
- `days_to_check`: cantidad de días que se quiere revisar (se hará hacia adelante y hacia atrás, si se le da un      valor de 30, revisará un total de 60 días).
- `tolerance_arcsec`: radio de tolerancia, en arcosegundos, para encontrar coincidencias con estrellas estándar.

 **Opcionales:**
- `--output_dir`: Directorio de salida (por defecto `"."`).

 **Ejemplo de uso:**
calib_date_finder 2020-05-16 7 5



### 6 **`calib_finder`**
Similar a calib_date_finder, este script busca calibraciones faltantes en días anteriores y posteriores a una fecha dada. A diferencia del anterior, se detendrá en cuanto encuentre la cantidad mínima requerida de cada calibración. Para cada una, mostrará la fecha y el nombre del archivo correspondiente.

 **Argumentos:**
- `date`: Fecha en formato `'YYYY-MM-DD'`.
- `days_to_check`: cantidad de días que se quiere revisar (se hará hacia adelante y hacia atrás, si se le da un valor de 30, revisará un total de 60 días).
- `tolerance_arcsec`: radio de tolerancia, en arcosegundos, para encontrar coincidencias con estrellas estándar.

 **Opcionales:**
- `--summary`: crea un archivo .txt de todas las calibraciones encontradas. Útil si no quieres solamente tenerlo impreso en la terminal. 
- `--output_dir`: Directorio de salida (por defecto `"."`).
- `--bias_min_nframes`: número de imágenes *bias* necesitadas (por defecto: `7`). 
- `--flatlamp_min_nframes`: número de imágenes *flatlamp* necesitadas (por defecto: `6`).
- `--domeflat_min_nframes`: número de imágenes *domeflats* necesitadas (por defecto: `3`).
- `--twiflats_min_nframes`: número de imágenes *twiflats* necesitadas (por defecto: `1`).
- `--dark_min_nframes`: número de imágenes *darks* necesitadas (por defecto: `3`).
- `--arc_min_nframes`: número de imágenes *arclapms* necesitadas (por defecto: `1`).
- `--contbars_min_nframes`: número de imágenes *contbars* necesitadas (por defecto: `1`).

 **Ejemplos de uso:**

**crea archivo txt:**    calib_finder 2020-05-16 2 5 --summary

**no crea archivo txt:**    calib_finder 2020-05-16 2 5


 **Observaciones:**
- Todos los scripts (menos `rename_files`) realizan una consulta al KOA, por lo que pueden tardarse un poco.
- Se crean archivos de metadata, por esto es necesario el directorio de salida.
- Por lo anterior, si no borras los archivos y ejecutas el script en la misma fecha, demorará considerablemente menos, al no hacer nuevamente el query. (**Excepto por `download_files`**)
- **No borres 'koa_metadata_{date}_filtered.tbl' antes de ejecutar `rename_files`**
