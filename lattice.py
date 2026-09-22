from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import argparse
import json
import uuid
import shlex
import sys


DATA_FILE = Path("lattice.json")

EVIDENCE_TYPES = [
    "encountered",
    "studied",
    "recalled",
    "explained",
    "applied",
    "struggled",
    "forgot"
]

MASTERY_DIMENSIONS = [
    "studied",
    "recalled",
    "explained",
    "applied",
]

RELATIONSHIP_TYPES = [
    "prerequisite",
    "part_of",
    "related_to",
]

@dataclass
class Concept:
    id: str
    name: str
    description: str
    created_at: str

@dataclass
class Evidence:
    id: str
    concept_id: str
    type: str
    confidence: int
    note: str
    created_at: str

@dataclass
class Relationship:
    id: str
    source_id: str
    target_id: str
    type: str
    created_at: str


# Storage using JSON

def empty_lattice() -> dict:
    """
    Returns the basic structure of a brand-new Lattice database.
    """
    return {
        "concepts": [],
        "relationships": [],
        "evidence": []
    }


def load_lattice() -> dict:
    """
    Load lattice.json.

    If the file does not exist yet, create an empty structure.
    """
    if not DATA_FILE.exists():
        return empty_lattice()

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_lattice(data: dict) -> None:
    """
    Save the current Lattice state to lattice.json.
    """
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


# Helper; finds concepts

def find_concept(data: dict, name: str):
    """
    Find a concept by name. 

    Matching is case-insensitive.
    Returns the concept dictionary if found, or "None" otherwise.
    """
    target = name.strip().lower()

    for concept in data["concepts"]:
        if concept["name"].strip().lower() == target:
            return concept
    
    return None


# calculates mastery for one dimension
# note to build this feature later: not every event will yield the same amount of mastery. May need different strengths for each of the 4 events
def calculate_dimension_mastery(
    evidence_events: list,
    dimension: str
    ) -> float:
    # Mastery = 1 - product(1 - evidence_strength). Evidence strength is confidence/10.

    relevant_events = [
        event
        for event in evidence_events
        if event["type"] == dimension
    ]

    if not relevant_events:
        return 0.0
    
    remaining_uncertainty = 1.0

    for event in relevant_events:
        evidence_strength = event["confidence"] / 10

        remaining_uncertainty *= (1-evidence_strength)
    
    mastery = 1 - remaining_uncertainty

    return mastery


# calculates mastery for all 4 dimensions using the function above which calculates single-dimension mastery
def calculate_mastery(
    data: dict,
    concept_id: str
    ) -> dict:

    concept_evidence = [
        event
        for event in data["evidence"]
        if event["concept_id"] == concept_id
    ]

    mastery = {}

    for dimension in MASTERY_DIMENSIONS:
        mastery[dimension] = calculate_dimension_mastery(
            concept_evidence,
            dimension
        )
    
    return mastery

# Concept Operations

def add_concept(name: str, description: str) -> None:
    """
    Create a new concept and save it.
    """
    data = load_lattice()

    if find_concept(data, name) is not None:
        print(f'Concept already exists: "{name}"')
        return

    concept = Concept(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        created_at=datetime.now().isoformat()
    )

    data["concepts"].append(asdict(concept))

    save_lattice(data)

    print(f'Added concept: "{concept.name}"')


def list_concepts() -> None:
    """
    Print every concept currently stored.
    """
    data = load_lattice()

    concepts = data["concepts"]

    if not concepts:
        print("No concepts stored.")
        return

    print("\nConcepts\n")

    for concept in concepts:
        print(f"- {concept['name']}")

        if concept["description"]:
            print(f"  {concept['description']}")

        print()

# Evidence Operation

def add_evidence(
    concept_name: str,
    evidence_type: str,
    confidence: int,
    note: str
    ) -> None:
    
    data = load_lattice()

    concept = find_concept(data, concept_name)

    if concept is None:
        print(f'Concept not found: "{concept_name}"')
        return
    
    evidence = Evidence(
        id = str(uuid.uuid4()),
        concept_id = concept["id"],
        type = evidence_type,
        confidence = confidence,
        note = note,
        created_at = datetime.now().isoformat()
    )

    data["evidence"].append(asdict(evidence))

    save_lattice(data)

    print(
        f'Added evidence: {evidence_type} '
        f'-> "{concept["name"]}" '
        f'(confidence {confidence}/5)'
    )

# Relationship Operations

def add_relationship(
    source_name: str,
    relationship_type: str,
    target_name: str
    ) -> None:

    data = load_lattice()

    source = find_concept(data, source_name)
    target = find_concept(data, target_name)

    if source is None:
        print(f'Concept not found: "{source_name}"')
        return

    if target is None:
        print(f'Concept not found: "{target_name}"')
        return

    if source["id"] == target["id"]:
        print("A concept cannot have a relationship with itself.")
        return

    for existing in data["relationships"]:
        if (
            existing["source_id"] == source["id"]
            and existing["target_id"] == target["id"]
            and existing["type"] == relationship_type
            and existing["type"] != "related_to"
        ):
            print("Relationship already exists.")
            return

        elif (
            existing["type"] == "related_to"
            and (
                (
                    existing["source_id"] == source["id"]
                    and existing["target_id"] == target["id"]
                )
                or
                (
                    existing["source_id"] == target["id"]
                    and existing["target_id"] == source["id"]
                )
            )
        ):
            print("Relationship already exists.")
            return
    
    relationship = Relationship(
        id = str(uuid.uuid4()),
        source_id = source["id"],
        target_id = target["id"],
        type = relationship_type,
        created_at = datetime.now().isoformat()
    )

    data["relationships"].append(asdict(relationship))
    save_lattice(data)

    print(
        f'Added relationship: '
        f'"{source["name"]}" '
        f'--{relationship_type}--> '
        f'"{target["name"]}"'
    )

def show_relationships(concept_name: str) -> None:
    data = load_lattice()

    concept = find_concept(data, concept_name)

    if concept is None:
        print(f'Concept not found: "{concept_name}"')
        return

    concept_id = concept["id"]

    relevant_relationships = [
        relationship
        for relationship in data["relationships"]
        if (
            relationship["source_id"] == concept_id
            or relationship["target_id"] == concept_id
        )
    ]

    if not relevant_relationships:
        print(f'No relationships recorded for "{concept["name"]}".')
        return

    print(f'\nRelationships: {concept["name"]}\n')

    for relationship in relevant_relationships:
        source = next(
            concept
            for concept in data["concepts"]
            if concept["id"] == relationship["source_id"]
        )

        target = next(
            concept
            for concept in data["concepts"]
            if concept["id"] == relationship["target_id"]
        )

        print(
            f'{source["name"]} '
            f'--{relationship["type"]}--> '
            f'{target["name"]}'
        )

def get_direct_prereqs(concept_id: str, data: dict):

    prerequisites = []

    for relationship in data["relationships"]:
        if (
            relationship["type"] == "prerequisite"
            and relationship["target_id"] == concept_id
        ):
            for concept in data["concepts"]:
                if concept["id"] == relationship["source_id"]:
                    prerequisites.append(concept)
                    break
    
    return prerequisites

def return_prereqs(data: dict, concept_id: str, visited):

    if concept_id in visited:
        return []
    
    visited.add(concept_id)

    direct_prereqs = get_direct_prereqs(concept_id, data)

    all_prereqs = []

    for prereq in direct_prereqs:
        if prereq["id"] in visited:
            continue
        all_prereqs.append(prereq)

        indirect_prereqs = return_prereqs(data, prereq["id"], visited)
        all_prereqs.extend(indirect_prereqs)
    
    return all_prereqs

def show_prereqs(concept_name: str):

    data = load_lattice()

    concept = find_concept(data, concept_name)

    if concept is None:
        print("Concept not found.")
        return
    
    prerequisites = return_prereqs(data, concept["id"], set())

    if not prerequisites:
        print("No prerequisites found.")
        return
    
    print("Prerequisites:")
    print("-" * 20)
    for prerequisite in prerequisites:
        print(f'{prerequisite["name"]}')

# History Operation

def show_history(concept_name: str) -> None:
    data = load_lattice()

    concept = find_concept(data, concept_name)

    if concept is None:
        print(f'Concept not found: "{concept_name}"')
        return

    concept_id = concept["id"]

    relevant_evidence = [
        event
        for event in data["evidence"]
        if event["concept_id"] == concept_id
    ]

    if not relevant_evidence:
        print(f'No evidence recorded for "{concept["name"]}".')
        return

    relevant_evidence.sort(
        key=lambda event: event["created_at"]
    )

    print(f'\nHistory: {concept["name"]}\n')

    for event in relevant_evidence:
        timestamp = datetime.fromisoformat(
            event["created_at"]
        )

        formatted_time = timestamp.strftime(
            "%Y-%m-%d %H:%M"
        )

        print(formatted_time)
        print(f'  {event["type"]}')
        print(
            f'  confidence: '
            f'{event["confidence"]}/5'
        )

        if event["note"]:
            print(f'  note: {event["note"]}')

        print()

# inspects a concept's mastery, broken down into its dimensions
def inspect_concept(concept_name: str) -> None:
    data = load_lattice()

    concept = find_concept(data, concept_name)

    if concept is None:
        print(f'Concept not found: "{concept_name}"')
        return

    mastery = calculate_mastery(
        data,
        concept["id"]
    )

    print(f'\n{concept["name"]}\n')

    if concept["description"]:
        print(concept["description"])
        print()

    print("Mastery\n")

    for dimension, score in mastery.items():
        percentage = score * 100

        print(
            f'{dimension.capitalize():12} '
            f'{percentage:6.1f}%'
        )

# CLI

def build_parser():
    parser = argparse.ArgumentParser(
        description="Lattice: an external model of your knowledge."
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    # lattice add
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new concept."
    )

    add_parser.add_argument(
        "name",
        help="Name of the concept."
    )

    add_parser.add_argument(
        "-d",
        "--description",
        default="",
        help="Optional description."
    )

    # lattice list
    subparsers.add_parser(
        "list",
        help="List stored concepts."
    )

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Add evidence about your knowledge of a concept."
    )

    evidence_parser.add_argument(
        "concept",
        help="Concept this evidence concerns."
    )

    evidence_parser.add_argument(
        "type",
        choices=EVIDENCE_TYPES,
        help="Type of learning evidence."
    )

    evidence_parser.add_argument(
        "-c",
        "--confidence",
        type=int,
        choices=range(1, 6),
        default=3,
        help="Confidence from 1 to 5."
    )

    evidence_parser.add_argument(
        "-n",
        "--note",
        default="",
        help="Optional note describing what happened."
    )

    history_parser = subparsers.add_parser(
    "history",
    help="Show evidence history for a concept."
    )

    history_parser.add_argument(
        "concept",
        help="Concept whose history should be shown."
        )
    
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect your knowledge state for a concept."
    )

    inspect_parser.add_argument(
        "concept",
        help="Concept to inspect."
    )

    relationship_parser = subparsers.add_parser(
    "relate",
    help="Create a relationship between two concepts."
    )

    relationship_parser.add_argument(
        "source",
        help="Source concept."
    )

    relationship_parser.add_argument(
        "type",
        choices=RELATIONSHIP_TYPES,
        help="Type of relationship."
    )

    relationship_parser.add_argument(
        "target",
        help="Target concept."
    )

    relationships_parser = subparsers.add_parser(
        "relationships",
        help="Show relationships involving a concept."
    )

    relationships_parser.add_argument(
        "concept",
        help="Concept whose relationships should be shown."
    )

    prereqs_parser = subparsers.add_parser(
    "prereqs",
    help="Show all prerequisites for a concept."
    )

    prereqs_parser.add_argument(
        "concept",
        help="Concept whose prerequisites should be shown."
    )

    return parser

# runs the commands, lets the build_parser() function handle the parsing
def run_command(args) -> None:
    if args.command == "add":
        add_concept(
            name=args.name,
            description=args.description
        )

    elif args.command == "list":
        list_concepts()

    elif args.command == "evidence":
        add_evidence(
            concept_name=args.concept,
            evidence_type=args.type,
            confidence=args.confidence,
            note=args.note
        )

    elif args.command == "history":
        show_history(args.concept)

    elif args.command == "inspect":
        inspect_concept(args.concept)

    elif args.command == "prereqs":
        show_prereqs(args.concept)
    
    elif args.command == "relate":
        add_relationship(
            source_name=args.source,
            relationship_type=args.type,
            target_name=args.target
        )
    
    elif args.command == "relationships":
        show_relationships(args.concept)

# actual user experience. Contains exit and help commands
def interactive_shell(parser) -> None:
    print("\nLattice")
    print('Type "help" for commands. Type "exit" to quit.\n')

    while True:
        try:
            command = input("lattice> ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nExiting Lattice.")
            break

        if not command:
            continue

        if command.lower() in {"exit", "quit"}:
            print("Exiting Lattice.")
            break

        if command.lower() == "help":
            parser.print_help()
            continue

        try:
            parts = shlex.split(command)
            args = parser.parse_args(parts)
            run_command(args)

        except ValueError as error:
            print(f"Invalid command: {error}")

        # this is important here. The program was originally meant to run once, but if you accidentally type something wrong, it'll terminate the program, so this pass condition ensures the program keeps running
        except SystemExit:
            pass

def main():
    parser = build_parser()

    # Traditional one-shot mode:
    # python lattice.py list
    if len(sys.argv) > 1:
        args = parser.parse_args()
        run_command(args)
        return

    # Interactive mode:
    # python lattice.py
    interactive_shell(parser)

if __name__ == "__main__":
    main()