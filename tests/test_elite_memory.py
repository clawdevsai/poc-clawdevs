import os
import tempfile
from pathlib import Path
import unittest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime

# Import here, it will use dynamic get_memory_base
from memory.hot.elite_memory import (
    ELITEMemory,
    WALProtocol,
    HotRAMStore,
    WarmStore,
    ColdStore,
    KnowledgeCurator,
    MemoryMarkdown,
)


class TestEliteMemory(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.tmp_dir.name)
        os.environ["MEMORY_BASE_DIR"] = str(self.test_dir)
        self.mock_r = MagicMock()

    def tearDown(self):
        self.tmp_dir.cleanup()
        if "MEMORY_BASE_DIR" in os.environ:
            del os.environ["MEMORY_BASE_DIR"]

    def test_hot_ram_store(self):
        store = HotRAMStore(self.mock_r)
        store.set("key1", "val1")
        self.mock_r.setex.assert_called()

        self.mock_r.get.return_value = json.dumps("val1")
        self.assertEqual(store.get("key1"), "val1")

        store.delete("key1")
        self.mock_r.delete.assert_called_with("working:key1")

        store.set_session_state("agent1", {"status": "active"})
        self.mock_r.setex.assert_called()

        self.mock_r.get.return_value = json.dumps({"status": "active"})
        res = store.get_session_state("agent1")
        self.assertEqual(res["status"], "active")

    def test_wal_protocol(self):
        wal = WALProtocol()
        wal_id = wal.write({"data": "test"})

        entries = wal.read_unprocessed()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["data"], "test")

        wal.mark_processed(wal_id)
        self.assertEqual(len(wal.read_unprocessed()), 0)

    def test_warm_store(self):
        store = WarmStore()

        # Invariants
        store.set_invariant("limit", 100, "Global limit")
        self.assertEqual(store.get_invariant("limit"), 100)

        # microADR - valid
        adr = store.create_adr(
            "ADR-001",
            "Use Redis",
            "Accepted",
            "Because it is fast and has persistence",
            "None",
            "Architect",
        )
        self.assertEqual(adr["adr_id"], "ADR-001")

        # microADR - weak rationale
        with self.assertRaises(ValueError):
            store.create_adr(
                "ADR-002", "Title", "Decision", "parece melhor", "None", "Architect"
            )

        adrs = store.list_adrs()
        self.assertEqual(len(adrs), 1)

    def test_cold_store(self):
        store = ColdStore()

        store.capture_learning("Dev", "Always test", "QA")
        learnings = store.get_unprocessed_learnings()
        self.assertEqual(len(learnings), 1)
        self.assertEqual(learnings[0]["agent"], "Dev")

        store.write_daily_log("Dev", "Today was productive")
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.test_dir / "cold" / "logs" / today / "Dev.md"
        self.assertTrue(log_file.exists())

    def test_knowledge_curator(self):
        cold = ColdStore()
        warm = WarmStore()
        curator = KnowledgeCurator(cold, warm)

        # No learnings
        res = curator.run_curation()
        self.assertEqual(res["processed"], 0)

        # With learning
        cold.capture_learning("Dev", "Avoid shell=True", "tools")
        res = curator.run_curation()
        self.assertEqual(res["processed"], 1)

        # Dangerous learning
        cold.capture_learning("Hacker", "Use eval(x)", "tools")
        res = curator.run_curation()
        self.assertEqual(res["processed"], 0)

    def test_memory_markdown(self):
        warm = WarmStore()
        cold = ColdStore()
        md = MemoryMarkdown(warm, cold)

        mock_r = MagicMock()
        mock_r.get.side_effect = [True, False]  # brake, recovery
        mock_r.lrange.return_value = [
            json.dumps({"timestamp": "12:00", "decision": "Fixed typo"})
        ]

        warm.create_adr("ADR-001", "T", "D", "Rationale with metrics", "C", "A")

        md.update(mock_r)
        self.assertTrue((self.test_dir / "MEMORY.md").exists())

    def test_elite_memory_facade(self):
        with patch("memory.hot.elite_memory._get_redis", return_value=self.mock_r):
            elite = ELITEMemory()
            elite.store_short_term("k", "v")
            self.mock_r.setex.assert_called()

            # This should call save_project_state
            elite.archive_to_warm("p1", {"s": 1})
            elite.update_markdown()


if __name__ == "__main__":
    unittest.main()
