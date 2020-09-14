import argparse
import json
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument


def eval_doc2vec(model, train_set, test_set, ctx_size, k, output_path):
    sent_index = 0
    sent_count = 0
    next_word_accuracy = 0
    sum_reciprocal_rank = 0

    stop = False
    while not stop:
        full_sent = test_set[sent_index]
        if len(full_sent) >= ctx_size + 1:
            sent = full_sent[:ctx_size]
            print('{} - Test sentence : {}'.format(sent_count, sent))
            inferred_vector = model.infer_vector(sent)
            sims_topn = model.docvecs.most_similar([inferred_vector], topn=k * 2)
            sims_topn_index = list(map(lambda x: x[0], sims_topn))

            suggestion = []
            for i, idx in enumerate(sims_topn_index):
                word_list = train_set[idx].words
                for word in word_list:
                    if word not in suggestion and len(suggestion) < k:
                        suggestion.append(word)
            next_word_in_suggestion = 1 if full_sent[ctx_size] in suggestion else 0
            if next_word_in_suggestion is 1:
                sum_reciprocal_rank += 1 / (suggestion.index(full_sent[ctx_size]) + 1)
            next_word_accuracy += next_word_in_suggestion
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

    ctx_range = list(range(1, 9))
    topk_range = [5, 10, 15, 20]
    for k in topk_range:
        for c in ctx_range:
            open(args.output, 'a+').write(
                'Evaluating doc2vec model with c={} and k={}\n'.format(c, k)
            )
            print('Evaluating doc2vec model with c={} and k={}'.format(c, k))
            eval_doc2vec(model, train_set, test_set, c, k, args.output)