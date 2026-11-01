"""Derive tiers with optional per-entry overrides of the legacy effect multiplier."""
import copy,re
EFFECT_MULTIPLIER=1.5
TIERS=[dict(id='Silver',label_ko='실버',label_en='Silver',multiplier=1,chance=50,suffix=''),dict(id='Gold',label_ko='골드',label_en='Gold',multiplier=2,chance=35,suffix='_Gold'),dict(id='Prismatic',label_ko='프리즘',label_en='Prismatic',multiplier=3,chance=15,suffix='_Prismatic')]
def scale_text(text,multiplier):
 def scale(m):
  value=float(m.group())*multiplier
  return str(int(value)) if value.is_integer() else str(value)
 return re.sub(r'\d+(?:\.\d+)?',scale,text)
def variants(base):
 result=[]
 for original in base:
  for tier in TIERS:
   effect_multiplier=tier['multiplier']*original.get('effect_multiplier',EFFECT_MULTIPLIER)
   row=copy.deepcopy(original);row['base_id']=original['id'];row['id']=original['id']+tier['suffix'];row['tier']=tier['id'];row['tier_ko']=tier['label_ko'];row['multiplier']=tier['multiplier'];row['draft_chance']=tier['chance']
   for lang in ['ko','en']:
    row['name_'+lang]='['+tier['label_'+lang]+'] '+original['name_'+lang]
    row['description_'+lang]=scale_text(original['description_'+lang],effect_multiplier)
   for effect in row['effects']:
    for prop in effect['PropertyEffects']:
     for constant in prop['ConstantStack']:
      value=constant['RawValue']*effect_multiplier
      assert value.is_integer(), 'Effect must remain exactly representable in fixed-point units'
      constant['RawValue']=int(value)
   result.append(row)
 return result
