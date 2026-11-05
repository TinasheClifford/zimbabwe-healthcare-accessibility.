# Zimbabwe Healthcare Accessibility Explorer

**Author: Tinashe Clifford Makandise**

A Python spatial data science project exploring distances between populated grid-cell centres and mapped public-sector healthcare facilities in Zimbabwe. Includes five executed notebooks, validation reports and a Streamlit dashboard with prepared data.

## Open the dashboard on Windows

1. Download the app ZIP and select **Extract All**. Open the extracted `zimbabwe-healthcare-accessibility` folder containing `app.py`.
2. Double-click **setup_windows.bat** once. Let installation complete. Internet is required to install dependencies.
3. Double-click **start_windows.bat**. Keep its command window open.
4. If the browser does not open automatically, visit http://localhost:8501.
5. Select a province/district and adjust the illustrative distance threshold. Explore maps, summaries, sources and downloads.

After restarting your computer, double-click **start_windows.bat** again. Stop the app with Ctrl+C or close its command window. Do not run the ZIP with Streamlit or Python.

The launcher uses `%USERPROFILE%\healthcare-app-env`, outside the long Downloads path, to reduce Windows path-length issues. It assumes `python` points to a working interpreter. Python 3.12 or 3.13 is recommended; the application was tested on Python 3.12. You do not need to activate the environment manually.

### Manual commands

Run each command separately from the extracted project folder:

```bat
python -m venv "%USERPROFILE%\healthcare-app-env"
```
```bat
"%USERPROFILE%\healthcare-app-env\Scripts\python.exe" -m pip install --timeout 120 --retries 10 -r requirements.txt
```
```bat
"%USERPROFILE%\healthcare-app-env\Scripts\python.exe" -m streamlit run app.py
```

On Linux/macOS, create a virtual environment, install requirements.txt and run `python -m streamlit run app.py` using that environment's Python.

## What the dashboard does

- Province and district selection using stable district codes.
- Population-weighted mean distance and population share beyond a 1–30 km illustrative threshold.
- Interactive district shading and facility markers; optional population-centre display sample.
- Selected district summaries and facility inventory downloads.
- National positional sensitivity, source attribution and limitations.

Metrics always use **all selected population cells** and the full prepared facility set. The nearest facility may lie outside the selected district/province. Facility-type filters change map markers only; they do not recompute accessibility. The mapped facility count refers to every inventory facility inside the selected area, regardless of display filters. Districts with zero mapped facilities can still have nearby facilities across the boundary.

The population display sample is limited to 8,000 points for browser performance and is labelled accordingly; it never supplies the calculation denominator. Background map tiles are off by default; the data layers can be explored without a map-tile provider. Optional background tiles need internet access. Browser WebGL is needed for the interactive map.

## Research question

Which populated areas are relatively far from mapped public-sector facilities, and where should geographic accessibility be investigated further?

This is an exploratory historical analysis, not an assessment of current healthcare coverage or a clinical referral system. Distances do not measure road travel, transport availability, staffing, capacity, affordability or quality. The thresholds are project analysis choices, not official standards. No optimal facility-placement recommendations are claimed.

## Data and methods

### Facilities

Maina et al. (2019), *A spatial database of health facilities managed by the public health sector in sub Saharan Africa*, Scientific Data 6:134.

- Study: https://doi.org/10.1038/s41597-019-0142-2
- Dataset: https://doi.org/10.6084/m9.figshare.7725374
- Original workbook: https://ndownloader.figshare.com/files/14379593
- Data record licence: CC0. Cite the study and dataset.

The Zimbabwe subset contains 1,236 source records. The analysis includes 1,201 usable in-country coordinates; 35 records lack coordinates and remain in audit outputs. Providers include government, local authorities and some not-for-profit organisations. This is not a complete present-day register of all public/private providers. Two source-province labels disagree with spatial assignment and remain flagged.

### Population

WorldPop/CIESIN Zimbabwe 2020, approximately 1 km UN-adjusted population counts.

- Product: https://hub.worldpop.org/geodata/summary?id=38911
- Citation DOI: https://doi.org/10.5258/SOTON/WP00671
- Licence: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/

Values are modelled people per native cell, not density. Population is represented at grid-cell centres. The in-country analysis contains 479,031 positive cells and approximately 14,851,844 estimated residents. The national-centre rule excludes approximately 11,083 estimated residents (0.075% of the original raster total), recorded separately in Notebook 2.

### Boundaries

OCHA/HDX Zimbabwe COD-AB: https://data.humdata.org/dataset/cod-ab-zwe. Catalogue licence: CC BY-IGO. Source boundaries date to 2018, with later review metadata. The data contain 91 district reporting polygons, including urban/rural distinctions; this is not interchangeable with every definition of Zimbabwe's district count. Analytical boundaries are retained upstream. The app uses a separate 25 m simplified display copy; its geometry never assigns populations or facilities.

### Distance calculation

Compute WGS84 ellipsoidal geodesic distance from each population-cell centre to the nearest prepared in-country facility. An Earth-centred Cartesian spatial index uses chord distances as lower bounds, then refines all candidate winners with ellipsoidal distances. Facility search crosses district borders but excludes neighbouring countries. Mean distances and threshold shares are weighted by cell population; “beyond” means strictly greater than the threshold.

## Main findings

| Indicator | Result |
|---|---:|
| Population-weighted mean distance | 6.43 km |
| Population-weighted median | 4.94 km |
| Population-weighted 90th percentile | 12.87 km |
| Population beyond 5 km | 49.50% |
| Population beyond 10 km | 18.36% |
| Population beyond 20 km | 2.90% |
| Nearest facility in a different district | 16.31% |

These refer to the historical facility inventory combined with modelled 2020 population and the stated boundary rule. Missing providers, omitted international facilities and source-year differences affect interpretation.

## Validation and sensitivity

Notebook 5 checks 150 targeted/random cells against exhaustive nearest-facility calculations. National and district totals reconcile, and compact export round trips reproduce the results. A conservative within-cell displacement bound produces positional threshold envelopes; these are **not confidence intervals** and do not account for facility omissions or population-model uncertainty. See `reports/final_findings.md` and `reports/05_validation_report.json`.

App checks cover data integrity, indicator consistency, region/threshold controls, empty display filters, and a zero-inventory district. Windows launchers are provided but were not executed on Windows. Browser map rendering must be checked on the target computer; automated tests inspect map data and application controls.

## Project contents and reproduction

- `app.py`: dashboard.
- `src/app_support.py`: loading, integrity checks and indicator calculations.
- `data/app/`: complete compact application inputs. Included; no notebook rerun needed to use the app.
- `notebooks/`: five executed analysis notebooks.
- `outputs/`: maps and summary tables.
- `reports/`: provenance, validation and final findings.
- `requirements.txt`: minimal app dependencies.
- `requirements-dev.txt`: analysis dependencies.
- `.streamlit/config.toml`: appearance and telemetry preference.
- `setup_windows.bat`, `start_windows.bat`: Windows setup and reopening.

This app package omits original raw files and large intermediate analysis outputs. To reproduce the notebooks, copy `data/raw/` from the earlier Stage 1 package into this project, install requirements-dev.txt in an analysis environment, and run Notebooks 1–5 in numerical order. Notebook 2 regenerates prepared datasets; Notebooks 4–5 regenerate application data. Preserve the original filenames and directory structure. Runtime app dependencies do not include GeoPandas, GDAL, Rasterio or SciPy because calculations are precomputed.

## Troubleshooting

- **Path not found:** extract the ZIP first and keep `app.py`, `src/` and `data/app/` together.
- **Module not found:** rerun setup_windows.bat and launch using start_windows.bat.
- **Connection interrupted during setup:** reconnect and rerun setup; cached downloads may be reused.
- **App data cannot load:** restore the entire data/app folder. The app checks export checksums; partial replacements can mismatch metadata.
- **Map blank:** enable browser hardware acceleration/WebGL, try another browser or disable background map tiles. Metrics and downloadable summaries do not depend on map tiles.
- **Python missing or incompatible:** use a working Python 3.12/3.13 installation and create a fresh dedicated environment.

## GitHub and deployment

Upload the extracted project contents, not the ZIP. Keep app.py and requirements.txt at the repository root, alongside src/ and data/app/. Do not omit the compressed population CSV. Create the app with entry point `app.py` and Python 3.12. The cloud app requires only requirements.txt; requirements-dev.txt is for notebook reproduction. Deployment has not been performed for this package.
