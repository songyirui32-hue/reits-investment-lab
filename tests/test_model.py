import json
from pathlib import Path
import pytest
from model import calculate, investor_irr

@pytest.fixture
def case():
    return json.loads((Path(__file__).parents[1]/'data/sample_case.json').read_text())

def test_base(case):
    r=calculate(**case)
    assert r['irr']==pytest.approx(0.03627990156371952)
    assert r['max_cost']==pytest.approx(941.0347099643224)
    assert r['flows']==[-1000,40,40,40,40,1020]
    assert r['yields']==[.04]*5

def test_cap(case):
    assert calculate(**{**case,'cap_rate':.07})['irr']<calculate(**case)['irr']

def test_cost(case):
    assert calculate(**{**case,'cost':1100})['irr']<calculate(**case)['irr']

def test_no_double_deduction(case):
    assert calculate(**case)['distributions']==[40]*5

@pytest.mark.parametrize('rate',[0,-.01])
def test_invalid_cap(case,rate):
    with pytest.raises(ValueError): calculate(**{**case,'cap_rate':rate})

def test_no_irr():
    with pytest.raises(ValueError,match='IRR'): investor_irr([-100,0,0])

def test_multiple_changes():
    with pytest.raises(ValueError,match='唯一'): investor_irr([-100,230,-132])

def test_warning(case):
    r=calculate(**{**case,'noi':[0]*5,'exit_noi':0})
    assert r['irr'] is None and 'IRR' in r['warning']

def test_app():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(str(Path(__file__).parents[1]/'app.py')).run(timeout=30)
    assert not app.exception
    assert app.metric[0].value=='3.6280%'
