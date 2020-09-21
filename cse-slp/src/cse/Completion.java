package cse;

// This code is adapted from:
// https://github.com/SLP-team/SLP-Core/blob/master/src/main/java/slp/core/modeling/runners/Completion.java

import java.util.List;
import java.util.stream.Stream;

import slp.core.util.Pair;

public class Completion {
    private final Integer realIx;
    private final List<Pair<Integer, Double>> completions;
    private String suggestions;

    public Completion(Integer realIx, List<Pair<Integer, Double>> predictions, String suggestions) {
        this.realIx = realIx;
        this.completions = predictions;
        this.suggestions = suggestions;
    }

    public Completion(Integer realIx, List<Pair<Integer, Double>> predictions) {
        this.realIx = realIx;
        this.completions = predictions;
    }

    public Integer getRealIx() {
        return realIx;
    }

    public List<Pair<Integer, Double>> getPredictions() {
        return completions;
    }

    public void setSuggestions(String suggestions) {
        this.suggestions = suggestions;
    }

    public String getSuggestions() {
        return suggestions;
    }

    public int getRank() {
        if (this.realIx == null) return -1;
        else {
            for (int i = 0; i < this.completions.size(); i++) {
                if (this.completions.get(i).left.equals(this.realIx)) {
                    return i;
                }
            }
            return -1;
        }
    }
}
