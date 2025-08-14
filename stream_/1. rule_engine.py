def evaluate_rule(rule, saju_features):
    cond = rule['condition']
    if '재성이 강하면' in cond and saju_features.get('has_gan("재성")'):
        return rule['result']
    return "조건 불충족"
