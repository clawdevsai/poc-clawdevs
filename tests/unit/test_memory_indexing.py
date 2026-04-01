"""
Unit Tests for Memory Indexing Service - Phase 4 Task 1
Testa func\u00f5es individuais de indexing e busca.
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

# Import the service
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../control-panel/backend"))

from app.services.memory_indexing import MemoryIndexingService


class TestMemoryIndexing(unittest.TestCase):
    """Test suite for MemoryIndexingService."""

    def setUp(self):
        """Criar temporary directory para testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_memory.db")
        self.service = MemoryIndexingService(memory_root=self.temp_dir)
        self.service.index_db = Path(self.temp_db)

    def tearDown(self):
        """Limpar temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_database_initialization(self):
        """Test que database \u00e9 criado corretamente."""
        self.service._init_database()
        self.assertTrue(self.service.index_db.exists())

    def test_file_hashing(self):
        """Test que hash_file gera hashes \u00fanicos."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")

        hash1 = self.service._hash_file(test_file)
        hash2 = self.service._hash_file(test_file)

        # Should be deterministic
        self.assertEqual(hash1, hash2)

        # Modify file should change hash
        test_file.write_text("different content")
        hash3 = self.service._hash_file(test_file)
        self.assertNotEqual(hash1, hash3)

    def test_excerpt_extraction(self):
        """Test que _extract_excerpt retorna trecho relevante."""
        content = "Lorem ipsum dolor sit amet. KEYWORD here. Consectetur adipiscing."
        excerpt = self.service._extract_excerpt(content, "KEYWORD", context_length=50)

        self.assertIn("KEYWORD", excerpt)
        self.assertLess(len(excerpt), len(content))

    def test_excerpt_extraction_no_match(self):
        """Test que excerpt_extraction retorna primeira parte se n\u00e3o encontrar match."""
        content = "Lorem ipsum dolor sit amet consectetur adipiscing elit."
        excerpt = self.service._extract_excerpt(content, "NONEXISTENT", context_length=20)

        self.assertTrue(len(excerpt) > 0)
        self.assertIn("Lorem", excerpt)

    def test_cache_freshness_check(self):
        """Test que _check_cache valida freshness corretamente."""
        cache_status = self.service._check_cache("test_agent", Path(self.temp_dir) / "nonexistent.md")
        self.assertFalse(cache_status.get("is_fresh"))

    def test_memory_indexing_missing_file(self):
        """Test que index_memory retorna erro para arquivo inexistente."""
        result = self.service.index_memory("nonexistent_agent")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["error"])

    def test_memory_indexing_success(self):
        """Test que index_memory funciona com arquivo v\u00e1lido."""
        # Create test memory directory and file
        agent_dir = Path(self.temp_dir) / "test_agent"
        agent_dir.mkdir()
        memory_file = agent_dir / "MEMORY.md"
        memory_file.write_text("---\nname: test\ntype: user\n---\n\nTest memory content")

        # Initialize database
        self.service._init_database()

        # Index memory
        result = self.service.index_memory("test_agent")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["agent_id"], "test_agent")
        self.assertGreater(result["memory_size_bytes"], 0)
        self.assertGreater(result["token_estimate"], 0)
        self.assertGreater(result["compression_ratio"], 0)

    def test_metrics_calculation(self):
        """Test que get_metrics calcula corretamente."""
        self.service._init_database()

        # Create test data
        agent_dir = Path(self.temp_dir) / "agent1"
        agent_dir.mkdir()
        memory_file = agent_dir / "MEMORY.md"
        memory_file.write_text("Test content for metrics")

        self.service.index_memory("agent1")

        metrics = self.service.get_metrics()

        self.assertEqual(metrics["status"], "success")
        self.assertGreaterEqual(metrics["total_indexed_agents"], 0)
        self.assertGreaterEqual(metrics["total_memory_size_bytes"], 0)


class TestMemoryIndexingSearch(unittest.TestCase):
    """Test suite for memory search functionality."""

    def setUp(self):
        """Setup para testes de search."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_search.db")
        self.service = MemoryIndexingService(memory_root=self.temp_dir)
        self.service.index_db = Path(self.temp_db)

    def tearDown(self):
        """Limpar files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_search_empty_index(self):
        """Test que search em index vazio retorna sucesso com 0 resultados."""
        self.service._init_database()
        result = self.service.search("nonexistent query")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result_count"], 0)
        self.assertEqual(len(result["results"]), 0)


if __name__ == "__main__":
    unittest.main()
