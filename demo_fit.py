import sys
from time import sleep
import json
NUM_RUNS = 10
import requests
from funcx.sdk.client import FuncXClient

pyhf_endpoint = 'ae7f555f-07ec-4261-b5f6-d0930ce545a5'

fxc = FuncXClient()


def prepare_workspace(data):
    import pyhf
    w = pyhf.Workspace(data)
    return w

prepare_func = fxc.register_function(prepare_workspace)


def infer_hypotest(w, metadata, doc):
    import pyhf
    import time

    tick = time.time()
    m = w.model(
        patches=[doc],
        modifier_settings={
            "normsys": {"interpcode": "code4"},
            "histosys": {"interpcode": "code4p"},
        }
    )
    d = w.data(m)
    return {
        'metadata': metadata,
        'CLs_obs': float(pyhf.infer.hypotest(1.0, d, m, qtilde=True)),
        'Fit-Time': time.time() - tick
    }


infer_func = fxc.register_function(infer_hypotest)

data = requests.get('https://gist.githubusercontent.com/lukasheinrich/75b80a2f8bc49e365bfb96e767c8a726/raw/a0946bc7590c76fec2b70de2f6f46208c0545c8d/BkgOnly.json').json()

prepare_task = fxc.run(data, endpoint_id=pyhf_endpoint, function_id=prepare_func)

# While this cooks, let's read in the patch set
patches = None
with open('patchset.json') as f:
    patches = json.load(f)
patch = patches['patches'][0]
name = patch['metadata']['name']

w = None

while not w:
    try:
        w = fxc.get_result(prepare_task)
    except Exception as e:
        print("prepare ", e)
        sleep(30)

print("--------------------")
print(w)

tasks = {}
for i in range(NUM_RUNS):
    patch = patches['patches'][i]
    name = patch['metadata']['name']
    task_id = fxc.run(w, patch['metadata'], patch['patch'], endpoint_id=pyhf_endpoint, function_id=infer_func)
    tasks[name] = {"id": task_id, "result": None}


def count_complete(l):
    return len(list(filter(lambda e: e['result'], l)))


while count_complete(tasks.values()) < NUM_RUNS:
    for task in tasks.keys():
        if not tasks[task]['result']:
            try:
                result = fxc.get_result(tasks[task]['id'])
                print(f"Task {task} complete, there are {count_complete(tasks.values())} results now")
                tasks[task]['result'] = result
            except Exception as e:
                print(e)
                sleep(30)

print("--------------------")
print(tasks.values())
