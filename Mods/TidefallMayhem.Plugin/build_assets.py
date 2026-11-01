"""Build the runtime package and its Excel-readable augment catalogue together."""
import collections,copy,csv,json,pathlib,random,sys,shutil
from first_turn import items,replace_array,renumber,node,human,descriptor,grant,S,D
from additional_augments import ADDITIONAL
from tiers import TIERS,variants
ROOT=pathlib.Path(__file__).resolve().parents[2]
SOURCE=pathlib.Path(__file__).resolve().parent
OLD=ROOT/'Mods/TidefallMayhem'
OUT=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'BepInEx/plugins/TidefallMayhem/Assets/TidefallMayhem'
def load(p):return json.loads((OLD/p).read_text(encoding='utf-8-sig'))
def write(p,d):
 f=OUT/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
original_codes=['Rage','Titan','March','Vengeance','Harvest','Forge','Insight','Gold','Voice','Scout','Juggernaut','Prosperity']
original_loc={lang:load(pathlib.Path('Localization')/(lang+'.json')) for lang in ['ko-KR','en-US']}
catalog_path=SOURCE/'augments.json'
if catalog_path.exists():catalog=json.loads(catalog_path.read_text(encoding='utf-8-sig'))
else:
 catalog=[]
 for code in original_codes:
  catalog.append(dict(id=code,name_ko=original_loc['ko-KR'][f'%TM_{code}_Title'],name_en=original_loc['en-US'][f'%TM_{code}_Title'],category='combat' if code in ['Rage','Titan','March','Vengeance','Scout','Juggernaut'] else 'economy',description_ko=original_loc['ko-KR'][f'%TM_{code}_Description'].split('\n')[0],description_en=original_loc['en-US'][f'%TM_{code}_Description'].split('\n')[0],effects=load(pathlib.Path('Augments')/f'TM_Augment_000_{code}.json')['Effects']))
 catalog+=ADDITIONAL
 catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
codes=[a['id'] for a in catalog];assert len(codes)==len(set(codes)) and len(codes)%3==0
# Preserve all sixteen original event IDs/offers to avoid changing pending choices.
packs=json.loads((ROOT/'Mods/offers.json').read_text(encoding='utf-8-sig'))
seen={frozenset(pack) for pack in packs};counts=collections.Counter(code for pack in packs for code in pack)
for attempt in range(1000):
 rng=random.Random(400036+attempt);remaining={code:8-counts[code] for code in codes};additional=[];used=set(seen)
 while sum(remaining.values()):
  chosen=[]
  for _ in range(3):
   candidates=[code for code in codes if remaining[code]>0 and code not in chosen]
   if not candidates:break
   code=rng.choices(candidates,weights=[remaining[c] for c in candidates])[0];chosen.append(code)
  if len(chosen)!=3 or frozenset(chosen) in used:break
  additional.append(chosen);used.add(frozenset(chosen))
  for code in chosen:remaining[code]-=1
 if not any(remaining.values()):packs+=additional;break
else:raise RuntimeError('Could not balance offer sets')
base_catalog=catalog
catalog=variants(base_catalog)
codes=[a['id'] for a in catalog]
(SOURCE/'augments-tiered.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base_packs=packs
offers=[(str(pi) if pi>=100 else f'{pi:02}',pack,'Silver') for pi,pack in enumerate(base_packs)]
for tier in TIERS[1:]:
 offers += [(f"{tier['id']}_{pi:02}",[code+tier['suffix'] for code in pack],tier['id']) for pi,pack in enumerate(base_packs)]
loc=copy.deepcopy(original_loc)
for lang in loc:
 for a in catalog:
  loc[lang][f"%TM_{a['id']}_Title"]=a['name_ko' if lang=='ko-KR' else 'name_en']
  suffix='\nPermanent. Stacks with earlier augments.' if lang=='en-US' else '\n'+original_loc[lang]['%TM_Rage_Description'].split('\n',1)[1]
  loc[lang][f"%TM_{a['id']}_Description"]=a['description_ko' if lang=='ko-KR' else 'description_en']+suffix
 for tier in TIERS:
  for phase in ['Start','Tide']:
   loc[lang][f"%TM_{phase}_{tier['id']}_Title"]=original_loc[lang][f'%TM_{phase}_Title']+' ['+tier['label_ko' if lang=='ko-KR' else 'label_en']+']'
 write(pathlib.Path('Localization')/(lang+'.json'),loc[lang])
for phase in ['Start','Tide']:
 c=load(pathlib.Path('Categories')/f'TM_Category_{phase}.json');c.update(RefillPoolWhenEmpty=True,NeedManualTrigger=False)
 write(pathlib.Path('Categories')/f'TM_Category_{phase}.json',c)
write(pathlib.Path('Markers')/'TM_Drafted_000.json',load('Markers/TM_Drafted_000.json'))
mapper_base=load('Mappers/TM_Augment_000_Rage.json')
descriptor_base=load('Augments/TM_Augment_000_Rage.json')
for a in catalog:
 code=a['id'];d=copy.deepcopy(descriptor_base);d['Effects']=a['effects'];write(pathlib.Path('Grants')/f'TM_Grant_{code}.json',d)
 mapper=copy.deepcopy(mapper_base);mapper['LocalizedName']=f'%TM_{code}_Title'
 write(pathlib.Path('Mappers')/f'TM_Grant_{code}.json',mapper)
 for bit in range(16):
  effect=copy.deepcopy(d)
  for e in effect['Effects']:
   for p in e['PropertyEffects']:
    for v in p['ConstantStack']:v['RawValue']*=1<<bit
  name=f'TM_Stack_{code}_{bit:02}'
  write(pathlib.Path('Stacks')/(name+'.json'),effect);write(pathlib.Path('Mappers')/(name+'.json'),mapper)
for offer_id,pack,tier_id in offers:
 d=load('Dialogs/TM_Offer_00.json');ns=d['serializationData']['SerializationNodes']
 replace_array(ns,'LocalizedChoices','System.String[], mscorlib',[[node('',1,f'%TM_{code}_Title')] for code in pack])
 d['serializationData']['SerializationNodes']=renumber(ns);write(pathlib.Path('Dialogs')/f'TM_Offer_{offer_id}.json',d)
 for phase in ['Start','Tide']:
  d=load(pathlib.Path('Events')/f'TM_Event_{0 if phase=="Start" else 1:03}_00.json');ns=d['serializationData']['SerializationNodes']
  for n in ns:
   if n['Name']=='PreventEventRemoval':n['Data']='true'
  conditions=[human(),descriptor('TM_Drafted_000',phase=='Start')]
  replace_array(ns,'Prerequisites',S+'NarrativeEventPrerequisite[]'+D,conditions)
  choices=items(ns,'Choices')
  for choice,code in zip(choices,pack):
   for n in choice:
    if n['Name']=='Title':n['Data']=f'%TM_{code}_Title'
    if n['Name']=='Description':n['Data']=f'%TM_{code}_Description'
   # No confirmation dialog or nested narrative event calls.
   for i,n in enumerate(choice):
    if n['Name']=='ChoiceDialog':choice[i+1]['Data']=''
   augment=grant(f'TM_Grant_{code}')
   for n in augment:
    if n['Name']=='Hidden':n['Data']='false'
   effects=[augment]+([grant('TM_Drafted_000')] if phase=='Start' else [])
   replace_array(choice,'SimulationEventEffects',S+'SimulationEventEffect[]'+D,effects)
  replace_array(ns,'Choices',S+'NarrativeEventChoice[]'+D,choices)
  d['serializationData']['SerializationNodes']=renumber(ns)
  d.update(EventDialog={'serializableElementName':f'TM_Offer_{offer_id}'},Title=f'%TM_{phase}_{tier_id}_Title',Notes='Human-only automatic augment draft. No mode toggle or manual event calls.')
  write(pathlib.Path('Events')/f'TM_{phase}_{offer_id}.json',d)
info=load('mod-info.json');info.update(Version='0.5.0',GameVersion='1.0.197',Description=f'{len(catalog)} permanent augments. Human players only. Automatic first-turn and Tidefall drafts. No mode toggle.')
write(pathlib.Path('mod-info.json'),info)
# Generate the runtime allow-list from the exact same catalogue as the CSV/assets.
cs='using System.Collections.Generic;\nnamespace TidefallMayhem { internal static class AugmentCatalog { internal static readonly string[] Codes = { '+', '.join(json.dumps(code) for code in codes)+' }; } }\n'
(SOURCE/'AugmentCatalog.cs').write_text(cs,encoding='utf-8')
with (SOURCE/'augments.csv').open('w',encoding='utf-8-sig',newline='') as stream:
 writer=csv.writer(stream);writer.writerow(['ID','증강명','분류','효과','등급','영구중첩','기본증강ID','실버대비배율','등급등장확률(%)'])
 for a in catalog:writer.writerow([a['id'],a['name_ko'],a['category'],a['description_ko'],a['tier_ko'],'가능',a['base_id'],a['multiplier'],a['draft_chance']])
shutil.copyfile(SOURCE/'augments.csv',OUT.parent.parent/'augments.csv')
(SOURCE/'offers-expanded.json').write_text(json.dumps(base_packs,indent=2)+'\n',encoding='utf-8')
print(f'Built {len(catalog)} augments, {len(offers)} tiered offers, {len(list(OUT.rglob("*.json")))} assets and UTF-8 CSV.')
