"""Generate fictional Excel inputs for the real engine; no lender data is used."""
import datetime as dt
import json
from pathlib import Path
import shutil
import sys
import openpyxl
import yaml

root=Path(sys.argv[1]); root.mkdir(parents=True,exist_ok=True)
varied='--varied' in sys.argv[2:]
config=root/'config'
if not config.exists(): shutil.copytree('/opt/engine-config',config)
headers=['advance_id','merchant_name','principal','factor_rate','lender_rtr','cash_collected',
         'term_start','term_end','last_pmt_date','as_of_date','substatus','pmt_frequency','scheduled_pmt']
originator={'name':'synthetic-demo','display_name':'Fictional MCA Demonstration','channel':'direct',
  'status_map':{'Active':'Active','Paid':'Paid'},'collections_basis':'cash',
  'layouts':[{'name':'synthetic','sheet':'Tape','fingerprint':{'required_headers':headers},
              'columns':{h:h for h in headers}}]}
(config/'originators/mca/synthetic-demo.yaml').write_text(yaml.safe_dump(originator,sort_keys=False))
wb=openpyxl.Workbook(); ws=wb.active; ws.title='Tape'; ws.append(headers)
for n in range(1,7):
    principal=([2500,10000,25000,75000,150000,300000][n-1] if varied else 10000*n)
    factor=1.05+n*0.1 if varied else 1.3
    term_end=dt.datetime(2026,6,1)+dt.timedelta(days=30+40*n) if varied else dt.datetime(2026,12,1)
    ws.append([f'DEMO-{n}',f'Fictional Merchant {n}',principal,factor,principal*factor,principal*0.65,
               dt.datetime(2026,6,1),term_end,dt.datetime(2026,9,1),dt.datetime(2026,9,2),
               'Active','Daily',principal*factor/130])
wb.save(root/'synthetic-tape.xlsx')
print(json.dumps({'tape':str(root/'synthetic-tape.xlsx'),'config':str(config),'fictional':True}))
