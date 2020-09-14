import argparse
import logging
import time
import os
import multiprocessing
import gensim.models.doc2vec
from gensim.models.doc2vec import Doc2Vec

assert gensim.models.doc2vec.FAST_VERSION > -1, "This will be painfully slow otherwise"

######################################
# Train a doc2vec model and save it #
######################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--train_set', type=str, help='Path to the training set (line format).')
    parser.add_argument('-dm', '--dm', type=int, help='If dm=1, use PV-DM otherwise use PV-DBOW.')
    parser.add_argument('-v', '--vector_dim', type=int, help='Dimension of the vectors.')
    parser.add_argument('-w', '--window', type=int, help='Size of the window.')
    parser.add_argument('-c', '--min_count', type=int, help='Ignore all words with frequency lower than min_count.')
    parser.add_argument('-e', '--epochs', type=int, help='Number of iterations over the training set.')
    parser.add_argument('-hs', '--hs', type=int, help='If hs=1, use hierarchical softmax, otherwise negative sampling.')
    parser.add_argument('-n', '--negative', type=int, help='If hs=0, specify how many "noise words" should be drawn.')
    parser.add_argument('-ns', '--ns_exponent', type=float, help='Exponent used to shape the negative sampling distribution.')
    parser.add_argument('-d', '--dbow_words', type=int, help='If set to 1 trains word-vectors simultaneous with doc vectors.')
    args = parser.parse_args()

    log_filename = './logs/doc2vec_{}_d{}_win{}_mc{}_hs{}.log'.format(
        'dbow' if args.dm == 0 else 'dm',
        args.vector_dim,
        args.window,
        args.min_count,
        args.hs
    ),
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    logging.basicConfig(
        filename='./logs/d2v_{}_d{}_win{}_mc{}_hs{}.log'.format(
            'dbow' if args.dm == 0 else 'dm',
            args.vector_dim,
            args.window,
            args.min_count,
            args.hs
        ),
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.DEBUG
    )

    logging.info('Training doc2vec model ...')
    start_time = time.perf_counter()
    model = Doc2Vec(
        corpus_file=args.train_set,
        dm=args.dm,
        vector_size=args.vector_dim,
        window=args.window,
        min_count=args.min_count,
        epochs=args.epochs,
        hs=args.hs,
        negative=args.negative,
        ns_exponent=args.ns_exponent,
        dbow_words=args.dbow_words,
        workers=multiprocessing.cpu_count()
    )
    end_time = time.perf_counter()
    logging.info('It took {} ms to train doc2vec model.'.format(end_time - start_time))
    logging.info('Saving model ...')

    model.save('./models/doc2vec/d2v_{}_d{}_win{}_mc{}_hs{}.bin'.format(
        'dbow' if args.dm == 0 else 'dm',
        args.vector_dim,
        args.window,
        args.min_count,
        args.hs
    ))

