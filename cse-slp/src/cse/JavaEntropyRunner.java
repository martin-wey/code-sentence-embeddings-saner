package cse;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.DoubleSummaryStatistics;

import slp.core.counting.giga.GigaCounter;
import slp.core.lexing.Lexer;
import slp.core.lexing.runners.LexerRunner;
import slp.core.lexing.simple.WhitespaceLexer;
import slp.core.modeling.Model;
import slp.core.modeling.ngram.JMModel;
import slp.core.modeling.mix.MixModel;
import slp.core.modeling.dynamic.CacheModel;
import slp.core.modeling.runners.ModelRunner;
import slp.core.translating.Vocabulary;
import slp.core.translating.VocabularyRunner;

public class JavaEntropyRunner {
    public static void main(String[] args) {
        if (args.length != 2) return;

        File train = new File(args[0]);
        File test = new File(args[1]);

        Lexer lexer = new WhitespaceLexer();
        LexerRunner lexerRunner = new LexerRunner(lexer, true);
        lexerRunner.setSentenceMarkers(true);

        List<Integer> cutOffValues = new ArrayList<>(Arrays.asList(5, 10, 20));
        List<Integer> modelOrderValues = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5, 6));

        List<String> results = new ArrayList<>();
        for(Integer cutOff : cutOffValues) {
            for (Integer modelOrder : modelOrderValues) {
                VocabularyRunner.cutOff(cutOff);
                Vocabulary vocabulary = VocabularyRunner.build(lexerRunner, train);
                vocabulary.close();

                Model model = new JMModel(modelOrder, new GigaCounter());
                // model = MixModel.standard(model, new CacheModel());
                // model.setDynamic(true);

                ModelRunner modelRunner = new ModelRunner(model, lexerRunner, vocabulary);
                modelRunner.learnDirectory(train);
                modelRunner.setSelfTesting(false);

                List<List<Double>> modeledTest = modelRunner.modelFile(test);
                DoubleSummaryStatistics statistics = modelRunner.getStats(modeledTest);
                results.add(String.format(
                    "Modeled %d tokens, cut-off=%d, model order=%d, average entropy:\t%.4f\n",
                    statistics.getCount(),
                    cutOff,
                    modelOrder,
                    statistics.getAverage())
                );
            }
        }
        results.forEach(System.out::println);
    }
}
