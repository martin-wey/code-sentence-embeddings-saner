package cse;

import slp.core.modeling.runners.ModelRunner;
import slp.core.lexing.runners.LexerRunner;
import slp.core.modeling.Model;
import slp.core.translating.Vocabulary;
import slp.core.util.Pair;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

final class CompletionModelRunner extends ModelRunner {

    CompletionModelRunner(Model model, LexerRunner lexerRunner, Vocabulary vocabulary) {
        super(model, lexerRunner, vocabulary);
    }

    void setCompletionCutOff(int value) {
        setPredictionCutoff(value);
    }

    void completeLastContentLine(String content) {
        completeLastToken(this.lexerRunner.lexLine(content));
    }

    void completeLastContentLines(List<String> content, List<String> suggestions) {
        List<Completion> rankingTmp = content.stream()
                .limit(10)
                .map(p -> completeLastToken(this.lexerRunner.lexLine(p)))
                .collect(Collectors.toList());

        // add static analysis suggestions corresponding to each completion
        List<Completion> rankings = IntStream.range(0, rankingTmp.size())
                .mapToObj(i -> {
                    Completion ranking = rankingTmp.get(i);
                    ranking.setSuggestions(suggestions.get(i));
                    return ranking;
                }).collect(Collectors.toList());

        // compute stats and metrics
        System.out.println(rankings.get(1).getSuggestions());
    }

    private Completion completeLastToken(Stream<String> lexed) {
        List<Integer> tokens = this.vocabulary.toIndices(lexed).collect(Collectors.toList());
        // Context is made of the previous tokens without the EOS special token (so -2)
        List<Integer> ctxTokens = tokens.stream().limit(tokens.size() - 2).collect(Collectors.toList());

        List<Map<Integer, Pair<Double, Double>>> preds = this.model.predict(ctxTokens);
        Map<Integer, Pair<Double, Double>> lastPred = preds.get(preds.size() - 2);
        List<Pair<Integer, Double>> completions = lastPred.entrySet().stream()
                .map(e -> Pair.of(e.getKey(), toProb(e.getValue())))
                .sorted((p1, p2) -> - Double.compare(p1.right, p2.right))
                .limit(GLOBAL_PREDICTION_CUTOFF)
                .collect(Collectors.toList());

        return new Completion(tokens.get(tokens.size() - 2), completions);
    }
}
