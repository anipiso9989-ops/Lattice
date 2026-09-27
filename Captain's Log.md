*This is an account of the build process that I went through when building Lattice. I wrote it after finishing the project.*
***
**Transparency Note**: I wrote the code myself, but I did use ChatGPT to debug a **little bit**. I don't particularly remember where exactly I used it, but I remembered it was used when I had *syntax errors*.
***
# Versions of the Project, at a Glance
### Originally:
- “An adaptive learning engine that models the learner and chooses the next challenge.”

### After the first technical critique
- “A bounded adaptive-learning algorithm using explicit knowledge tracing and generated problems.”

### After the major pivot
- “A personal knowledge-state graph that builds an external model of what a user knows from evidence of learning.”

### Current
- “A local Python CLI that stores concepts, learning evidence, and relationships; derives four mastery dimensions with a transparent diminishing-returns model; and recursively traverses prerequisite structure.”
# Entry 001

I initially wanted to build something that would be an application of the ideas I came up with. 

I didn't want this project to be something productivity-directed; I had already built things like Concept Packager, so I rejected tools like that for this idea.

Initially, the project felt a little overwhelming because I had no clue what to *build*. So, I took some time to brainstorm and came up with a list of features that have all been implemented into the program.

When I was building, I took an "increment first" approach. Essentially, I'd build a feature, test it and see if there's any syntax/logic errors, and then move on. If there were any said errors, I'd work with ChatGPT to fix them.

# 002

v1 of Lattice, the first proposed version, was supposed to be an adaptive learning engine.

The model was supposed to model what the learner knows, pick the next challenge and let the learner attempt it, and then adapt the model and run the process again based on feedback. 

Concepts learned would be "nodes" in a knowledge graph, and relationships would be "connections". Think of a relationship like "related to", or "prerequisite".

For example, if I had algebra, pre-calculus, and calculus, the program was supposed to come up with questions based on mastery, use the chain of relationships and how well I knew each subject, and then select increasingly appropriate problems. 

The problem was that you can't really generate novelty with a deterministic computer program, so I scrapped this idea.

Oh and by the way, the entire program was supposed to run in your CLI. No GUI (for simplicity's sake), authentication, web app architecture, databases, branding, or LLM calls.

So, I built a very early v0.1 prototype. Initially, it was difficult to build and I needed help when getting started. But, it worked. It included a simple loop with concepts, relationships, a mastery score from 0 to 1, and data persistence with JSON. 

The early logic for mastery was intentionally simple, so as to not unnecessarily complicate the code.

It proved that I could run a local system that persisted, that the model could be represented in 1s and 0s, and that the loop actually worked.

# 003

This is where I made a big pivot. I redefined Lattice's purpose as an external representation of a person's knowledge, which I hypothesized to provisionally act as a mental model with connections and nodes, just like a neural network (whether that be artificial or natural). 

Essentially, I decided that the user would supply evidence of learning (so the whole project is dependent on the user's inputs), Lattice stores it, and Lattice also maintains a structured model of what the user knows and how well, and updates based on later inputs from the user. 

This was a more general idea than my initial one, because it applied to essentially anything one could learn.

This project was not my proof that I had solved cognition, but rather just a representation of the theories I came up with, so that those same theories could be inspected and improved over time.

# 004

The central architecture became:
  - concepts,
  - relationships,
  - evidence,
  - mastery derived from evidence,
  - knowledge-state views derived from the stored data.

The mastery score is created by Lattice (the formula is on the README page). If the user chose the mastery score, Lattice would just be a spreadsheet.

Instead, the user provides evidence:
- studied
- recalled
- explained
- applied
- struggled
- forgot
- encountered
Lattice calculates a mastery state from the first 4 events. I kept the last 3 as just evidence.

It also stores the dates of each piece of evidence.

This allows for transparent auditing of what the user has actually done, and let's us figure out *why* Lattice did what it did.
# 005

I used a custom dataclass called `Concept` to define each concept.  UUIDs were used to assign every element of the knowledge graph its own unique name.

These mattered because names can change. So, identity = UUID, but display name = concept name. We keep readability, but the computer still understands what's what.

I also implemented an early version of CLI usage using `argparse` so that the user could interact with the app using custom commands like `add` and `list`. UX to me is very important so making this app easy to use was critical.

# 006

Then, I built duplicate protection because I realized that it would have been really annoying to have 2 concepts of the same name in the app. Duplication protection was also **case insensitive**; it didn't care whether you wrote it in all caps or not.

But, this duplicate protection only applied to concepts, not evidence. You can study something 3 times and log it in; Lattice doesn't block that.

I built this early because I didn't want to deal with wrong data later; think of it as proactive error prevention.

Then I started to move a little fast. I built the evidence data class, and included the evidence types.

I also built confidence, an integer from 1-5, inclusive. This is really important because it lets Lattice calculate the mastery score. Confidence goes along with each element of evidence. It roughly means "how strongly/reliably the user believes this evidence represents what happened", or rather "how well they understand the concept after doing this evidence". Evidence can carry an optional note if needed, and each evidence element also gets its own timestamp, to the second.

I then added a history command that allowed the user to view the evidence of a given concept. Edge cases (i.e. existing concept with no evidence) were handled.

I then defined mastery as not one singular number, but something with 4 dimensions, one for each piece of evidence (study, recall, explanation, application). Mastery went from a scalar to a vector, which I think is a better representation.

I didn't have enough knowledge to create a sophisticated formula myself, so I just created a simple one that *worked*.

For one mastery dimension:

`M = 1 - product(1 - e_i)`

where:

`e_i = confidence / 10`

So confidence maps as:
- 1/5 → 0.10
- 2/5 → 0.20
- 3/5 → 0.30
- 4/5 → 0.40
- 5/5 → 0.50

If we do repeated confidence-5 events for example, mastery becomes 0.5 → 0.75 → 0.875 → 0.9375. **Diminishing returns.** The first initial exposure matters more than the 20th.

Then, I added an `inspect` command that finds the concept, calculates its 4 mastery dimensions, and prints the name of the concept plus the percentages.

However, somewhere in the build process, I realized there was a problem. Every time you wanted to interact with the program, you had to type `python lattice.py blah blah blah argument goes here`. I didn't like that, so I implemented a persistent interactive shell.

Type in `python lattice.py` once, and you can type in all of the commands you want. `exit` closes the program with your changes saved.

After that was built, I added relationships. 3 types:
- prerequisite
- part_of
- related_to

It's its own dataclass.

There was also a direction to it, with 3 parts. For example
`Algebra --prerequisite-→ Precalculus`
- Algebra is the source
- Precalculus is the target
- prerequisite is the relationship type

# 007
There were edge cases for relationships though.

For example, I blocked relationships where source and target are the same concept. Additionally, I blocked exact duplicates for relationships. 

Another deeper issue. `related_to` is symmetric. `A is related to B` is logically the same thing as `B is related to A`.

So, this forced me to distinguish ordered and unordered pairs for directed and symmetric relationships, respectively. 

I encountered a mistake in which I was actually representing these conditions in an if statement. For some reason, there was a logic error. So, I looked into if statements and realized I could use *parentheses* to clearly define what goes with what. Essentially, there were some precedence issues. Basically:
- wrong: `statement 1 and statement 2 or statement 3 and statement 4
- correct: `(statement 1 and statement 2) or (statement 3 and statement 4)`
- The incorrect one would have evaluated left to right, with statement 2 and 3 being evaluated initially.
- I also tried to require same AND reverse direction simultaneously, but that's impossible for 2 different concepts.
- So, I had to change my logic to OR.

I also had some syntax errors, i.e. wrote `related_to` as `related to`. Not pretty.

This also introduced an invariant: the graph should contain at most one logical relationship of a given type between the same concepts.

Then, I implemented prerequisite traversal. Lattice stored edges, but that along didn't make it a graph processing system. It needed to find the upstream prereqs of a given concept, not the directly connected ones. Essentially, I needed a chain of prerequisites.

Since prerequisite edges point:
	source --prereq-→ target
I needed to follow the prerequisite concepts backwards.

The intended algorithm was to give an input (the data and concept_id). Then for each relationship, it had to be a prerequisite, and its target had to be the concept being inspected. Then, match relationship source ID to the concept ID being inspected, and add that to the chain of prerequisites.

Unfortunately, there were some logical mistakes.

I tried to compare `concept_id == relationship["source_id"]` instead of the current concept's ID to the relationship source ID, since the concept being inspected changes as you go down the line of prereqs. 

Some nesting issues with looping and filtering also existed and took a while to fix. 

I actually learned something I didn't know before. The graph has 2 separate collections of data:
  - relationship records contain UUID references,
  - actual concept dictionaries live elsewhere.
Traversal therefore requires joining those collections manually.

# 008

This is really the last thing I built: recursive traversal.

The goal was to find all prerequisites, so the program had to find direct prereqs, find THAT prereq's prereqs, and continue until no more exist. Recursion fit because it was a repeating process that used the previous output for the next input.

There's a danger though; cyclical prereqs.

If A → B, B → C, and C → A, then the cycle doesn't end. Now, realistically, this doesn't exist to the best of my knowledge, but I still implemented protections.

I created a set called `visited`. It would chuck every prereq in there as well as the set of the chain of prereqs for a given concept, and then if it ever came across it, it would stop going further. This same set is passed through recursive calls; it does not reset when you go down the chain of prereqs, otherwise that would defeat the purpose of what it was built to do.

I made a lot of mistakes when building this feature.

For one, I compared an ID to the whole set: `concept_id == visited`.
The ID should be IN the set "visited", so I changed `==` to `in`.

Another thing. I forgot what sets and lists use to add elements and mixed the two up. Now I know:
- Sets use .add()
- Lists use .append()

There was also a mistake with the set `visited` and the dictionary `all_prereqs`, which I was storing the chain of prereqs in.

I needed to specify to the code and to myself that `visited ` is just a checking set to make sure we don't repeat any prereqs, and `all_prereqs` is the actual set, the real output.


There were plenty of syntax errors here too. 

I tried calling a function using something like `data:dict` for some reason, but those don't belong there; they belong in the function definitions. 

After fixing my mistakes, I wired everything to the CLI, tested it, and voila: v1 was ready to go.

# Final Implementation List, at a Glance
- Wanted one substantial Python project grounded in my own ideas.
- Chose Lattice as an adaptive learning engine.
- Ran the first working prototype.
- Challenged its vague assumptions.
- Considered deterministic algebra problem generation.
- Rejected problem generation as wrong scope.
- Redefined Lattice as an external knowledge-state graph.
- Established concepts / relationships / evidence architecture.
- Added JSON persistence.
- Added concept creation and listing.
- Added UUID identity.
- Added evidence events.
- Added confidence, notes, timestamps.
- Added concept lookup.
- Added duplicate concept protection.
- Added history.
- Chose four mastery dimensions.
- Chose diminishing-returns formula.
- Added single-dimension mastery function.
- Added all-dimensions mastery function.
- Added `inspect`.
- Noted no-decay limitation.
- Identified CLI friction.
- Built interactive shell / REPL.
- Preserved one-shot CLI compatibility.
- Added relationship types.
- Added relationship storage.
- Added self-link protection.
- Added relationship duplicate protection.
- Added relationship inspection.
- Fixed `related_to` symmetry.
- Debugged strings, AND/OR logic, `continue`/`return`, and precedence.
- Built direct prerequisite lookup.
- Debugged UUID joining logic.
- Built recursive traversal.
- Added cycle protection.
- Debugged set/list APIs and `append`/`extend`.
- Added `show_prereqs`.
- Wired `prereqs` into CLI.
- Tested upstream prerequisite chains.
- Current next major feature: combine graph structure + mastery evidence for possible gap detection.

# The most important design decisions I made

- Rejecting a generic AI wrapper.
- Rejecting the overly broad adaptive tutoring/problem-generation direction.
- Redefining Lattice as an external knowledge-state graph.
- Keeping the project domain-general.
- Separating:
  - concepts,
  - relationships,
  - evidence.
- Storing raw evidence instead of only final scores.
- Using UUID references rather than names for identity.
- Preserving four mastery dimensions instead of collapsing knowledge into one number.
- Treating the mastery formula as a provisional assumption.
- Keeping some evidence types in history without forcing them into the score.
- Adding an interactive shell because repeated command friction mattered.
- Treating `related_to` as symmetric while keeping other relationships directional.
- Using recursive traversal plus a visited set.
- Separating graph computation from display.
- Keeping the implementation local, small, transparent, and inspectable.

---

# The most important struggles

- Initial coding paralysis:
  - knowing syntax but freezing at project scale.
- Trying to think about the finished system instead of the next behavior.
- Realizing the first adaptive-tutor framing contained vague, computationally undefined assumptions.
- Scope control:
  - refusing to build enormous question-generation infrastructure.
- Limited confidence in the math behind mastery.
- Understanding references by UUID.
- Distinguishing:
  - entity duplication,
  - event repetition.
- Understanding CLI architecture and persistent loops.
- Reasoning about directed vs undirected graph edges.
- Boolean logic:
  - `and`,
  - `or`,
  - parentheses,
  - operator precedence.
- Control flow:
  - `continue` vs `return`.
- Direct graph traversal:
  - locating incoming prerequisite edges.
- Recursion.
- Cycle protection.
- Membership testing in sets.
- List vs set methods.
- `append()` vs `extend()`.
- Function definition syntax vs function-call syntax.
- Correctly capturing function return values.
- Checking `None` vs checking an empty list.

---

# The most important fixes / lessons

- **Break scope down aggressively.**
  - Tiny working behavior first.
- **Define vague product language computationally.**
  - “Know,” “learn,” “master,” “related,” and “prerequisite” all need explicit semantics.
- **Store identity separately from names.**
- **Store raw evidence so conclusions can be recomputed.**
- **Validate input before it corrupts state.**
- **Do not treat every repeated record as a duplicate.**
  - concept and evidence have different semantics.
- **Separate computation from display.**
- **Graph direction must have one consistent meaning.**
- **Symmetric edges need different duplicate semantics than directed edges.**
- **Parentheses matter when Boolean logic becomes nontrivial.**
- **`return` exits a function; `continue` only skips one loop iteration.**
- **Sets are useful for fast membership/cycle detection.**
- **Recursion becomes manageable when expressed as one sentence:**
  - for every prerequisite I find, run the same search from that prerequisite.
- **A working model can still be intellectually honest about its assumptions.**
- **A limitation is not automatically a failure.**
  - If the assumptions are explicit, the limitation becomes something to test next.

---
# Known weaknesses / open modeling questions

### Self-report dependence

- The model is only as good as the user's:
  - self-awareness,
  - honesty,
  - consistency,
  - willingness to log evidence.
- The system does not independently validate the evidence.

### No time decay

- Scores do not currently decay.
- Old evidence remains as influential as recent evidence.
- Timestamps are stored, so a later version can introduce recency.

### Equal treatment within dimensions

- The current formula only uses confidence for strength.
- It does not yet distinguish different contexts inside a dimension.
- Example:
  - one trivial application,
  - one difficult novel application,
  - can currently enter the same `applied` dimension structure if given the same confidence.

### Cross-dimension weighting unresolved

- Study, recall, explanation, and application remain separate.
- There is no composite score.
- A future composite would need a justified weighting scheme.
- The README explicitly notes that application may deserve more weight than study if such a score is ever created.

### Neutral evidence types

- `encountered`, `struggled`, and `forgot` are logged but do not change scores.
- This is a simplification.
- Future versions could make them affect:
  - confidence,
  - recency,
  - mastery decay,
  - uncertainty.

### Graph semantics

- `prerequisite` has traversal logic.
- `part_of` and `related_to` can be stored/displayed but do not yet drive sophisticated graph analysis.
- Relationship correctness still depends on user input.

### Editing / deleting

- Basic user mistakes are not yet fully reversible through dedicated edit/delete commands.
- Current future ideas include:
  - rename concept,
  - delete concept,
  - safely update/delete related references.

Essentially, Lattice cannot:
- Independently determine whether someone truly knows a concept.
- Verify the truth of self-reported evidence.
- Automatically observe learning.
- Automatically generate or grade problems.
- Infer knowledge that the user never logs.
- Establish a scientifically validated mastery score.
- Model forgetting over time.
- Use negative/struggle evidence to reduce mastery.
- Know whether application should count more than study in a validated way.
- Automatically discover relationships.
- Automatically identify all real knowledge gaps yet.
- Claim that the current mastery formula measures cognition in any objective scientific sense.

---

