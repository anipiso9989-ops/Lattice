# Lattice — Concise Captain's Log

*This is a compressed account of how I built Lattice, focused on the decisions, failures, and technical lessons that shaped the project.*

> **Transparency note:** I wrote the code myself, but I used ChatGPT minimally to help debug syntax and logic errors.

---

## What Lattice became

Lattice started as an adaptive learning engine that would model a learner, generate the next challenge, observe the result, and update its model.

I eventually rejected that design.

The problem was scope. A system that generated meaningful problems would need domain-specific generators for algebra, calculus, physics, biology, and so on. I realized I was building the wrong thing: a giant educational-content system instead of the representation of knowledge I actually cared about.

So I pivoted.

Lattice became a **personal knowledge-state graph**: a local Python CLI that stores concepts, evidence of learning, and relationships between concepts, then derives an inspectable model of what the user knows.

That pivot was probably the most important decision in the entire project.

---

## 1. Evidence, not conclusions

The core design rule became:

> **The user supplies evidence. Lattice supplies the conclusion.**

If the user simply typed `mastery = 0.8`, Lattice would basically be a spreadsheet.

Instead, the user records events such as:

- studied
- recalled
- explained
- applied
- struggled
- forgot
- encountered

Each event is timestamped, can include a note, and has a confidence value from 1–5.

Lattice stores the raw evidence permanently and derives mastery from it.

That means the model is auditable. If I later decide my mastery formula is wrong, I can change the formula and recompute the state without losing the original history.

This became one of the ideas I liked most about the architecture: **store the evidence first; treat the model as revisable.**

---

## 2. I stopped treating mastery as one number

At first, mastery was just a scalar from 0 to 1.

I decided that was too blunt.

Someone can memorize a concept without being able to apply it. Someone else may understand it well but struggle to recall it quickly.

So I modeled mastery as four separate dimensions:

- studied
- recalled
- explained
- applied

For each dimension I used a simple diminishing-returns formula:

`M = 1 - product(1 - e_i)`

where:

`e_i = confidence / 10`

Repeated strong evidence therefore looks like:

`0.50 → 0.75 → 0.875 → 0.9375`

The score approaches 1 without easily reaching it.

I do **not** claim this is a scientifically validated measure of learning. It is a provisional model that makes my assumptions explicit enough to inspect and improve.

That distinction became important throughout the project: I wanted Lattice to be a testable representation, not a claim that I had solved cognition.

---

## 3. Identity and persistence

Every concept gets a UUID.

I separated:

- **identity** = UUID
- **display value** = concept name

That matters because names can change, but evidence and relationships should still point to the same underlying concept.

The program stores everything in a local `lattice.json` file:

- concepts
- evidence
- relationships

I intentionally kept the storage simple. JSON made the system transparent while I was building it because I could open the file and inspect exactly what Lattice believed its own state was.

I also added case-insensitive duplicate protection for concepts early, because I did not want bad data contaminating the graph later.

But I deliberately did **not** apply the same duplicate rule to evidence. Studying the same concept three times is not duplicate data; it is three separate learning events.

That taught me an important lesson: two records can look structurally similar while having completely different semantics.

---

## 4. A UX annoyance forced a better architecture

Originally, every interaction required commands like:

`python lattice.py inspect "Calculus"`

I got annoyed very quickly.

So I built a persistent interactive shell:

```text
python lattice.py

lattice> list
lattice> inspect "Calculus"
lattice> evidence "Calculus" recalled -c 4
lattice> exit
```

That small UX improvement forced me to restructure the program.

I separated:

- parsing a command,
- executing a command,
- keeping the application alive.

I also had to handle the fact that `argparse` normally exits the program after invalid input. Inside an interactive shell, a typo should not kill the entire application, so I caught that exit and returned to the prompt.

The feature began as “I don't want to keep typing `python lattice.py`,” but it ended up improving the program's internal structure.

---

## 5. Relationships were more subtle than I expected

I added three relationship types:

- `prerequisite`
- `part_of`
- `related_to`

For a prerequisite edge:

`Algebra --prerequisite--> Calculus`

Algebra is the source and Calculus is the target.

Then I discovered a modeling problem.

`prerequisite` is directional:

`A prerequisite B`

is not equivalent to:

`B prerequisite A`

But `related_to` is symmetric:

`A related_to B`

means the same thing as:

`B related_to A`

That forced me to distinguish between **ordered** and **unordered** relationships.

I also introduced an invariant:

> The graph should contain at most one logical relationship of a given type between the same concepts.

Implementing that exposed several bugs.

I initially wrote logic that accidentally required the same direction **and** the reverse direction at once. That is impossible for two different concepts.

I also ran into operator-precedence problems when combining `and` and `or`.

The fix was not some clever trick. It was to make the logical grouping explicit with parentheses and reason carefully about exactly what each condition meant.

That was one of the moments where a mathematical distinction—directed versus symmetric relationships—became a concrete software invariant.

---

## 6. The graph became real when I added traversal

At first, Lattice could store graph edges, but that did not make it much of a graph-processing system.

I wanted:

`prereqs "Machine Learning"`

to find the entire upstream chain, not just the directly connected concepts.

For example:

`Arithmetic → Algebra → Calculus → Machine Learning`

should return all three prerequisites.

The first step was finding direct prerequisites.

That exposed something I had not thought deeply about before:

- relationship records contain UUID references,
- concept objects live in a separate collection.

So traversal requires joining those two collections manually.

I made several mistakes while building this:

- comparing the wrong UUID,
- referencing variables that did not exist,
- confusing the concept being inspected with the source concept on an edge,
- getting the nesting of loops and filters wrong.

Eventually the direct lookup worked.

Then I made it recursive.

---

## 7. Recursion and cycle protection

To get every prerequisite, the program has to do the same thing repeatedly:

> For every prerequisite I find, find that prerequisite's prerequisites.

That is recursion.

Then I noticed the failure case:

`A → B → C → A`

Without protection, traversal would continue forever.

So I added a `visited` set containing concept UUIDs that had already been processed.

The same set is passed through every recursive call.

I made a lot of mistakes here too:

- `concept_id == visited` instead of `concept_id in visited`
- using `.append()` on a set instead of `.add()`
- confusing the purpose of the `visited` set with the actual results list
- mixing up `append()` and `extend()`
- putting type-annotation syntax inside function calls
- checking for `None` when the function actually returned an empty list

But this feature taught me more than almost anything else in the project.

By the end, Lattice could recursively traverse arbitrary prerequisite chains while preventing cycles.

That was the point where the project stopped merely *storing* a graph and started *computing over* one.

---

## 8. How my build process changed

At the beginning, I had a recurring problem: I knew Python, but an entire project felt overwhelming.

I kept trying to imagine the finished system before writing the next function.

The method that finally worked was:

> Build the smallest observable behavior the program cannot do yet.

Then:

1. implement it,
2. test it,
3. break it,
4. fix it,
5. move one layer outward.

That became the actual engineering process behind Lattice.

The project also changed substantially while I built it:

`adaptive tutor → bounded problem generator → knowledge-state graph`

I learned that removing an ambitious feature can make a project **more** technically coherent, not less.

---

## 9. What Lattice still does not solve

The current model has deliberate limitations.

- It depends on self-reported evidence.
- It cannot independently verify what somebody knows.
- Mastery does not decay with time.
- `struggled`, `forgot`, and `encountered` are stored but do not currently change mastery.
- The mastery formula is a design choice, not a validated cognitive metric.
- Relationships are user-supplied.
- It does not yet automatically identify true knowledge gaps.
- `part_of` and `related_to` do not yet drive advanced graph analysis.

I consider those limitations useful rather than embarrassing.

They tell me exactly where the model breaks and therefore what a future version would need to test.

The most obvious next experiment is to combine prerequisite structure with mastery evidence and ask:

> **Can Lattice identify plausible prerequisite gaps without pretending that its inference is certain?**

---

## What I actually built

By the end of v1, Lattice could:

- create and persist concepts,
- assign stable UUID identities,
- prevent duplicate concepts,
- record timestamped learning evidence,
- store confidence and notes,
- display evidence history,
- calculate four mastery dimensions,
- inspect a concept's current knowledge state,
- run as an interactive CLI,
- store directed and symmetric relationships,
- enforce relationship invariants,
- display a concept's relationships,
- recursively traverse prerequisite chains,
- prevent infinite traversal through cycles.

The finished program is not the most important part of the project.

The important part was taking an idea about learning, forcing its vague language into explicit representations and algorithms, discovering where those representations failed, and revising them until they could survive contact with actual code.
