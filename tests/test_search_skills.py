import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = str(REPO / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from search_skills import tokenize_normalized, WeightedBM25

class TestSearchSkills(unittest.TestCase):
    def test_token_normalization(self):
        # camelCase
        self.assertEqual(tokenize_normalized("dockerCompose"), ["docker", "compose"])
        # snake_case & kebab-case
        self.assertEqual(tokenize_normalized("deep_research_v2"), ["deep", "research", "v2"])
        self.assertEqual(tokenize_normalized("nextjs-15-expert"), ["nextjs", "15", "expert"])
        # punctuation & casing
        self.assertEqual(tokenize_normalized("Postgres / SQL (v16.0)"), ["postgres", "sql", "v16"])

    def test_bm25_exact_match_boost(self):
        mock_skills = {
            "docker-patterns": {
                "name": "docker-patterns",
                "tags": ["docker", "containers"],
                "description": "Docker container patterns and compose files."
            },
            "unrelated-skill": {
                "name": "unrelated-skill",
                "tags": ["python"],
                "description": "Unrelated python development workflows."
            }
        }
        index = WeightedBM25(mock_skills)
        results = index.query("docker-patterns", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0][1]["name"], "docker-patterns")

    def test_camel_case_query_hit(self):
        mock_skills = {
            "docker-patterns": {
                "name": "docker-patterns",
                "tags": ["docker", "containers"],
                "description": "Docker container patterns and compose files."
            },
            "other": {
                "name": "other",
                "tags": ["other"],
                "description": "Something else entirely."
            }
        }
        index = WeightedBM25(mock_skills)
        results = index.query("dockerCompose", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1]["name"], "docker-patterns")

if __name__ == "__main__":
    unittest.main()
