import collections,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
V=ROOT/'ModWork'/'Vanilla'
P=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'BepInEx'/'plugins'/'TidefallMayhem'/'Assets'/'TidefallMayhem'
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
vanilla=collections.defaultdict(set)
for f in V.rglob('*.json'):
 try:d=read(f)
 except (ValueError,UnicodeError):continue
 if isinstance(d,dict) and 'AMP_SERIALIZATION_HEADER' in d:vanilla[d['AMP_SERIALIZATION_HEADER']['AssetTypeName']].add(f.stem)
assets={f:read(f) for f in P.rglob('*.json')}
names={f.stem for f,d in assets.items() if 'AMP_SERIALIZATION_HEADER' in d}
loc=read(P/'Localization'/'ko-KR.json');assert set(loc)==set(read(P/'Localization'/'en-US.json'))
refs=[]
def inspect(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='serializableElementName' and x.startswith('TM_'):refs.append(x)
   if k in ['Data','Title','Description','LocalizedName'] and isinstance(x,str) and x.startswith('%TM_'):assert x in loc,x
   inspect(x)
 elif isinstance(v,list):
  for x in v:inspect(x)
for f,d in assets.items():
 if 'AMP_SERIALIZATION_HEADER' not in d:continue
 h=d['AMP_SERIALIZATION_HEADER'];assert h['SourceElementName'] in vanilla[h['AssetTypeName']],f
 inspect(d)
 stack=[];ids=set()
 for i,n in enumerate(d.get('serializationData',{}).get('SerializationNodes',[])):
  if n['Entry']==7:
   stack.append([n['Name'],None,0])
   if '|' in n['Data']:
    ident=n['Data'].split('|')[0];assert ident not in ids,(f,i);ids.add(ident)
  elif n['Entry']==12:assert stack and stack[-1][1] is None;(stack[-1].__setitem__(1,int(n['Data'])))
  elif n['Entry']==13:assert stack and stack[-1][1]==stack[-1][2],(f,i,stack)
  elif n['Entry']==8:
   assert stack,(f,i);stack.pop()
   if stack and stack[-1][1] is not None:stack[-1][2]+=1
  elif stack and stack[-1][1] is not None:stack[-1][2]+=1
 assert not stack,f
for ref in refs:assert ref in names,ref
for phase in ['Start','Tide']:
 c=read(P/'Categories'/f'TM_Category_{phase}.json')
 assert c['IsOptional'] is False and c['RefillPoolWhenEmpty'] is True
 assert c['DeadZoneAffectedByGameSpeed'] is False
 assert c['NumberOfTurnsInDeadZoneAfterTrigger']==(3 if phase=='Tide' else 0)
for f in (P/'Events').glob('*.json'):
 ns=read(f)['serializationData']['SerializationNodes'];fields=collections.defaultdict(list)
 for n in ns:fields[n['Name']].append(n['Data'])
 assert fields['PreventEventRemoval']==['true']
 assert fields['ConsumeEventUponTrigger']==['true']
 assert len(fields['Title'])==(2 if f.stem=='TM_ModeChoice' else 3)
 if f.stem.startswith('TM_Tide_'):
  assert 'TM_ModeEnabled' not in fields['serializableElementName'] and 'TM_Drafted_000' in fields['serializableElementName']
 elif f.stem.startswith('TM_Start_'):assert fields['serializableElementName'].count('TM_Drafted_000')==4
 assert any('SimulationVariableFilterEmpireIsPlayedByAI' in n['Data'] and ns[i+1]['Data']=='true' for i,n in enumerate(ns))
# Repeated three-turn tide signals must yield exactly one draft per tide.
expiry=3;drafts=[]
for turn in range(1,10001):
 if turn%20 in [0,1,2] and turn>=20 and turn>=expiry:
  drafts.append(turn);expiry=turn+3
assert drafts==list(range(20,10001,20))
# Every bit descriptor must represent exactly 2**bit copies of the grant.
for f in (P/'Grants').glob('TM_Grant_*.json'):
 code=f.stem.removeprefix('TM_Grant_');base=read(f)['Effects']
 for bit in range(16):
  actual=read(P/'Stacks'/f'TM_Stack_{code}_{bit:02}.json')['Effects']
  for a,b in zip(actual,base):
   assert a['Path']==b['Path']
   for pa,pb in zip(a['PropertyEffects'],b['PropertyEffects']):
    assert pa['TargetProperty']==pb['TargetProperty'] and pa['ToTargetOperation']==pb['ToTargetOperation']
    assert pa['ConstantStack'][0]['RawValue']==pb['ConstantStack'][0]['RawValue']*(1<<bit)
print(f'PASS: {len(assets)} JSON files, source assets, Odin trees, references, localization, repeat-after-load flags, 500 Tidefalls and all {len(list((P/"Stacks").glob("*.json")))} stack descriptors.')
