"""Additional augment definitions. Engine values use 1,000 fixed-point units."""
U=['Armies','Units']; C=['Settlements']
def fx(path,*props):
 return {'ApplyEffectOnSource':False,'Path':{'PropertyToFollow':path,'Validations':[],'specificTargetType':''},'PropertyEffects':[{'Note':'','TargetProperty':p,'ToTargetOperation':op,'RpnOperationStack':[],'ConstantStack':[{'RawValue':v}],'PropertyLocalName':[]} for p,op,v in props],'IgnorePropertyEffectLoopCheck':False}
def row(code,ko,en,category,kd,ed,*effects):
 return dict(id=code,name_ko=ko,name_en=en,category=category,description_ko=kd,description_en=ed,effects=list(effects))
ADDITIONAL=[
 row('Bulwark','철벽','Bulwark','방어','모든 유닛 고정 피해 감소 +8.','All units: +8 flat damage reduction.',fx(U,('DamageReductionFlat',0,8000))),
 row('Renewal','재생의 샘','Renewal','회복','모든 유닛 체력 재생 +8.','All units: +8 health regeneration.',fx(U,('HealthRegen',0,8000))),
 row('Veteran','백전노장','Veteran','성장','모든 유닛 경험치 획득 배율 +50%p.','All units: +50 percentage points experience gain multiplier.',fx(U,('ExperienceGainMultiplier',0,500))),
 row('Drill','정예 훈련소','Elite Training','성장','모든 정착지에서 생성하는 유닛의 시작 경험치 +100.','All settlements: +100 experience on unit creation.',fx(C,('ExperienceGainOnUnitCreation',0,100000))),
 row('Harmony','태평성대','Harmony','내정','모든 정착지 승인도 획득 +15.','All settlements: +15 approval gain.',fx(C,('ApprovalGain',0,15000))),
 row('Garrison','강철 체력','Iron Constitution','방어','모든 유닛 최대 체력 +60.','All units: +60 maximum health.',fx(U,('HealthPoints',0,60000))),
 row('Armory','중무장','Heavy Armament','전투','모든 유닛 피해 보너스 +20%p, 고정 피해 감소 +4.','All units: +20 percentage points damage bonus and +4 flat damage reduction.',fx(U,('DamageBonusModifier',0,200),('DamageReductionFlat',0,4000))),
 row('FieldMedic','야전 의무대','Field Medics','회복','모든 유닛 최대 체력 +25%, 체력 재생 +4.','All units: +25% maximum health and +4 health regeneration.',fx(U,('HealthPoints',4,250),('HealthRegen',0,4000))),
 row('Countercharge','반격의 포효','Countercharge','전투','모든 유닛 피해 보너스 +20%p, 반격 피해 보너스 +40%p.','All units: +20 percentage points damage bonus and +40 percentage points retaliation damage.',fx(U,('DamageBonusModifier',0,200),('RetaliateDamageModifier',0,400))),
 row('Blitz','전격전','Blitz','기동','모든 유닛 지상 이동력 +1, 피해 보너스 +20%p.','All units: +1 land movement and +20 percentage points damage bonus.',fx(U,('LandSpeed',0,1000),('DamageBonusModifier',0,200))),
 row('SiegeIndustry','공성 공방','Siege Workshops','복합','모든 정착지 산업 +25%, 모든 유닛 피해 보너스 +20%p.','All settlements: +25% industry. All units: +20 percentage points damage bonus.',fx(C,('IndustryGain',4,250)),fx(U,('DamageBonusModifier',0,200))),
 row('SupplyChains','보급의 물결','Supply Chains','복합','모든 정착지 식량 +25%, 모든 유닛 지상 이동력 +1.','All settlements: +25% food. All units: +1 land movement.',fx(C,('FoodGain',4,250)),fx(U,('LandSpeed',0,1000))),
 row('MilitaryAcademy','전쟁 대학','Military Academy','성장','모든 유닛 경험치 획득 배율 +50%p, 모든 정착지의 신규 유닛 시작 경험치 +50.','All units: +50 percentage points experience gain multiplier. All settlements: +50 experience on unit creation.',fx(U,('ExperienceGainMultiplier',0,500)),fx(C,('ExperienceGainOnUnitCreation',0,50000))),
 row('WorkshopSchool','기술 혁명','Technical Revolution','경제','모든 정착지 산업·과학 +25%.','All settlements: +25% industry and science.',fx(C,('IndustryGain',4,250),('ScienceGain',4,250))),
 row('MerchantLeague','상인 연맹','Merchant League','경제','모든 정착지 더스트·영향력 +25%.','All settlements: +25% Dust and influence.',fx(C,('MoneyGain',4,250),('InfluenceGain',4,250))),
 row('Enlightenment','계몽의 시대','Enlightenment','경제','모든 정착지 과학·영향력 +25%.','All settlements: +25% science and influence.',fx(C,('ScienceGain',4,250),('InfluenceGain',4,250))),
 row('Granaries','풍요로운 민심','Full Granaries','내정','모든 정착지 식량 +25%, 승인도 획득 +10.','All settlements: +25% food and +10 approval gain.',fx(C,('FoodGain',4,250),('ApprovalGain',0,10000))),
 row('Commerce','산업 자본','Industrial Capital','경제','모든 정착지 더스트·산업 +25%.','All settlements: +25% Dust and industry.',fx(C,('MoneyGain',4,250),('IndustryGain',4,250))),
 row('WarEconomy','전시 경제','War Economy','복합','모든 정착지 산업 +30%, 모든 유닛 피해 보너스 +15%p.','All settlements: +30% industry. All units: +15 percentage points damage bonus.',fx(C,('IndustryGain',4,300)),fx(U,('DamageBonusModifier',0,150))),
 row('SkilledLabor','숙련된 병기공','Skilled Armorers','성장','모든 정착지 산업 +25%, 신규 유닛 시작 경험치 +75.','All settlements: +25% industry and +75 experience on unit creation.',fx(C,('IndustryGain',4,250),('ExperienceGainOnUnitCreation',0,75000))),
 row('ResearchFunding','황금 연구소','Golden Laboratories','경제','모든 정착지 과학 +30%, 더스트 +20%.','All settlements: +30% science and +20% Dust.',fx(C,('ScienceGain',4,300),('MoneyGain',4,200))),
 row('Rally','국민 총동원','Rally the Nation','복합','모든 정착지 승인도 획득 +15, 모든 유닛 피해 보너스 +15%p.','All settlements: +15 approval gain. All units: +15 percentage points damage bonus.',fx(C,('ApprovalGain',0,15000)),fx(U,('DamageBonusModifier',0,150))),
 row('Expedition','원정의 베테랑','Expedition Veterans','기동','모든 유닛 지상 이동력 +1, 경험치 획득 배율 +50%p.','All units: +1 land movement and +50 percentage points experience gain multiplier.',fx(U,('LandSpeed',0,1000),('ExperienceGainMultiplier',0,500))),
 row('Frontier','개척의 시대','Frontier Age','복합','모든 정착지 식량·산업 +20%, 모든 유닛 시야 +2.','All settlements: +20% food and industry. All units: +2 vision.',fx(C,('FoodGain',4,200),('IndustryGain',4,200)),fx(U,('VisionRange',0,2000))),
]
