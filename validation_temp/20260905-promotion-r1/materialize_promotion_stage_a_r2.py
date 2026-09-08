#!/usr/bin/env python3
from pathlib import Path
src=Path('validation_temp/20260905-promotion-r1/materialize_promotion_stage_a.py')
s=src.read_text(encoding='utf-8')
repls={
"'score':58,'breakdown':{'market_structure_competition':18,'supply_demand_price_utilisation':14,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':8,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4}":"'score':55,'breakdown':{'market_structure_competition':18,'supply_demand_price_utilisation':14,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':8,'systemic_scale':2,'persistence_irreversibility':3,'decision_urgency_actionability':2}",
"'score':57,'breakdown':{'market_structure_competition':17,'supply_demand_price_utilisation':16,'technology_performance_safety':0,'cashflow_asset_value':12,'law_policy_market_access':2,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4}":"'score':55,'breakdown':{'market_structure_competition':19,'supply_demand_price_utilisation':17,'technology_performance_safety':0,'cashflow_asset_value':10,'law_policy_market_access':2,'systemic_scale':2,'persistence_irreversibility':3,'decision_urgency_actionability':2}",
"'score':55,'breakdown':{'market_structure_competition':17,'supply_demand_price_utilisation':17,'technology_performance_safety':0,'cashflow_asset_value':5,'law_policy_market_access':5,'systemic_scale':2,'persistence_irreversibility':5,'decision_urgency_actionability':4}":"'score':55,'breakdown':{'market_structure_competition':19,'supply_demand_price_utilisation':19,'technology_performance_safety':0,'cashflow_asset_value':5,'law_policy_market_access':5,'systemic_scale':2,'persistence_irreversibility':3,'decision_urgency_actionability':2}",
"'score':55,'breakdown':{'market_structure_competition':17,'supply_demand_price_utilisation':18,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':2,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4}":"'score':55,'breakdown':{'market_structure_competition':19,'supply_demand_price_utilisation':19,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':2,'systemic_scale':2,'persistence_irreversibility':3,'decision_urgency_actionability':2}",
}
for old,new in repls.items():
    assert old in s, old
    s=s.replace(old,new,1)
exec(compile(s,str(src)+'[R2_SCORE_CAPS]','exec'),{'__name__':'__main__','__file__':str(src)})
