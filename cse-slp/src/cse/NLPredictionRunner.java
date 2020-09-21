package cse;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.nio.file.Files;
import java.nio.file.Paths;

import slp.core.counting.giga.GigaCounter;
import slp.core.lexing.Lexer;
import slp.core.lexing.runners.LexerRunner;
import slp.core.lexing.simple.WhitespaceLexer;
import slp.core.modeling.Model;
import slp.core.modeling.ngram.ADMModel;
import slp.core.translating.Vocabulary;
import slp.core.translating.VocabularyRunner;

public class NLPredictionRunner {
    public static void main(String[] args) {
        if (args.length < 2) return;

        File train = new File(args[0]);
        File test = new File(args[1]);

        Lexer lexer = new WhitespaceLexer();
        LexerRunner lexerRunner = new LexerRunner(lexer, true);
        lexerRunner.setSentenceMarkers(true);

        VocabularyRunner.cutOff(10);
        Vocabulary vocabulary = VocabularyRunner.build(lexerRunner, train);
        vocabulary.close();

        Model model = new ADMModel(4, new GigaCounter());
        CompletionModelRunner modelRunner = new CompletionModelRunner(model, lexerRunner, vocabulary);
        modelRunner.learnDirectory(train);
        modelRunner.setSelfTesting(false);
        modelRunner.setCompletionCutOff(10);

        try {
            List<String> lines = Files.lines(Paths.get(args[1]))
                    .collect(Collectors.toList());
            List<String> suggestions = Files.lines(Paths.get(args[2]))
                    .collect(Collectors.toList());

            modelRunner.completeLastContentLines(lines, suggestions);
        } catch (IOException e) {
            e.printStackTrace();
        }

        /*
        try {
            List<String> lines = Files.lines(Paths.get(args[1]))
                    .collect(Collectors.toList());

            List<Stream<String>> linesLexed = lines.stream()
                    .map(lexerRunner::lexLine)
                    .collect(Collectors.toList());

        } catch (IOException e) {
            e.printStackTrace();
        }

        Stream<Pair<File, List<List<Double>>>> modeledFiles = modelRunner.modelDirectory(test);
        DoubleSummaryStatistics statistics = modelRunner.getStats(modeledFiles);
        System.out.printf("Modeled %d tokens, average entropy:\t%.4f\n", statistics.getCount(), statistics.getAverage());

        Stream<Pair<File, List<List<Double>>>> predictedFile = modelRunner.predict(test);
        DoubleSummaryStatistics completionStats = modelRunner.getStats(predictedFile);
        System.out.printf("Modeled %d tokens, average MRR:\t%.4f\n", completionStats.getCount(), completionStats.getAverage());
         */
    }
}
