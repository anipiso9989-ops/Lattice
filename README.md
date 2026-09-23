# Lattice

Lattice is small CLI model that represents a person's knowledge. You add concepts, connect them, and record evidence of learning. Lattice uses your inputs to calculate a knowledge state for each concept.

I built it to test a provisional idea: knowledge can be represented as a graph of concepts and relationships. Learning changes what we know and what we can do with the knowledge we have. Think of this as an external model of what you know, essentially. I didn't want to create something simpler like a list of topics, because that would have been too blunt. 

I started with concepts as "nodes" and relationships as "connecting lines" or "edges". Think of a graph with dots and lines connecting them. Each concept has a unique stable ID (UUID, 128 bit number), so the connections can handle name changes. A prerequisite points from the foundational concept to the concept that depends on it (in my code, these are "source" and "target", respectively); `prereqs` walks you through that chain of connections.

Then, I added evidence. Things like studying, recalling (active recall, a well known learning technique), explaining (i.e. Feynman technique), and applying a concept (probably one of the best things you can do for learning) are recorded as separate events. Lattice derives 4 corresponding mastery scores from those events, with diminishing returns.

Here's the formula I used for mastery:

$$
M = 1 - \prod_{i=1}^{n} \left(1 - \frac{c_i}{10}\right)
$$

where $M$ = mastery, and $c_i$ = your confidence level (which is a user input, an integer from 1 to 5, inclusive). $1-\frac{c_i}{10}$ is your uncertainty. As your confidence level goes up, the mastery level gradually goes up, but doesn't really reach 1 (intentional; this introduces diminishing returns which exist in the real world, AND it also doesn't assume perfection, which truly does NOT exist in our world. You can get approximate perfection, but for the purposes of this project, you can't get to 1).

The mastery scores remain separate; being able to recall something isn't the same as being able to apply it. I think one composite score would have been a misrepresentation of a person's actual mastery. Encounters, struggles, and forgetting can also be logged as evidence, but they don't change the scores; I don't think those would reflect mastery for the purposes of this project; I wanted to focus on the positives.

The build process made my theories concrete. I had to decide what exactly a relationship means, what the different relationship types were, how to avoid getting stuck in a cycle, what counts as evidence, and what a score can honestly claim. The result is a working program, with assumptions I can inspect and change, rather than a claim that I've cracked the theory of the mind.

## Try It! (plz try it if you can I need feedback)

Just download `lattice.py` and run `python lattice.py` for the interactive shell, and then run these example commands if you'd like (documentation is in `CHEATSHEET.txt`):
```
add "Algebra"
add "Calculus"
relate "Algebra" prerequisite "Calculus"
evidence "Algebra" recalled -c 4 -n "Solved problems from memory"
inspect "Algebra"
prereqs "Calculus"
```

Other commands you may be interested include `list`, `history`, and `relationships`. Data is saved locally in `lattice.json`. To reset your entire model, just delete the file; the program will create a brand new one if it sees one is missing.

## What's open for discussion

My mastery formula is a design choice, not an actual measure of understanding. Evidence types have equal weight within their dimensions, and scores don't decay with time (something that actually does happen in the real world if you don't practice your skills regularly). Lattice can show the structure and evidence you've entered: it cannot establish what someone knows independently of their inputs. So, the program is dependent on one's self awareness and willingness to log data in. This is why I introduced CLI commands to make the whole process WAY faster; I don't want the user experience to be inefficient. Because this process could take some time, **speed** is key.

## Next steps

A feature that I'm considering building is to use prerequisites and evidence together to identify possible knowledge gaps.

Also, I'm considering how to assign different mastery weightage to the 4 different types of evidence; obviously, being able to apply something shows mastery better than just studying it, so logically it should have more weight. 

I'll build these later, though. Definitely keeping a tab on it.
