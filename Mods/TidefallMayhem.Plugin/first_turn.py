"""First-turn mode choice and human-only event prerequisites."""
import copy,json,pathlib
S='Amplitude.Mercury.Data.Simulation.'
D=', Amplitude.Mercury.Data'
REF='Amplitude.Framework.DatatableElementReference, Amplitude.Framework'
def node(name,entry,data=''):return dict(Name=name,Entry=entry,Data=str(data))
def obj(name,typ):
 inline=typ in [REF,S+'NarrativeEventPrerequisite'+D]
 return node(name,7,typ if inline else '0|'+typ)
def ref(name,target):return [obj(name,REF),node('serializableElementName',1,target),node('',8)]
def end(ns,start):
 depth=0
 for i in range(start,len(ns)):
  depth+=(ns[i]['Entry']==7)-(ns[i]['Entry']==8)
  if depth==0:return i+1
 raise ValueError('Unclosed object')
def array(name,typ,items):return [obj(name,typ),node('',12,len(items))]+[n for item in items for n in item]+[node('',13),node('',8)]
def find(ns,name):return next(i for i,n in enumerate(ns) if n['Name']==name)
def replace_array(ns,name,typ,items):
 start=find(ns,name);ns[start:end(ns,start)]=array(name,typ,items)
def items(ns,name):
 i=find(ns,name)+2;result=[]
 while ns[i]['Entry']!=13:
  j=end(ns,i);result.append(copy.deepcopy(ns[i:j]));i=j
 return result
def human():return [obj('',S+'NarrativeEventPrerequisite'+D),node('EntityID',1,'Empire'),obj('Filter',S+'SimulationVariableFilterEmpireIsPlayedByAI'+D),node('IsInverted',5,'true'),node('',8),node('',8)]
def descriptor(name,inverted=False):
 return [obj('',S+'NarrativeEventPrerequisite'+D),node('EntityID',1,'Empire'),obj('Filter',S+'SimulationVariableFilterEntityDescriptor'+D),node('IsInverted',5,str(inverted).lower())]+array('MustHaveOneOfDescriptors','Amplitude.Framework.DatatableElementReference[], Amplitude.Framework',[ref('',name)])+[node('',8),node('',8)]
def effect(kind,tail):
 return [obj('',S+'SimulationEventEffect_'+kind+D),node('SimulationEffectDescriptionOverride',6,''),node('UIMapperOverride',6,''),node('Hidden',5,'true'),node('GainValues',6,''),node('TargetID',1,'Empire')]+tail+[node('',8)]
def grant(name):return effect('ApplyDescriptor',ref('Descriptor',name))
def renumber(ns):
 count=0
 # Reference-type nodes use IDs; inline value types retain their original form.
 for n in ns:
  if n['Entry']==7 and '|' in n['Data'] and n['Data'].split('|',1)[0].isdigit():
   n['Data']=str(count)+'|'+n['Data'].split('|',1)[1];count+=1
 return ns
def configure(out,old):
 def read(p):return json.loads((out/p).read_text(encoding='utf-8-sig'))
 def write(p,d):
  f=out/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for marker in ['TM_ModeChosen','TM_ModeEnabled']:
  write(pathlib.Path('Markers')/(marker+'.json'),read('Markers/TM_Drafted_000.json'))
 # First augment can only be opened by choosing Enable, in the same turn.
 category=read('Categories/TM_Category_Start.json');category['NeedManualTrigger']=True
 write('Categories/TM_Category_Start.json',category)
 for phase in ['Start','Tide']:
  for i in range(16):
   p=pathlib.Path('Events')/f'TM_{phase}_{i:02}.json';d=read(p);ns=d['serializationData']['SerializationNodes']
   conditions=[human(),descriptor('TM_Drafted_000',True)] if phase=='Start' else [human(),descriptor('TM_ModeEnabled'),descriptor('TM_Drafted_000')]
   replace_array(ns,'Prerequisites',S+'NarrativeEventPrerequisite[]'+D,conditions)
   d['serializationData']['SerializationNodes']=renumber(ns);write(p,d)
 # A dedicated mandatory event asks once per human empire/save.
 category=read('Categories/TM_Category_Start.json');category.update(Priority=1001,NeedManualTrigger=False)
 write('Categories/TM_Category_Mode.json',category)
 d=read('Events/TM_Start_00.json');ns=d['serializationData']['SerializationNodes']
 replace_array(ns,'Prerequisites',S+'NarrativeEventPrerequisite[]'+D,[human(),descriptor('TM_ModeChosen',True),descriptor('TM_Drafted_000',True)])
 choices=items(ns,'Choices')[:2]
 for choice,enabled in zip(choices,[True,False]):
  for n in choice:
   if n['Name']=='Title':n['Data']='%TM_Mode_Enable_Title' if enabled else '%TM_Mode_Disable_Title'
   if n['Name']=='Description':n['Data']='%TM_Mode_Enable_Description' if enabled else '%TM_Mode_Disable_Description'
  effects=[grant('TM_ModeChosen')]
  if enabled:effects += [grant('TM_ModeEnabled')]
  replace_array(choice,'SimulationEventEffects',S+'SimulationEventEffect[]'+D,effects)
 replace_array(ns,'Choices',S+'NarrativeEventChoice[]'+D,choices)
 d.update(Category={'serializableElementName':'TM_Category_Mode'},EventDialog={'serializableElementName':'TM_ModeDialog'},Title='%TM_Mode_Title',Description='%TM_Mode_Description',Notes='One saved opt-in choice, human players only. Enable immediately opens the first augment draft.')
 d['serializationData']['SerializationNodes']=renumber(ns);write('Events/TM_ModeChoice.json',d)
 dialog=read('Dialogs/TM_Offer_00.json');ns=dialog['serializationData']['SerializationNodes']
 for n in ns:
  if n['Name']=='LocalizationKey':n['Data']='%TM_Mode_Description'
 replace_array(ns,'LocalizedChoices','System.String[], mscorlib',[[node('',1,'%TM_Mode_Enable_Title')],[node('',1,'%TM_Mode_Disable_Title')]])
 dialog['serializationData']['SerializationNodes']=renumber(ns);write('Dialogs/TM_ModeDialog.json',dialog)
 for lang in ['ko-KR','en-US']:
  ko=lang=='ko-KR';p=pathlib.Path('Localization')/(lang+'.json');loc=read(p)
  loc.update({'%TM_Mode_Title':'아수라장 증강을 켤까요?' if ko else 'Enable Mayhem augments?',
   '%TM_Mode_Description':'이번 게임에서 증강 모드를 사용할지 선택하세요. 켜면 지금 첫 증강을 고르고, 이후 매 Tidefall마다 추가 증강을 고릅니다. 증강은 플레이어만 받으며 AI에는 적용되지 않습니다. 선택은 이 세이브에 저장됩니다.' if ko else 'Choose whether to use augments in this game. Enable to choose your first augment now and another at each Tidefall. Only human players receive augments. This choice is saved with your game.',
   '%TM_Mode_Enable_Title':'증강 켜기' if ko else 'Enable augments',
   '%TM_Mode_Enable_Description':'지금 첫 증강을 선택합니다. 이후 매 Tidefall마다 플레이어에게 영구 증강을 추가합니다.' if ko else 'Choose your first augment now, then gain another permanent augment each Tidefall. Human players only.',
   '%TM_Mode_Disable_Title':'증강 끄기' if ko else 'Disable augments',
   '%TM_Mode_Disable_Description':'이번 게임은 증강 없이 진행합니다. 이 세이브에서는 다시 묻지 않습니다.' if ko else 'Play this game without augments. You will not be asked again in this save.'})
  write(p,loc)
