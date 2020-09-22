package cse;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.DoubleSummaryStatistics;

import slp.core.counting.giga.GigaCounter;
import slp.core.lexing.Lexer;
import slp.core.lexing.runners.LexerRunner;
import slp.core.lexing.simple.WhitespaceLexer;
import slp.core.modeling.Model;
import slp.core.modeling.ngram.ADMModel;
import slp.core.modeling.ngram.JMModel;
import slp.core.translating.Vocabulary;
import slp.core.translating.VocabularyRunner;

public class JavaFunctionPredictionRunner {
    public static void main(String[] args) {
        if (args.length < 2) return;

        File train = new File(args[0]);

        Lexer lexer = new WhitespaceLexer();
        LexerRunner lexerRunner = new LexerRunner(lexer, true);
        lexerRunner.setSentenceMarkers(true);

        VocabularyRunner.cutOff(10);
        Vocabulary vocabulary = VocabularyRunner.build(lexerRunner, train);
        vocabulary.close();

        Model model = new JMModel(6, new GigaCounter());
        CompletionModelRunner modelRunner = new CompletionModelRunner(model, lexerRunner, vocabulary);
        modelRunner.learnDirectory(train);
        modelRunner.setSelfTesting(false);
        modelRunner.setTmpCompletionCutOff(1000);

        try {
            List<String> sequences = Files.lines(Paths.get(args[1]))
                    .collect(Collectors.toList());
            List<String> suggestions = Files.lines(Paths.get(args[2]))
                    .collect(Collectors.toList());

            List<Completion> completions = modelRunner.completeLastTokenLines(sequences, suggestions);
            DoubleSummaryStatistics mrrs = modelRunner.getCompletionMRR(completions);
            System.out.printf("Evaluated %d samples, average MRR:\t%.4f\n", mrrs.getCount(), mrrs.getAverage());

            DoubleSummaryStatistics recalls = modelRunner.getCompletionRecall(completions);
            System.out.printf("Evaluated %d samples, Recall@%d MRR:\t%.4f\n",
                    recalls.getCount(), modelRunner.COMPLETION_CUTOFF, recalls.getAverage());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
