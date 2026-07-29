import json, sys
sys.stdout.reconfigure(encoding='utf-8')
f = open(r'wakala_architecture_complete_explique.excalidraw','r',encoding='utf-8')
data = json.load(f)
f.close()

print('type:', data.get('type'))
print('version:', data.get('version'))
print('source:', data.get('source'))

problems = []
for i, e in enumerate(data['elements']):
    if e.get('isDeleted', False):
        continue
    eid = e.get('id','')
    etype = e.get('type','')
    for field in ['id','type','x','y','width','height']:
        if field not in e:
            problems.append(f'Element {i} ({eid}): missing {field}')
    for field in ['x','y','width','height']:
        v = e.get(field)
        if v is not None and not isinstance(v, (int, float)):
            problems.append(f'Element {i} ({eid}): {field} is {type(v).__name__}')
    w = e.get('width', 0)
    h = e.get('height', 0)
    if w < 0:
        problems.append(f'Element {i} ({eid}): negative width {w}')
    if h < 0:
        problems.append(f'Element {i} ({eid}): negative height {h}')
    # Check text elements have text
    if etype == 'text' and 'text' not in e:
        problems.append(f'Element {i} ({eid}): text element missing text')
    # Check arrows have points
    if etype == 'arrow' and 'points' not in e:
        problems.append(f'Element {i} ({eid}): arrow missing points')
    # Check fontFamily is valid
    if etype == 'text':
        ff = e.get('fontFamily')
        if ff not in [1, 2, 3, 4, 5, None]:
            problems.append(f'Element {i} ({eid}): invalid fontFamily {ff}')

if problems:
    print(f'Found {len(problems)} problems:')
    for p in problems:
        print(' ', p)
else:
    print('No structural problems found')

deleted = sum(1 for e in data['elements'] if e.get('isDeleted', False))
active = len(data['elements']) - deleted
print(f'Active: {active}, Deleted: {deleted}, Total: {len(data["elements"])}')

# Check appState
appState = data.get('appState', {})
print('appState keys:', list(appState.keys())[:15])
