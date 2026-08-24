#!/usr/bin/env python3

import unittest
from pathlib import Path
from unittest.mock import patch

import flow_runner


class FlowRunnerTests(unittest.TestCase):
    def test_rejects_paths_outside_workspace(self) -> None:
        with self.assertRaisesRegex(flow_runner.FlowRunnerError, "OUTSIDE_WORKSPACE"):
            flow_runner._safe_path("../Access_Key.txt")

    def test_ep03_contract_is_product_scoped(self) -> None:
        contract = flow_runner._job_contract("kid-block-tales-ep03")
        self.assertEqual(contract["content_id"], "block-tales-ep03")
        self.assertEqual(Path(contract["source_path"]).name, "STEP6.json")
        self.assertEqual(contract["channel_group"], "kid")

    def test_flow_url_targets_the_ppmovie_studio_tool(self) -> None:
        self.assertIn("/project/7c7bdbb9-b431-4ad8-a2d7-0597f685b5fe/", flow_runner.FLOW_URL)
        self.assertIn("/tool-version/c137fec7-6ff7-41eb-8d93-784d1d54c03c", flow_runner.FLOW_URL)

    def test_unknown_action_is_rejected_before_side_effect(self) -> None:
        with self.assertRaisesRegex(flow_runner.FlowRunnerError, "NOT_ALLOWLISTED"):
            flow_runner.dispatch("kid-block-tales-ep03", "DELETE_ALL")

    def test_worker_uses_step6_for_images_and_blocks_export_without_videos(self) -> None:
        worker = flow_runner.WORKER.read_text(encoding="utf-8")
        self.assertIn('"STEP\\\\s*06|สร้างหนัง", "STEP_06"', worker)
        self.assertNotIn('"STEP\\\\s*05|ตัวละคร", "STEP_05"', worker)
        self.assertIn("FLOW_IMAGES_NOT_READY_FOR_VIDEO", worker)
        self.assertIn("FLOW_VIDEOS_NOT_READY_FOR_EXPORT", worker)
        self.assertIn('"สร้างวิดีโอ|generate video", "ทั้งหมด|all"', worker)
        self.assertIn('"ส่งออกรวมคลิป|export full clip|export clip"', worker)
        self.assertLess(worker.index("await verifyImagesReady(cdp, contextMap);"), worker.index("GENERATE_ALL_VIDEOS"))
        self.assertLess(worker.index("await verifyVideosReadyForExport(cdp, contextMap);"), worker.index("CREATE_COVER"))


if __name__ == "__main__":
    unittest.main()
