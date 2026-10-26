export type Feature = {
  name: string;
  label: string;
  group: string;
  unit: string;
  help: string;
  required: boolean;
  min?: number;
  max?: number;
  typical: number;
  seenMin: number;
  seenMax: number;
};

export const GROUPS = ['Terrain & vegetation', 'Human footprint', 'Building', 'Weather'];

// Order matches the saved model exactly. Ranges come from the training data.
export const FEATURES: Feature[] = [
  { name: 'Aspect', label: 'Aspect', group: 'Terrain & vegetation', unit: 'degrees', help: 'Compass direction the slope faces (-1 = flat)', required: true, min: -1, max: 360, typical: 159, seenMin: -1, seenMax: 359 },
  { name: 'Elevation', label: 'Elevation', group: 'Terrain & vegetation', unit: 'm', help: 'Height above sea level', required: true, min: -100, max: 4500, typical: 517, seenMin: 3, seenMax: 2772 },
  { name: 'Slope', label: 'Slope', group: 'Terrain & vegetation', unit: 'degrees', help: 'Steepness of the terrain', required: true, min: 0, max: 90, typical: 5, seenMin: 0, seenMax: 39 },
  { name: 'TRI', label: 'Terrain ruggedness (TRI)', group: 'Terrain & vegetation', unit: 'index', help: 'Terrain Ruggedness Index', required: true, min: 0, typical: 7.93725, seenMin: 0, seenMax: 68.0368 },
  { name: 'EVH', label: 'Vegetation height (EVH)', group: 'Terrain & vegetation', unit: 'LANDFIRE code', help: 'Existing vegetation height', required: true, min: 0, typical: 22, seenMin: 11, seenMax: 308 },
  { name: 'EVT', label: 'Vegetation type (EVT)', group: 'Terrain & vegetation', unit: 'LANDFIRE code', help: 'Existing vegetation type code', required: true, min: 0, typical: 7299, seenMin: 7008, seenMax: 9829 },
  { name: 'PFTk9', label: 'Fine-to-woody fuel ratio (PFTk9)', group: 'Terrain & vegetation', unit: 'ratio', help: 'Fine fuel vs woody fuel in a 9x9 pixel kernel. May be left empty.', required: false, min: 0, typical: 0.0103395, seenMin: 1.52416e-08, seenMax: 100 },
  { name: 'Frs_Area', label: 'Forest area', group: 'Terrain & vegetation', unit: 'grid share', help: 'Forest area in the 100 m grid', required: true, min: 0, typical: 0.0009, seenMin: 0, seenMax: 0.0729 },
  { name: 'BTF', label: 'Building-to-forest ratio (BTF)', group: 'Terrain & vegetation', unit: 'ratio', help: 'Building to forest area ratio', required: true, min: 0, typical: 0, seenMin: 0, seenMax: 16.7347 },
  { name: 'WUI_Area', label: 'WUI area', group: 'Human footprint', unit: 'km²', help: 'Wildland-urban interface area in the 100 m grid', required: true, min: 0, typical: 0.0872675, seenMin: 0, seenMax: 0.0942673 },
  { name: 'BuildingDensity', label: 'Building density', group: 'Human footprint', unit: 'per m²', help: 'Building footprint density', required: true, min: 0, typical: 0.000381688, seenMin: 0, seenMax: 0.0121 },
  { name: 'RoadLength', label: 'Road length', group: 'Human footprint', unit: 'grid density', help: 'Road length in the 100 m grid', required: true, min: 0, typical: 0.00048325, seenMin: 0, seenMax: 0.00235974 },
  { name: 'CBFR', label: 'Building flammability (CBFR)', group: 'Building', unit: '0 to 10', help: 'Composite Building Flammability Rating; 0 = non-combustible, 10 = highly flammable', required: true, min: 0, max: 10, typical: 4.54974, seenMin: 0, seenMax: 10 },
  { name: 'prcp', label: 'Precipitation', group: 'Weather', unit: 'mm', help: 'Daily precipitation', required: true, min: 0, typical: 0, seenMin: 0, seenMax: 17.2 },
  { name: 'MaxRH', label: 'Max relative humidity', group: 'Weather', unit: '%', help: 'Daily maximum relative humidity', required: true, min: 0, max: 100, typical: 41.1, seenMin: 10.1, seenMax: 100 },
  { name: 'Srad', label: 'Solar radiation', group: 'Weather', unit: 'W/m²', help: 'Daily mean shortwave radiation', required: true, min: 0, typical: 232.2, seenMin: 107.6, seenMax: 375.5 },
  { name: 'tdmean', label: 'Mean dew point temperature', group: 'Weather', unit: '°C', help: 'Lower values mean drier air', required: true, min: -60, max: 40, typical: -0.2786, seenMin: -19.952, seenMax: 17.875 },
  { name: 'WD', label: 'Wind direction (10 m)', group: 'Weather', unit: 'degrees', help: 'Direction the wind comes from', required: true, min: 0, max: 360, typical: 208, seenMin: 1, seenMax: 360 },
  { name: 'Tmax', label: 'Max temperature', group: 'Weather', unit: 'K', help: 'Daily maximum temperature in Kelvin (300 K = 27 °C)', required: true, min: 200, max: 340, typical: 304, seenMin: 278.9, seenMax: 318.5 },
  { name: 'VPD', label: 'Vapor pressure deficit', group: 'Weather', unit: 'kPa', help: 'Atmospheric dryness', required: true, min: 0, typical: 2.31, seenMin: 0.21, seenMax: 5.68 },
  { name: 'WS10m', label: 'Wind speed (10 m)', group: 'Weather', unit: 'm/s', help: 'Near-surface wind speed', required: true, min: 0, typical: 4.5, seenMin: 1.1, seenMax: 14 },
];

// Real record from the held-out test split (label: No damage) for the 'Load sample' button.
export const SAMPLE: Record<string, number> = {
  Aspect: 112.0,
  Elevation: 231.0,
  Slope: 8.0,
  TRI: 14.4913768768311,
  EVH: 25.0,
  EVT: 7299.0,
  WUI_Area: 0.0921951239807312,
  BuildingDensity: 0.0005410368618055,
  BTF: 0.0,
  Frs_Area: 0.0,
  RoadLength: 0.0001007432583719,
  PFTk9: 66.6666641235352,
  CBFR: 2.58128032973231,
  prcp: 0.0,
  MaxRH: 32.0999984741211,
  Srad: 140.699996948242,
  tdmean: -10.95800018,
  WD: 29.0,
  Tmax: 298.100006103516,
  VPD: 1.94000005722046,
  WS10m: 4.40000009536743,
};