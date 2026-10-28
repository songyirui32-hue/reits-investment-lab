"""五年、无杠杆、年度末现金流；金额单位万元。"""
import math
import numpy_financial as nf


def investor_irr(flows):
    if not all(math.isfinite(x) for x in flows):
        raise ValueError('现金流必须为有限数值')
    signs = [1 if x > 0 else -1 for x in flows if x != 0]
    if not signs or sum(a != b for a, b in zip(signs, signs[1:])) != 1:
        raise ValueError('IRR无法唯一计算：现金流需恰好发生一次正负号变化')
    result = float(nf.irr(flows))
    if not math.isfinite(result):
        raise ValueError('现金流无法计算IRR')
    return result


def calculate(cost, noi, capex, expenses, exit_noi, cap_rate, disposal_rate, target_irr):
    if any(len(x) != 5 for x in (noi, capex, expenses)):
        raise ValueError('必须输入五年的经营数据')
    values = [cost, *noi, *capex, *expenses, exit_noi, cap_rate, disposal_rate, target_irr]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('输入必须为有限数值')
    if cost <= 0 or cap_rate <= 0 or target_irr <= -1:
        raise ValueError('买入成本及Cap Rate必须大于零，目标IRR必须大于-100%')
    if not 0 <= disposal_rate <= 1 or any(x < 0 for x in [*capex, *expenses, exit_noi]):
        raise ValueError('费用与退出NOI不得为负，处置费用率必须在0%至100%之间')
    distributions = [n-c-e for n,c,e in zip(noi,capex,expenses)]
    exit_value = exit_noi / cap_rate
    recovery = exit_value * (1-disposal_rate)
    flows = [-cost, *distributions]
    flows[-1] += recovery
    try:
        irr, warning = investor_irr(flows), None
    except ValueError as exc:
        irr, warning = None, str(exc)
    return dict(distributions=distributions, yields=[x/cost for x in distributions],
                exit_value=exit_value, recovery=recovery, flows=flows, irr=irr, warning=warning,
                max_cost=sum(c/(1+target_irr)**t for t,c in enumerate(flows) if t))
