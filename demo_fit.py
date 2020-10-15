from datetime import time
from time import sleep

import requests
from funcx.sdk.client import FuncXClient
pyhf_endpoint = 'ae7f555f-07ec-4261-b5f6-d0930ce545a5'

fxc = FuncXClient()


def hello_pyhf(data, doc):
    import pyhf
    w = pyhf.Workspace(data)
    m = w.model(
        patches=[doc],
        modifier_settings={
            "normsys": {"interpcode": "code4"},
            "histosys": {"interpcode": "code4p"},
        }
    )
    d = w.data(m)
    return {
        'CLs_obs': float(pyhf.infer.hypotest(1.0, d, m, qtilde=True))
    }


f = fxc.register_function(hello_pyhf)

data = requests.get('https://gist.githubusercontent.com/lukasheinrich/75b80a2f8bc49e365bfb96e767c8a726/raw/a0946bc7590c76fec2b70de2f6f46208c0545c8d/BkgOnly.json').json()
doc = requests.get('https://gist.githubusercontent.com/lukasheinrich/0bae2f9d6c2667d35cdff31d61092b16/raw/cb45fb6e7f7cdf7432834dd475f1353107602332/patch.json').json()

res = fxc.run(data, doc, endpoint_id=pyhf_endpoint, function_id=f)

result = None

while not result:
    try:
        result = fxc.get_result(res)
    except Exception as e:
        print(e)
        sleep(30)

print("--------------------")
print(result)
