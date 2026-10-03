#!/usr/bin/env python3
"""
Word-Level Highlight

highlight(text, sources) -> str

    text     : words separated by single spaces, letters and digits only
    sources  : list of phrases, each one or more words, case-sensitive

Find every WHOLE-WORD occurrence of every source in text (a match must line
up with word boundaries: "aa" does not match inside "aaab"). Merge occurrences
whose word spans overlap, directly or transitively, into maximal regions.
Wrap each region in <hl> ... </hl> and return the rebuilt string.
Regions that merely touch (no shared word) stay separate.

Parts:
    1. one source: whole-word match + wrap (several occurrences allowed)
    2. several sources that do not overlap each other
    3. overlapping sources: merge into maximal regions (sort + sweep, LC 56)
    4. bonus: 20,000 words x 2,000 sources — the naive n*L scan takes seconds;
       index text words in a dict (or a trie over words) to go sub-second

Run the tests:  python3 test_highlight.py        (all parts)
                python3 test_highlight.py 2      (part 2 only)
or just run this file (F5 in VS Code).
"""


def highlight(text: str, sources: list[str]) -> str:
    text_list = text.split(" ")
    text_coord = []
    positions = {}
    for i, word in enumerate(text_list):
        positions.setdefault(word, []).append(i)
    for source in sources:
        source_list = source.split(" ")
        source_len = len(source_list)
        #match source_list against text_list, find starting coord and end coord
        for start_index in positions.get(source_list[0], []):
            if source_list == text_list[start_index: start_index + source_len]:
                text_coord.append((start_index, start_index + source_len))
    text_coord.sort()
    
    merged_coord = []
    for left, right in text_coord:
        if merged_coord and left < merged_coord[-1][1]:
            merged_coord[-1] = (merged_coord[-1][0], max(merged_coord[-1][1], right))
        else:
            merged_coord.append((left, right))
    res = []
    cur = 0
    for left, right in merged_coord:
        res.extend(text_list[cur: left])
        res.append("<hl>" + " ".join(text_list[left: right]) + "</hl>")
        cur = right
    res.extend(text_list[cur:])
    return " ".join(res)




    


if __name__ == "__main__":
    from test_highlight import main
    main()
