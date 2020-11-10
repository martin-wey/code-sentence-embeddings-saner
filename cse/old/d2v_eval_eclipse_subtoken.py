import argparse
import json
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from utils import nlp_utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model_path', type=str, help='Path to the trained word2vec model.')
    parser.add_argument('-t', '--train_set', type=str, help='Path to the training set (json format).')
    parser.add_argument('-e', '--test_set', type=str, help='Path to the test set (json format).')
    parser.add_argument('-o', '--output', type=str, help='Path to the results output file.')
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
    print('Initialize tokenizers ...\n')
    tokenizer_us = nlp_utils.initialize_nlp('en_core_web_sm')
    tokenizer_us = nlp_utils.initialize_tokenizer(tokenizer_us, 'underscore')
    tokenizer_camel = nlp_utils.initialize_nlp('en_core_web_sm')
    tokenizer_camel = nlp_utils.initialize_tokenizer(tokenizer_camel, 'camel')

    topk_range = [5, 10]
    open(args.output, 'a+').close()
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

                    print('Method to predict : {}'.format(current_method_name))
                    print('Eclipse proposals : {}'.format(method_proposals))
                    # Check that Eclipse proposals are not empty otherwise
                    # we cannot build a suggestion list
                    if len(method_proposals) > 0:
                        context_subtoken = nlp_utils.tokenize_list(tokenizer_us, context)
                        context_subtoken = nlp_utils.tokenize_list(tokenizer_camel, context_subtoken, lower=True)
                        context_subtoken = nlp_utils.strings_to_list(context_subtoken)
                        print('Context : {}'.format(context_subtoken))

                        inferred_vector = model.infer_vector(context_subtoken)
                        sims_topn = model.docvecs.most_similar([inferred_vector], topn=1000)
                        sims_topn_index = list(map(lambda x: x[0], sims_topn))

                        # Build an exhaustive suggestion list based on retrieved documents
                        _tmp_suggestions = []
                        for i, idx in enumerate(sims_topn_index):
                            word_list = train_set[idx].words
                            for word in word_list:
                                if word not in _tmp_suggestions:
                                    _tmp_suggestions.append(word)

                        # For each method proposal, tokenize it and check that each subtoken
                        # appears in the temporary suggestions list
                        # If each subtoken appears in the temporary suggestions list, then
                        # we add the original method proposal in the final suggestion list
                        suggestions = []
                        for method_proposal in method_proposals:
                            _add_proposal = True
                            method_subtokens = nlp_utils.tokenize_list(tokenizer_us, [method_proposal])
                            method_subtokens = nlp_utils.tokenize_list(tokenizer_camel, method_subtokens, lower=True)
                            method_subtokens = nlp_utils.strings_to_list(method_subtokens)
                            for subtoken in method_subtokens:
                                if subtoken not in _tmp_suggestions:
                                    _add_proposal = False
                            if _add_proposal and method_proposal not in suggestions and len(suggestions) < k:
                                suggestions.append(method_proposal)
                        print('Suggestions : {}\n'.format(suggestions))

                        if current_method_name in suggestions:
                            score += 1
                            sum_reciprocal_rank += 1 / (suggestions.index(current_method_name) + 1)
                        test_size += 1
                    context.append(current_method_name)

        with open(args.output, 'a+') as f:
            f.write('Precision@{} : {}'.format(k, score / test_size))
            f.write('MRR@{} : {}'.format(k, sum_reciprocal_rank / test_size))
            f.write('Test size : {}'.format(test_size))
        print('Precision@{} : {}'.format(k, score / test_size))
        print('MRR@{} : {}'.format(k, sum_reciprocal_rank / test_size))
        print('Test size : {}'.format(test_size))
