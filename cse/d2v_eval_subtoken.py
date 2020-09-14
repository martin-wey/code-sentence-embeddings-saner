import argparse
import json
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from utils import nlp_utils


def eval_doc2vec(model, train_set, test_set, ctx_size, k, tokenizer_us, tokenizer_camel, output_path):
    sent_index = 0
    sent_count = 0
    next_word_accuracy = 0
    sum_reciprocal_rank = 0

    stop = False
    while not stop:
        full_sent = test_set[sent_index]
        if len(full_sent) >= ctx_size + 1:
            sent = full_sent[:ctx_size]
            sent = nlp_utils.tokenize_list(tokenizer_us, sent)
            sent_subtoken = nlp_utils.tokenize_list(tokenizer_camel, sent, lower=True)
            sent_subtoken = nlp_utils.strings_to_list(sent_subtoken)
            # print('{} - Test sentence : {}'.format(sent_count, sent_subtoken))

            inferred_vector = model.infer_vector(sent_subtoken)
            sims_topn = model.docvecs.most_similar([inferred_vector], topn=k * 3)
            sims_topn_index = list(map(lambda x: x[0], sims_topn))

            suggestion = []
            for i, idx in enumerate(sims_topn_index):
                word_list = train_set[idx].words
                for word in word_list:
                    if word not in suggestion and len(suggestion) < k:
                        suggestion.append(word)

            # print('Pred : ' + full_sent[ctx_size])
            next_call = nlp_utils.tokenize_list(tokenizer_us, [full_sent[ctx_size]])
            next_call = nlp_utils.tokenize_list(tokenizer_camel, next_call, lower=True)
            next_call = nlp_utils.strings_to_list(next_call)
            # print('Pred token : ' + ' '.join(next_call))
            # print(suggestion)

            score = 1
            # We check that all subtokens of the method to predict are
            # present in the suggestion list
            for subtoken in next_call:
                if subtoken not in suggestion:
                    score = 0
            if score == 1:
                # The reciprocal rank is computed by taking into account
                # the index of the last subtoken of the method to predict
                # in the suggestion list
                sum_reciprocal_rank += 1 / (suggestion.index(next_call[-1]) + 1)
            next_word_accuracy += score
            # print(score)
            sent_count += 1
        sent_index += 1
        if sent_index == (len(test_set) - 1):
            stop = True
    with open(output_path, 'a+') as f:
        f.write('Accuracy : {} (ctx={}, topn={}, test_size={})\n'.format(
            next_word_accuracy / sent_count,
            ctx_size,
            k,
            sent_count
        ))
        f.write('MRR : {} (ctx={}, topn={}, test_size={})\n'.format(
            sum_reciprocal_rank / sent_count,
            ctx_size,
            k,
            sent_count
        ))
    print('Accuracy : {} (ctx={}, topn={}, test_size={})\n'.format(
        next_word_accuracy / sent_count,
        ctx_size,
        k,
        sent_count
    ))
    print('MRR : {} (ctx={}, topn={}, test_size={})\n'.format(
        sum_reciprocal_rank / sent_count,
        ctx_size,
        k,
        sent_count
    ))


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
    print('Initialize tokenizers ...')
    tokenizer_us = nlp_utils.initialize_nlp('en_core_web_sm')
    tokenizer_us = nlp_utils.initialize_tokenizer(tokenizer_us, 'underscore')
    tokenizer_camel = nlp_utils.initialize_nlp('en_core_web_sm')
    tokenizer_camel = nlp_utils.initialize_tokenizer(tokenizer_camel, 'camel')

    ctx_range = list(range(1, 9))
    topk_range = [10, 20, 30, 40]
    for k in topk_range:
        for c in ctx_range:
            open(args.output, 'a').write(
                'Evaluating doc2vec model with c={} and k={}\n'.format(c, k)
            )
            print('Evaluating doc2vec model with c={} and k={}'.format(c, k))
            eval_doc2vec(model, train_set, test_set, c, k, tokenizer_us, tokenizer_camel, args.output)