import argparse
import subprocess

projects = ['aws-sdk-java', 'hibernate-orm', 'gradle', 'spring-framework', 'jclouds'
            'hadoop-common', 'neo4j', 'druid', 'spring-security', 'cassandra',
            'netty', 'mongo-java-driver', 'antlr', 'junit', 'facebook-android-sdk',
            'twitter4j', 'hystrix', 'clojure', 'android-async-http', 'game-of-life']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', type=str)
    parser.add_argument('-m', '--model_path', type=str)
    parser.add_argument('-k', '--kenlm_path', type=str)
    args = parser.parse_args()

    for project in projects:
        data = "%s/%s/ngrams.txt" % (args.data_path, project)
        results = "%s/results/%s.log" % (args.data_path, project)
        open(results, 'a').close()
        for i in range(2, 10):
            model = "%s/%s-g.bin" % (args.model_path, i)
            with open(results, 'a+') as f:
                f.write("Evaluating %s-grams model:\n" % i)
                f.write('----------------------------\n')
                cat = subprocess.Popen(['cat', data], stdout=subprocess.PIPE)
                query = subprocess.Popen(
                    ['%s/query' % args.kenlm_path, model, '-v', 'summary'],
                    stdin=cat.stdout,
                    stdout=f
                )
                query.communicate()
                query.wait()