import json

filepath = 'D:/Projet automobile/vente-auto-platform/Livrables/wakala_architecture_complete_technique.excalidraw'
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, el in enumerate(data['elements']):
    if el['type'] == 'text' and 'budget donné a du sens' in el.get('text', ''):
        print(f'Found text at index {i}')
        print('Text:', el['text'])
        print('Width:', el.get('width'))
        print('ContainerId:', el.get('containerId'))
        # Let's find the yellow rectangle near it
        for j in range(max(0, i-5), min(len(data['elements']), i+5)):
            if data['elements'][j]['type'] == 'rectangle':
                print(f"Rect at {j}: ID={data['elements'][j].get('id')} color={data['elements'][j].get('backgroundColor')}, bound={data['elements'][j].get('boundElements')}")
