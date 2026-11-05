"""Read validated exports; compute indicators from all selected population cells."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd


def load_data(root):
    folder = Path(root) / 'data/app'
    metadata = json.loads((folder / 'app_metadata.json').read_text(encoding='utf-8'))
    for name, expected in metadata['app_files_sha256'].items():
        if Path(name).name != name:
            raise ValueError('Unexpected application file path.')
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Application data checksum mismatch: {name}')
    cells = pd.read_csv(folder / 'population_accessibility.csv.gz',
                        usecols=['cell_id', 'longitude', 'latitude', 'population', 'adm2_pcode', 'distance_km'],
                        dtype={'adm2_pcode': 'string'})
    summary = pd.read_csv(folder / 'district_summary.csv', dtype={'adm2_pcode': 'string'})
    polygons = json.loads((folder / 'districts_display.geojson').read_text(encoding='utf-8'))
    facilities_json = json.loads((folder / 'facilities.geojson').read_text(encoding='utf-8'))
    facilities = pd.DataFrame([f['properties'] for f in facilities_json['features']])
    if not cells.cell_id.is_unique or not summary.adm2_pcode.is_unique:
        raise ValueError('Duplicate application records.')
    if not np.isfinite(cells[['population','distance_km']]).all().all() or not (cells.population > 0).all():
        raise ValueError('Invalid population or distance values.')
    if not np.isclose(cells.population.sum(), metadata['population_denominator'], rtol=1e-10):
        raise ValueError('Population total differs from validated exports.')
    return cells, summary, polygons, facilities, metadata


def select_region(cells, summary, province='All Zimbabwe', district='All districts'):
    selected = summary
    if province != 'All Zimbabwe':
        selected = selected[selected.adm1_name.eq(province)]
    if district != 'All districts':
        selected = selected[selected.adm2_pcode.eq(district)]
    return cells[cells.adm2_pcode.isin(selected.adm2_pcode)], selected.copy()


def indicators(cells, threshold):
    total = float(cells.population.sum())
    if total <= 0:
        return {'population': 0., 'mean_km': None, 'beyond_population': 0., 'beyond_percent': None}
    beyond = float(cells.loc[cells.distance_km.gt(threshold), 'population'].sum())
    return {'population': total, 'mean_km': float(np.average(cells.distance_km, weights=cells.population)),
            'beyond_population': beyond, 'beyond_percent': beyond/total*100}


def district_indicators(cells, selected_summary, threshold):
    result = selected_summary[['adm2_pcode','adm2_name','adm1_name','population_estimate','weighted_mean_distance_km']].copy()
    beyond = cells.loc[cells.distance_km.gt(threshold)].groupby('adm2_pcode').population.sum()
    result['population_beyond_threshold'] = result.adm2_pcode.map(beyond).fillna(0.)
    result['percent_beyond_threshold'] = np.where(result.population_estimate.gt(0), result.population_beyond_threshold / result.population_estimate*100, np.nan)
    return result


def display_features(polygons, district_table):
    rows = district_table.set_index('adm2_pcode')
    output = []
    for feature in polygons['features']:
        code = feature['properties']['adm2_pcode']
        if code not in rows.index:
            continue
        row = rows.loc[code]
        percent = float(row.percent_beyond_threshold)
        if np.isfinite(percent):
            fraction = np.clip(percent/100, 0, 1)
            color = [int(254-100*fraction), int(240-220*fraction), int(217-170*fraction), 200]
            text = f"{row.adm2_name} ({code})\nPopulation beyond threshold: {percent:.1f}%\nWeighted mean distance: {row.weighted_mean_distance_km:.2f} km"
        else:
            color, text = [190,190,190,160], f'{row.adm2_name}: no population denominator'
        output.append({'type':'Feature','tooltip_text':text,'geometry':feature['geometry'],'properties':{'code':code,'fill_color':color,'tooltip_text':text}})
    return {'type':'FeatureCollection','features':output}


def map_view(feature_collection):
    positions=[]
    def collect(coords):
        if len(coords) >= 2 and isinstance(coords[0], (int,float)):
            positions.append(coords[:2])
        else:
            for part in coords:
                collect(part)
    for feature in feature_collection['features']:
        collect(feature['geometry']['coordinates'])
    if not positions:
        return {'longitude':29.8,'latitude':-19.,'zoom':5.7}
    a=np.asarray(positions);lo=a.min(axis=0);hi=a.max(axis=0)
    span=max(float(hi[0]-lo[0]),float(hi[1]-lo[1])*1.4,.05)
    return {'longitude':float((lo[0]+hi[0])/2),'latitude':float((lo[1]+hi[1])/2),'zoom':float(np.clip(np.log2(360/span)-.5,5,12))}
