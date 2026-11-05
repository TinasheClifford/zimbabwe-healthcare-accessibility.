# Zimbabwe Healthcare Accessibility — Final Analytical Findings
Author: Tinashe Clifford Makandise

## Question and scope
Which populated areas are relatively far from mapped public-sector facilities? Historical facility locations are combined with 2020 modelled population and OCHA reporting boundaries. This is an exploratory mixed-period analysis, not a current healthcare coverage assessment.

## Data and method
The source workbook contains 1,236 Zimbabwe records. Analysis uses 1,201 usable in-country coordinates; 35 missing-coordinate records remain in the audit. Two source-province disagreements remain flagged. Population-cell centres inside the national boundary represent 14,851,844 estimated residents across 479,031 positive cells. The prior boundary-centre exclusion is 11,083 estimated residents (0.075% of the original raster population). Facility search crosses district boundaries but excludes other countries.

Nearest distances use WGS84 ellipsoidal geodesics. Indicators are population-weighted; beyond-threshold means strictly greater than the threshold.

## Main results
- Population-weighted mean distance: 6.43 km.
- Population-weighted median: 4.94 km.
- Population-weighted 90th percentile: 12.87 km.
- Beyond 5 km: 7,351,043 estimated residents (49.50%).
- Beyond 10 km: 2,726,224 estimated residents (18.36%).
- Beyond 20 km: 430,947 estimated residents (2.90%).
- Nearest facility in another district: 16.31% of analysed population.

## Validation and sensitivity
150 targeted/random exhaustive nearest-facility checks passed. Saved cell totals, district means and threshold summaries reconcile, and compressed exports reproduce the original metrics. A conservative 0.931 km within-cell displacement bound gives positional threshold envelopes (see outputs/tables/05_cell_position_sensitivity.csv). These are not statistical confidence intervals and do not include facility omission or population-model uncertainty.

## Use and limitations
The findings identify geographic patterns worth investigating. Facility records should be locally verified before planning decisions. Distances do not measure road travel, transport availability, staffing, affordability, capacity or quality. No official access standards, current operational checks, alternate population-model validation or optimal new-facility recommendations are claimed.

## Sources
- Maina et al. (2019), Scientific Data 6:134: https://doi.org/10.1038/s41597-019-0142-2; data https://doi.org/10.6084/m9.figshare.7725374.
- WorldPop/CIESIN Zimbabwe population product: https://hub.worldpop.org/geodata/summary?id=38911; https://doi.org/10.5258/SOTON/WP00671.
- OCHA/HDX Zimbabwe COD-AB: https://data.humdata.org/dataset/cod-ab-zwe.

## Next deliverable
A Streamlit app using precomputed validated data, source attribution and clearly labelled limitations. The app has not yet been built or deployed.
