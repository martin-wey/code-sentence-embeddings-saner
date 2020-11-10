import json

##############################################
# Compute Eclipse content assist R@k and MRR #
##############################################

with open('./test_eclipse/netty_eclipse.json', 'r') as f :
    test = json.load(f)
test = test['proposals']


for i, method in enumerate(test):
    for j, m in enumerate(method['methodInvocation']):
        method['methodInvocation'][j]['proposals'] = sorted(method['methodInvocation'][j]['proposals'])

k_range = [5, 10]
for k in k_range:
    test_size = 0
    score = 0
    sum_reciprocal_rank = 0
    for method in test:
        if len(method['methodInvocation']) > 0:
            for m in method['methodInvocation']:
                true_method = m['name']
                proposals = m['proposals'][:k]
                if true_method in proposals:
                    score += 1
                    sum_reciprocal_rank += 1 / (proposals.index(true_method) + 1)
                test_size += 1

    print('Recall@{} : {}'.format(k, score / test_size))
    print('MRR@{} : {}'.format(k, sum_reciprocal_rank / test_size))
