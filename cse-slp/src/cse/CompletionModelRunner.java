package cse;

import slp.core.modeling.runners.ModelRunner;
import slp.core.lexing.runners.LexerRunner;
import slp.core.modeling.Model;
import slp.core.translating.Vocabulary;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

final class CompletionModelRunner extends ModelRunner {

    CompletionModelRunner(Model model, LexerRunner lexerRunner, Vocabulary vocabulary) {
        super(model, lexerRunner, vocabulary);
    }

    void predictLastContent(String content) {
        //setPredictionCutoff(20);
        predictLastToken(this.lexerRunner.lexLine(content));
    }

    private void predictLastToken(Stream<String> lexed) {
        List<Integer> tokens = this.vocabulary.toIndices(lexed).collect(Collectors.toList());
        List<List<Integer>> preds = toPredictions(this.model.predict(tokens));
        List<Integer> lastPred = preds.get(preds.size() - 2);
        List<String> lastPredWords = this.vocabulary.toWords(lastPred);
        System.out.println(lastPredWords);
    }
}
