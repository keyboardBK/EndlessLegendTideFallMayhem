import collections,csv,json,pathlib,re,sys
from tiers import TIERS,EFFECT_MULTIPLIER,scale_text
ROOT=pathlib.Path(__file__).resolve().parents[2];SRC=pathlib.Path(__file__).parent
P=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'BepInEx/plugins/TidefallMayhem/Assets/TidefallMayhem'
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
base=read(SRC/'augments.json');variants=read(SRC/'augments-tiered.json');bybase={a['id']:a for a in base};codes={a['id'] for a in variants}
assert len(base)==36 and len(variants)==len(codes)==108
with (SRC/'augments.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f))
assert len(rows)==109 and (SRC/'augments.csv').read_bytes().startswith(b'\xef\xbb\xbf')
assert set(re.findall(r'"([A-Za-z_]+)"',(SRC/'AugmentCatalog.cs').read_text()))==codes
counts=collections.Counter(a['tier'] for a in variants);assert counts==dict(Silver=36,Gold=36,Prismatic=36)
for row,a in zip(rows[1:],variants):
 b=bybase[a['base_id']];effect_multiplier=b.get('effect_multiplier',EFFECT_MULTIPLIER);assert row[:4]==[a['id'],a['name_ko'],a['category'],a['description_ko']]
 assert row[4]==a['tier_ko'] and row[6:]==[a['base_id'],str(a['multiplier']),str(a['draft_chance'])]
 assert '?' not in row[1] and '?' not in row[3]
 grant=read(P/'Grants'/f"TM_Grant_{a['id']}.json")
 assert grant['Effects']==a['effects']
 for e,original in zip(a['effects'],b['effects']):
  assert e['Path']==original['Path']
  for prop,orig in zip(e['PropertyEffects'],original['PropertyEffects']):
   assert prop['TargetProperty']==orig['TargetProperty'] and prop['ToTargetOperation']==orig['ToTargetOperation']
   for actual,expected in zip(prop['ConstantStack'],orig['ConstantStack']):
    assert type(actual['RawValue']) is int
    assert actual['RawValue']==expected['RawValue']*a['multiplier']*effect_multiplier
 for language in ['ko','en']:
  assert a['description_'+language]==scale_text(b['description_'+language],a['multiplier']*effect_multiplier)
 if a['tier']=='Silver':assert a['id']==b['id']
 for lang in ['ko-KR','en-US']:
  loc=read(P/'Localization'/f'{lang}.json');assert loc[f"%TM_{a['id']}_Title"]==a['name_ko' if lang=='ko-KR' else 'name_en']
  assert loc[f"%TM_{a['id']}_Description"].split('\n')[0]==a['description_ko' if lang=='ko-KR' else 'description_en']
basepacks=read(SRC/'offers-expanded.json');old=read(ROOT/'Mods/offers.json');assert basepacks[:16]==old
assert len({frozenset(p) for p in basepacks})==len(basepacks)==96
for phase in ['Start','Tide']:
 observed=collections.Counter();rarities=collections.Counter()
 for f in (P/'Events').glob(f'TM_{phase}_*.json'):
  d=read(f);ns=d['serializationData']['SerializationNodes'];chosen=[n['Data'][4:-6] for n in ns if n['Name']=='Title']
  assert len(chosen)==len(set(chosen))==3 and all(c in codes for c in chosen)
  tiers={next(a['tier'] for a in variants if a['id']==c) for c in chosen};assert len(tiers)==1
  tier=tiers.pop();rarities[tier]+=1;observed.update(chosen)
  assert d['Title']==f'%TM_{phase}_{tier}_Title'
 assert rarities==dict(Silver=96,Gold=96,Prismatic=96)
 assert set(observed)==codes and set(observed.values())=={8}
assert (SRC/'augments.csv').read_bytes()==(P.parent.parent/'augments.csv').read_bytes()
print('PASS: all 108 augments, per-entry balance multipliers, tier ratios 1/2/3, CSV copies, localized descriptions and balanced candidate pools match runtime effects.')
