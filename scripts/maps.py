import json, tempfile, urllib.request, zipfile, io
from pathlib import Path
import shapefile
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
layers=[]
NE='https://naturalearth.s3.amazonaws.com/'
def load(url,kind,tol,select=lambda a:True,crs=None,group=None):
 print(url,flush=True)
 with tempfile.TemporaryDirectory() as d:
  with urllib.request.urlopen(url,timeout=180) as r: data=r.read()
  zipfile.ZipFile(io.BytesIO(data)).extractall(d)
  f=next(Path(d).rglob('*.shp')); reader=shapefile.Reader(str(f),encodingErrors='replace'); buckets={}
  for rec in reader.iterShapeRecords():
   a=rec.record.as_dict()
   if not select(a):continue
   geom=shape(rec.shape.__geo_interface__)
   if crs:geom=transform(Transformer.from_crs(crs,4326,always_xy=True).transform,geom)
   geom=geom.simplify(tol,preserve_topology=True)
   if geom.is_empty:continue
   lines=[]
   def walk(g):
    if g.geom_type=='Polygon':walk(g.exterior);[walk(x) for x in g.interiors]
    elif g.geom_type in ('LineString','LinearRing'):lines.append([[round(x,5),round(y,5)] for x,y,*_ in g.coords])
    elif hasattr(g,'geoms'):[walk(x) for x in g.geoms]
   walk(geom)
   if lines:buckets.setdefault(group(a) if group else kind,[]).append({'b':list(geom.bounds),'l':lines})
  for name,features in buckets.items():layers.append({'kind':kind,'name':name,'features':features})
load(NE+'50m_physical/ne_50m_land.zip','land',.025)
load(NE+'50m_cultural/ne_50m_admin_0_boundary_lines_land.zip','boundary',.015)
load(NE+'50m_cultural/ne_50m_admin_1_states_provinces.zip','boundary',.015,lambda a:a.get('admin') in ('United States of America','Canada'))
load(NE+'10m_physical/ne_10m_lakes.zip','lake',.008)
load(NE+'10m_physical/ne_10m_rivers_lake_centerlines.zip','water',.008)
states={'42':'PA','36':'NY','39':'OH','54':'WV','24':'MD','34':'NJ','10':'DE','51':'VA','18':'IN','26':'MI','17':'IL','55':'WI','27':'MN','50':'VT','25':'MA','23':'ME','09':'CT','33':'NH'}
for typ in ('county','cousub'):
 load(f'https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_{typ}_500k.zip','detail',.003,lambda a:a.get('STATEFP') in states,group=lambda a:states[a['STATEFP']]+'-'+typ)
for typ in ('cd','csd'):
 load(f'https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/l{typ}_000b21a_e.zip','detail',.003,lambda a:str(a.get('PRUID')) in ('24','35'),crs=3347,group=lambda a:('QC' if str(a['PRUID'])=='24' else 'ON')+'-'+typ)
assert all(any(x['name'].startswith(st+'-') for x in layers) for st in list(states.values())+['ON','QC'])
Path('app/src/main/assets/offline-map.json').write_text(json.dumps(layers,separators=(',',':')))
