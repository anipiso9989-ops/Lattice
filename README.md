# Lattice

Lattice is a small Python project that turns my ideas about learning and knowledge into a working system.

## The Ideas

I began with a question:

> What would it mean to represent what a person knows, rather than simply storing what they have read?

From that question, I developed several connected ideas:

- **Knowledge can be represented as a graph.**  
  Concepts are nodes, and relationships between them are edges.

- **Knowledge is built from atomic concepts.**  
  A large idea can be broken into smaller, understandable units that can be combined into larger structures.

- **Knowledge has prerequisites.**  
  Complex concepts depend on simpler ones. Understanding calculus, for example, depends on earlier mathematical concepts.

- **Learning should be demonstrated through evidence.**  
  Exposure alone does not prove learning. Applying, explaining, recalling, and studying an idea provide different kinds of evidence.

- **Mastery is multidimensional.**  
  Someone may have studied a concept without being able to explain or apply it. These should not be collapsed into one simplistic score.

These ideas began as notes and theories in my personal knowledge system. Lattice is my attempt to make them operational.

## The Physical Representation

Lattice is a command-line application written in Python. It stores its data in a local JSON file and currently supports:

- Creating and listing concepts
- Recording evidence of learning
- Tracking confidence and notes
- Viewing an evidence history
- Calculating separate mastery scores for studying, recalling, explaining, and applying
- Creating relationships between concepts
- Representing prerequisites
- Recursively finding the prerequisites of a concept
- Running either as a traditional command-line program or an interactive shell

For example:

```text
add "Algebra"
add "Calculus"
relate "Algebra" prerequisite "Calculus"
evidence "Algebra" studied -c 5
evidence "Algebra" explained -c 4
inspect "Algebra"
prereqs "Calculus"
```

The program does not store a permanent mastery label. Instead, it stores raw evidence and derives the current knowledge state from that evidence. This preserves the distinction between what happened and what the system currently infers.

## Idea -> Application

The intellectual work came first: defining concepts, relationships, prerequisites, evidence, and mastery.

The engineering work was translating those abstractions into concrete structures:

- `Concept`, `Evidence`, and `Relationship` data models
- UUID-based identity
- JSON persistence
- Graph traversal
- Recursive prerequisite discovery
- A diminishing-returns mastery calculation
- A usable interactive interface

Lattice is intentionally small, but it represents a complete cycle:

> **Idea → Model → Implementation → Feedback**

I am using the project to explore whether theories about learning, cognition, and structured knowledge can become useful computational systems. The current version is only the beginning. For example, the next step is gap detection: identifying which prerequisites are weak or missing before attempting to master a more advanced concept.
