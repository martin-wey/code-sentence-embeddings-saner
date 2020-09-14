package cse;

import java.io.File;
import java.util.DoubleSummaryStatistics;
import java.util.List;
import java.util.stream.Stream;

import slp.core.counting.giga.GigaCounter;
import slp.core.lexing.Lexer;
import slp.core.lexing.runners.LexerRunner;
import slp.core.lexing.simple.WhitespaceLexer;
import slp.core.modeling.Model;
import slp.core.modeling.ngram.ADMModel;
import slp.core.modeling.runners.ModelRunner;
import slp.core.translating.Vocabulary;
import slp.core.translating.VocabularyRunner;
import slp.core.util.Pair;

public class NLPredictionRunner {
    public static void main(String[] args) {
        if (args.length < 2) return;

        File train = new File(args[0]);
        File test = new File(args[1]);

        // File test = args.length < 2 ? train : new File(args[1]);

        Lexer lexer = new WhitespaceLexer();
        LexerRunner lexerRunner = new LexerRunner(lexer, true);
        lexerRunner.setSentenceMarkers(true);

        VocabularyRunner.cutOff(10);
        Vocabulary vocabulary = VocabularyRunner.build(lexerRunner, train);
        vocabulary.close();

        Model model = new ADMModel(4, new GigaCounter());
        ModelRunner modelRunner = new ModelRunner(model, lexerRunner, vocabulary);
        modelRunner.learnDirectory(train);
        modelRunner.setSelfTesting(false);

        Stream<Pair<File, List<List<Double>>>> modeledFiles = modelRunner.modelDirectory(test);
        DoubleSummaryStatistics statistics = modelRunner.getStats(modeledFiles);
        System.out.printf("Modeled %d tokens, average entropy:\t%.4f\n", statistics.getCount(), statistics.getAverage());

        /*
        Stream<Pair<File, List<List<Double>>>> predictedFile = modelRunner.predict(test);
        DoubleSummaryStatistics completionStats = modelRunner.getStats(predictedFile);
        System.out.printf("Modeled %d tokens, average MRR:\t%.4f\n", completionStats.getCount(), completionStats.getAverage());
         */


    }
}
