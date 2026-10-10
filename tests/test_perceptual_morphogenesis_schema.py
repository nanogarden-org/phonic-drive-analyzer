import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "perceptual-morphogenesis-v1.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "annotations" / "perceptual_morphogenesis.example.yaml"


def test_perceptual_morphogenesis_example_matches_versioned_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    example = yaml.safe_load(EXAMPLE_PATH.read_text(encoding="utf-8"))

    errors = list(Draft202012Validator(schema).iter_errors(example))
    assert not errors, "\n".join(error.message for error in errors)

    event = example["listening_sessions"][0]["events"][0]
    assert set(event["dimensions"]) == {
        "particle_field",
        "aggregation",
        "topology",
        "growth",
        "transformation",
        "color_texture",
        "persistence",
    }
