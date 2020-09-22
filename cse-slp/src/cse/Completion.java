package cse;

// This code is adapted from:
// https://github.com/SLP-team/SLP-Core/blob/master/src/main/java/slp/core/modeling/runners/Completion.java

import java.util.List;
import java.util.stream.Collectors;

import slp.core.util.Pair;

public class Completion {
    private final Integer realIx;
    private final List<Pair<Integer, Double>> completions;
    private List<Integer> suggestions;
    private List<Pair<Integer, Double>> filteredSuggestions;

    Completion(Integer realIx, List<Pair<Integer, Double>> predictions) {
        this.realIx = realIx;
        this.completions = predictions;
    }

    public Integer getRealIx() {
        return realIx;
    }

    List<Pair<Integer, Double>> getCompletions() {
        return completions;
    }

    void setSuggestions(List<Integer> suggestions) {
        this.suggestions = suggestions;
    }

    public List<Integer> getSuggestions() {
        return suggestions;
    }

    public void setFilteredSuggestions(List<Pair<Integer, Double>> suggestions) {
        this.filteredSuggestions = suggestions;
    }

    List<Pair<Integer, Double>> getFilteredSuggestions() {
        return filteredSuggestions;
    }

    void filterSuggestions(int maxSize) {
        this.filteredSuggestions = completions.stream()
                .filter(e -> this.suggestions.contains(e.left))
                .limit(10)
                .collect(Collectors.toList());
    }

    int getRank() {
        if (this.realIx == null) return -1;
        else {
            for (int i = 0; i < this.filteredSuggestions.size(); i++) {
                if (this.filteredSuggestions.get(i).left.equals(this.realIx) && this.realIx != 0) {
                    return i;
                }
            }
            return -1;
        }
    }

    double getRecall() {
        if (this.realIx == null) return 0;
        else {
            for (Pair<Integer, Double> suggestion : filteredSuggestions) {
                if (suggestion.left.equals(this.realIx) && this.realIx != 0) {
                    return 1;
                }
            }
            return 0;
        }
    }
}
