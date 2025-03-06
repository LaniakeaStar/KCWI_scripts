from setuptools import setup, find_packages

setup(
    name="KCWI_scripts",
    version="0.1.0",
    author="Iñaqui Roa Soto",
    author_email="inaqui.roasoto@uc.cl",
    description="Collection of scripts to work with KCWI data.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LaniakeaStar/KCWI_scripts",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "astropy",
        "pykoa",
        "argparse"
    ],

    python_requires='>=3.10.16',
    entry_points={
        "console_scripts": [
            "calib_date_finder=KCWI_scripts.calib_date_finder:main",
            "calib_finder=KCWI_scripts.calib_finder:main",
            "download_files_by_date=KCWI_scripts.download_files_by_date:main",
            "download_files=KCWI_scripts.download_files:main",
            "obs_table_date=KCWI_scripts.obs_table_date:main",
            "obs_table_target=KCWI_scripts.obs_table_target:main",
            "rename_files=KCWI_scripts.rename_files:main",
        ]
    },
)
