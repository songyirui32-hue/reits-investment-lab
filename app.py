import json
from pathlib import Path
import pandas as pd
import streamlit as st
from model import calculate

st.set_page_config(page_title='REITs Investment Lab', layout='wide')
st.title('REITs Investment Lab')
st.info('模拟数据 · 产权类商业物业 · 单一资产 · 无债务 · 平层权益 · 持有5年')
st.caption('全部权益归投资人，年度末分派100%，无留存、无初始交易费用。金额单位：万元。')
case = json.loads((Path(__file__).parent/'data/sample_case.json').read_text())
with st.form('parameters'):
    cost = st.number_input('初始证券买入成本（万元）', min_value=0.01, value=1000.0)
    table = st.data_editor(pd.DataFrame({'年度':range(1,6), 'NOI':[float(x) for x in case['noi']], '资本开支':[float(x) for x in case['capex']], '其他税费及费用':[float(x) for x in case['expenses']]}), disabled=['年度'], hide_index=True)
    exit_noi = st.number_input('退出次年（第6年）NOI（万元）', min_value=0.0, value=60.0)
    cap = st.number_input('退出 Cap Rate（%）', min_value=0.01, value=6.0)
    fee = st.number_input('退出处置费用率（%）', min_value=0.0, max_value=100.0, value=2.0)
    target = st.number_input('目标 IRR（%）', min_value=-99.0, value=5.0)
    st.form_submit_button('计算收益与估值')
params=dict(cost=cost, noi=table['NOI'].tolist(), capex=table['资本开支'].tolist(), expenses=table['其他税费及费用'].tolist(), exit_noi=exit_noi, cap_rate=cap/100, disposal_rate=fee/100, target_irr=target/100)
try:
    r=calculate(**params)
except (ValueError, TypeError) as exc:
    st.error(str(exc)); st.stop()
if r['warning']: st.warning(r['warning'])
if any(x<0 for x in r['distributions']): st.warning('负可分配现金表示投资人需补足资金，不是负数分红。IRR可能无法唯一确定。')
a,b,c=st.columns(3)
a.metric('投资人 IRR', '无法计算' if r['irr'] is None else f"{r['irr']:.4%}")
b.metric('最高允许总投入', f"{r['max_cost']:,.2f} 万元")
c.metric('退出净回收', f"{r['recovery']:,.2f} 万元")
st.subheader('五年现金流表')
output=table.copy()
output['可供分配现金 / 当年分派']=r['distributions']
output['年度分派率（%）']=[x*100 for x in r['yields']]
output['退出净回收']=[0]*4+[r['recovery']]
output['投资人现金流']=r['flows'][1:]
st.caption(f'第0年投资人现金流：{-cost:,.2f} 万元')
st.dataframe(output, hide_index=True)
st.subheader('退出 Cap Rate 敏感性')
rates=sorted(set([max(0.01,cap+d*0.5) for d in range(-4,5)]+[cap]))
rows=[]
for rate in rates:
    result=calculate(**{**params,'cap_rate':rate/100})
    rows.append({'退出 Cap Rate（%）':rate,'投资人 IRR（%）':None if result['irr'] is None else result['irr']*100})
st.line_chart(pd.DataFrame(rows).set_index('退出 Cap Rate（%）'))
with st.expander('参数解释与计算口径', expanded=True):
    st.markdown('NOI 为物业净经营收益。资本开支、其他税费及费用仅填写尚未在 NOI 中扣除的部分，避免重复扣减。\n\n年度分派 = NOI − 资本开支 − 其他税费及费用；年度分派率 = 年度分派 ÷ 初始成本。\n\n退出资产价值 = 第6年 NOI ÷ 退出 Cap Rate；退出净回收 = 退出资产价值 ×（1 − 处置费用率）。第5年同时收到分派和退出净回收。\n\nIRR 使用第0至5年投资人现金流；最高允许总投入为未来现金流按目标 IRR 折现的现值。模拟模型不包含固定还本付息或担保收益。')
