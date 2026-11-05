"""Zimbabwe Healthcare Accessibility Explorer — Tinashe Clifford Makandise."""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from src.app_support import load_data, select_region, indicators, district_indicators, display_features, map_view

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Zimbabwe Healthcare Accessibility',page_icon='🌍',layout='wide')

@st.cache_data(show_spinner='Loading validated geographic data…')
def cached_data():
    return load_data(ROOT)

st.caption('SPATIAL DATA SCIENCE · TINASHE CLIFFORD MAKANDISE')
st.title('Zimbabwe Healthcare Accessibility Explorer')
st.write('Explore geographic proximity to mapped public-sector healthcare facilities.')
st.info('Historical facility inventory + 2020 modelled population. Distances are straight-line geographic distances, not travel times or current healthcare coverage.')
try:
    cells,summary,polygons,facilities,metadata=cached_data()
except Exception:
    st.error('The application data could not be loaded. Keep the complete data/app folder from the package. If rebuilding, run Notebooks 1–5 in order. See README.md.')
    st.stop()

with st.sidebar:
    st.header('Explore an area')
    province=st.selectbox('Province',['All Zimbabwe']+sorted(summary.adm1_name.unique()),key='province')
    options=summary if province=='All Zimbabwe' else summary[summary.adm1_name.eq(province)]
    labels=options.set_index('adm2_pcode').district_label.to_dict()
    district=st.selectbox('District',['All districts']+options.sort_values(['adm2_name','adm2_pcode']).adm2_pcode.tolist(),
                          format_func=lambda code: labels.get(code,code),key='district')
    threshold=st.slider('Illustrative distance threshold (km)',1,30,10,key='threshold')
    st.caption('Beyond means strictly greater than the selected threshold. These are not official access standards.')
    st.divider()
    st.subheader('Map display')
    show_facilities=st.checkbox('Show facilities',value=True)
    context=st.checkbox('Include facilities outside the selected area',value=True)
    facility_types=st.multiselect('Facility types shown on map',sorted(facilities.facility_type.unique()),default=sorted(facilities.facility_type.unique()),key='types')
    show_population=st.checkbox('Show population-centre distance sample',value=False)
    basemap=st.checkbox('Show background map tiles',value=False)
    st.caption('Facility display filters do not change distances or indicators. Calculations use the complete mapped inventory.')

selected_cells,selected_summary=select_region(cells,summary,province,district)
region_name=labels[district] if district!='All districts' else province
stats=indicators(selected_cells,threshold)
table=district_indicators(selected_cells,selected_summary,threshold)
region_facilities=facilities[facilities.adm2_pcode.isin(selected_summary.adm2_pcode)]
st.subheader(region_name)
columns=st.columns(4)
columns[0].metric('Estimated population',f"{stats['population']:,.0f}")
columns[1].metric('Weighted mean distance',f"{stats['mean_km']:.2f} km" if stats['mean_km'] is not None else 'N/A')
columns[2].metric(f'Population beyond {threshold} km',f"{stats['beyond_percent']:.2f}%" if stats['beyond_percent'] is not None else 'N/A')
columns[3].metric('Mapped facilities in area',f'{len(region_facilities):,}')
st.caption(f"Approximately {stats['beyond_population']:,.0f} estimated residents beyond the selected threshold. Indicators use all {len(selected_cells):,} selected population cells; the nearest facility may be outside the selected area.")

map_tab,table_tab,method_tab=st.tabs(['Map and distribution','District summaries','Methods and limitations'])
with map_tab:
    features=display_features(polygons,table)
    layers=[pdk.Layer('GeoJsonLayer',features,filled=True,stroked=True,get_fill_color='properties.fill_color',get_line_color=[85,100,120],line_width_min_pixels=1,pickable=True)]
    visible=facilities if context else region_facilities
    visible=visible[visible.facility_type.isin(facility_types)].copy()
    if show_facilities and len(visible):
        visible['tooltip_text']=visible.facility_name+'\n'+visible.facility_type+'\n'+visible.adm2_name.fillna('Unassigned district')
        layers.append(pdk.Layer('ScatterplotLayer',visible[['longitude','latitude','tooltip_text']],get_position='[longitude, latitude]',get_radius=250,radius_min_pixels=3,get_fill_color=[29,78,216,220],pickable=True))
    if show_population and len(selected_cells):
        points=selected_cells.sample(n=min(8000,len(selected_cells)),random_state=42).copy()
        points['color']=points.distance_km.map(lambda d:[190,35,35,180] if d>threshold else [15,118,110,150])
        points['tooltip_text']=points.apply(lambda row:f"Population-cell centre\nDistance: {row.distance_km:.2f} km\nEstimated cell population: {row.population:,.1f}",axis=1)
        layers.append(pdk.Layer('ScatterplotLayer',points[['longitude','latitude','color','tooltip_text']],get_position='[longitude, latitude]',get_radius=180,radius_min_pixels=2,get_fill_color='color',pickable=True))
        st.caption(f'Map shows {len(points):,} of {len(selected_cells):,} population centres sampled for display only. Red: beyond threshold; teal: within. Metrics use every selected cell.')
    deck=pdk.Deck(layers=layers,initial_view_state=pdk.ViewState(**map_view(features)),map_style='light' if basemap else None,
                  map_provider='carto' if basemap else None,tooltip={'text':'{tooltip_text}'},height=560)
    st.pydeck_chart(deck,height=560)
    st.caption('District shading: pale = lower population share beyond threshold; dark red = higher share (0–100%). Blue markers = mapped facilities. Borders are simplified for display only.')
    if show_facilities and not len(visible):
        st.caption('No facility markers match the selected display filters; accessibility metrics are unchanged.')
    bands=pd.cut(selected_cells.distance_km,[-np.inf,5,10,20,np.inf],labels=['0–5 km','>5–10 km','>10–20 km','>20 km'])
    distribution=selected_cells.groupby(bands,observed=False).population.sum().rename('Estimated population')
    st.write('**Population by fixed distance band**')
    st.bar_chart(distribution,color='#2563EB')
    st.caption('Fixed 5/10/20 km bands provide comparison; they do not move with the threshold slider.')
with table_tab:
    st.write(f'**District indicators at the selected {threshold} km threshold**')
    ordered=table.sort_values(['percent_beyond_threshold','adm2_pcode'],ascending=[False,True])
    st.dataframe(ordered,hide_index=True,width='stretch')
    st.download_button('Download selected district summary (CSV)',ordered.to_csv(index=False).encode('utf-8'),file_name=f'healthcare_district_summary_{threshold}km.csv',mime='text/csv')
    st.download_button('Download facility inventory for selected area (CSV)',region_facilities.to_csv(index=False).encode('utf-8'),file_name='mapped_facilities_selected_area.csv',mime='text/csv')
    st.caption('Inventory download includes every mapped facility in the selected area, regardless of map-display type filters. Counts are not capacity-adjusted.')
with method_tab:
    st.write('**How the analysis works**')
    st.write('Population counts are assigned to native grid-cell centres. Each centre is matched to the nearest prepared in-country facility using WGS84 ellipsoidal geodesic distance. Results are weighted by estimated residents. District borders do not constrain facility choice.')
    for limitation in metadata['limitations']:
        st.write('• '+limitation)
    st.write('35 source facility records lacked coordinates and remain outside mapped calculations; two province disagreements are flagged in the analysis. The facility compilation includes government, local-authority and some not-for-profit providers.')
    st.write('**Validation**')
    st.write(f"{metadata['validation']['exhaustive_sample_cells']} exhaustive nearest-facility checks passed, together with population reconciliation and export checks. These checks validate computation, not real-world service completeness.")
    sensitivity=pd.read_csv(ROOT/'data/app/position_sensitivity.csv')
    st.write('**National within-cell positional sensitivity**')
    st.dataframe(sensitivity,hide_index=True,width='stretch')
    st.caption('National results, regardless of area selection. These conservative positional envelopes are not confidence intervals and exclude facility omission and population-model uncertainty.')
    for source in metadata['sources']:
        st.markdown(f"[{source['name']}]({source['url']}) — {source['license']}")
    report=ROOT/'reports/final_findings.md'
    if report.is_file():
        st.download_button('Download final analytical findings',report.read_bytes(),file_name='healthcare_accessibility_findings.md',mime='text/markdown')
    st.caption('This tool supports exploration and further investigation. It is not a clinical referral service or an optimal facility-placement model.')
