#!/usr/bin/env python3
"""Smoke tests for queue discovery and channel separation."""

import unittest

import autopost


class AutoPostSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.queue = autopost.build_queue()

    def test_discovers_all_episodes(self) -> None:
        self.assertEqual(len(self.queue["jobs"]), 41)

    def test_channel_split(self) -> None:
        kid = [job for job in self.queue["jobs"] if job["channel_group"] == "kid"]
        history = [job for job in self.queue["jobs"] if job["channel_group"] == "history"]
        self.assertEqual(len(kid), 26)
        self.assertEqual(len(history), 15)

    def test_lowercase_wwii_soldier_metadata_is_normalized(self) -> None:
        jobs = {job["job_id"]: job for job in self.queue["jobs"]}
        job = jobs["history-wwii-soldier-pov-ep01"]
        self.assertEqual(job["series_id"], "wwii-soldier-pov")
        self.assertEqual(job["episode"], 1)
        self.assertEqual(job["title_th"], "WWII Soldier POV: D-Day at Omaha Beach")
        self.assertEqual(set(job["platform_runs"]), {"youtube", "youtube_shorts"})

    def test_every_job_targets_only_approved_platforms(self) -> None:
        expected = {"youtube", "youtube_shorts"}
        for job in self.queue["jobs"]:
            self.assertEqual(set(job["platform_runs"]), expected)

    def test_disabled_platforms_are_removed_from_existing_jobs(self) -> None:
        for job in self.queue["jobs"]:
            self.assertNotIn("tiktok", job["platform_runs"])
            self.assertNotIn("facebook_reels", job["platform_runs"])

    def test_approved_and_published_jobs_are_not_blocked(self) -> None:
        for job in self.queue["jobs"]:
            if job["job_id"] in {"kid-block-tales-ep02", "kid-block-tales-ep03"}:
                self.assertEqual(job["status"], "PUBLISHED")
                self.assertEqual(job["readiness"]["blockers"], [])
                continue
            self.assertEqual(job["status"], "WAITING_ASSETS")
            self.assertIn("metadata_not_approved", job["readiness"]["blockers"])

    def test_normal_sync_preserves_schedule(self) -> None:
        before = {job["job_id"]: job["scheduled_at"] for job in self.queue["jobs"]}
        refreshed = autopost.build_queue()
        after = {job["job_id"]: job["scheduled_at"] for job in refreshed["jobs"]}
        self.assertEqual(before, after)

    def test_payload_includes_channel_compliance(self) -> None:
        kid_payload = autopost.build_publish_payload(
            "kid-minecraft-adventures-ep01", "youtube"
        )
        history_payload = autopost.build_publish_payload(
            "history-wwii-untold-stories-ep01", "youtube"
        )
        self.assertTrue(kid_payload["options"]["self_declared_made_for_kids"])
        self.assertFalse(history_payload["options"]["self_declared_made_for_kids"])
        self.assertTrue(kid_payload["options"]["contains_synthetic_media"])


if __name__ == "__main__":
    unittest.main()
