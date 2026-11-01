import json,pathlib,sys
from first_turn import items
P=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[2]/'BepInEx/plugins/TidefallMayhem/Assets/TidefallMayhem'
def read(p):return json.loads((P/p).read_text(encoding='utf-8-sig'))
def nodes(d):return d['serializationData']['SerializationNodes']
def values(ns,key):return [n['Data'] for n in ns if n['Name']==key]
def allowed(event,markers,ai=False):
 for block in items(nodes(event),'Prerequisites'):
  inverted=values(block,'IsInverted')==['true']
  found=ai if any('SimulationVariableFilterEmpireIsPlayedByAI' in n['Data'] for n in block) else any(v in markers for v in values(block,'serializableElementName'))
  if found==inverted:return False
 return True
assert not (P/'Events/TM_ModeChoice.json').exists()
assert not (P/'Dialogs/TM_ModeDialog.json').exists()
assert not (P/'Categories/TM_Category_Mode.json').exists()
for phase in ['Start','Tide']:assert read(pathlib.Path('Categories')/f'TM_Category_{phase}.json')['NeedManualTrigger'] is False
start=[read(f.relative_to(P)) for f in sorted((P/'Events').glob('TM_Start_*.json'))]
tide=[read(f.relative_to(P)) for f in sorted((P/'Events').glob('TM_Tide_*.json'))]
for event in start+tide:
 for n in nodes(event):
  assert 'SimulationEventEffect_TriggerNarrativeEvent' not in n['Data'], 'Nested trigger regression'
  assert n['Data'] not in ['TM_ModeChosen','TM_ModeEnabled'], 'Old mode gate'
 assert not allowed(event,set(),True)
 assert not allowed(event,{'TM_Drafted_000'},True)
for event in start:
 assert allowed(event,set()) and allowed(event,{'TM_ModeChosen'})
 for choice in items(nodes(event),'Choices'):
  markers=set()
  for effect in items(choice,'SimulationEventEffects'):markers.update(values(effect,'serializableElementName'))
  assert 'TM_Drafted_000' in markers
  restored=set(json.loads(json.dumps(list(markers))))
  assert not any(allowed(e,restored) for e in start)
  assert all(allowed(e,restored) for e in tide)
  assert not any(allowed(e,restored,True) for e in tide)
plugin=(pathlib.Path(__file__).parent/'Plugin.cs').read_text(encoding='utf-8-sig')
assert 'SnapshotValidationVariables' not in plugin and 'OpenFirstDraftAfterChoice' not in plugin
print(f'PASS: no toggle UI or recursive trigger; {len(start)*3} initial-choice paths; saved progression; AI excluded.')
