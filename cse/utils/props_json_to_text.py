import json

name = 'twitter4j'
with open(f'../test_eclipse/{name}_eclipse.json', 'r') as f:
    test = json.load(f)
test = test['proposals']

for i, method in enumerate(test):
    for j, m in enumerate(method['methodInvocation']):
        method['methodInvocation'][j]['proposals'] = sorted(method['methodInvocation'][j]['proposals'])

sequences = []
proposals = []

for method in test:
    if len(method['methodInvocation']) > 0:
        current_sequences = [method['methodDeclarationName']]

        for i, m in enumerate(method['methodInvocation']):
            function_proposals = m['proposals']
            current_sequences.append(m['name'])

            if len(function_proposals) > 0:
                proposals.append(' '.join(function_proposals))
                sequences.append(' '.join(current_sequences))

assert len(sequences) == len(proposals)


with open(f'../test_eclipse/{name}_sequences.txt', 'w+') as f:
    for seq in sequences:
        f.write(seq)
        f.write('\n')

with open(f'../test_eclipse/{name}_proposals.txt', 'w+') as f:
    for prop in proposals:
        f.write(prop)
        f.write('\n')
