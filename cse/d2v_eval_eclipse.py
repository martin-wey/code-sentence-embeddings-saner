import argparse
import json
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model_path', type=str, help='Path to the trained word2vec model.')
    parser.add_argument('-t', '--train_set', type=str, help='Path to the training set (json format).')
    parser.add_argument('-e', '--test_set', type=str, help='Path to the test set (json format).')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    print('Loading doc2vec model ...')
    model = Doc2Vec.load(args.model_path)
    print('Loading training set ...')
    with open(args.train_set, 'r') as f:
        train_docs = json.load(f)
    train_set = [TaggedDocument(sent, [i]) for i, sent in enumerate(train_docs)]
    print('Loading test set ...')
    with open(args.test_set, 'r') as f:
        test_set = json.load(f)
    test_set = test_set['proposals']

    topk_range = [5, 10]
    for k in topk_range:
        test_size = 0
        score = 0
        sum_reciprocal_rank = 0
        for method in test_set:
            if len(method['methodInvocation']) > 0:
                context = [method['methodDeclarationName']]
                for i, m in enumerate(method['methodInvocation']):
                    current_method_name = m['name']
                    method_proposals = m['proposals']

                    # Check that Eclipse proposals are not empty otherwise
                    # we cannot build a suggestion list
                    if len(method_proposals) > 0:
                        inferred_vector = model.infer_vector(context)
                        sims_topn = model.docvecs.most_similar([inferred_vector], topn=1000)
                        sims_topn_index = list(map(lambda x: x[0], sims_topn))

                        suggestions = []
                        for i, idx in enumerate(sims_topn_index):
                            word_list = train_set[idx].words
                            for word in word_list:
                                if word not in suggestions and word in method_proposals and len(suggestions) < k:
                                    suggestions.append(word)
                        if current_method_name in suggestions:
                            score += 1
                            sum_reciprocal_rank += 1 / (suggestions.index(current_method_name) + 1)
                        test_size += 1
                    context.append(current_method_name)
        print('Precision@{} : {}'.format(k, score / test_size))
        print('MRR@{} : {}'.format(k, sum_reciprocal_rank / test_size))
        print('Test size : {}'.format(test_size))


