import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import youtube_publisher


class YouTubePublisherTests(unittest.TestCase):
    def test_missing_credentials_are_reported_without_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            status = youtube_publisher.credential_status(Path(directory) / "missing.json")
        self.assertFalse(status["configured"])
        self.assertNotIn("client_secret", status)
        self.assertNotIn("refresh_token", status)

    def test_channel_mismatch_blocks_before_upload(self) -> None:
        job = {"status": "READY", "channel_group": "kid"}
        payload = {"options": {"privacy_status": "private"}}
        channels = {"channels": {"kid": {"youtube_channel_id": "EXPECTED"}}}
        with patch.object(youtube_publisher.autopost, "load_queue", return_value={}), patch.object(
            youtube_publisher.autopost, "find_job", return_value=job
        ), patch.object(youtube_publisher.autopost, "build_publish_payload", return_value=payload), patch.object(
            youtube_publisher, "load_credentials", return_value={"client_id": "id", "client_secret": "secret", "refresh_token": "refresh"}
        ), patch.object(youtube_publisher, "refresh_access_token", return_value="access"), patch.object(
            youtube_publisher, "authenticated_channel", return_value={"id": "OTHER", "title": "Wrong"}
        ), patch.object(youtube_publisher.autopost, "load_config", return_value=(channels, {})), patch.object(
            youtube_publisher, "_upload_resumable"
        ) as upload:
            with self.assertRaisesRegex(youtube_publisher.YouTubePublisherError, "YOUTUBE_CHANNEL_SCOPE_MISMATCH"):
                youtube_publisher.publish_private("job")
        upload.assert_not_called()

    def test_success_records_one_video_for_youtube_and_shorts(self) -> None:
        job = {"status": "READY", "channel_group": "kid"}
        payload = {"options": {"privacy_status": "private"}}
        channels = {"channels": {"kid": {"youtube_channel_id": "EXPECTED"}}}
        results = [{"status": "PARTIAL"}, {"status": "PUBLISHED"}]
        with patch.object(youtube_publisher.autopost, "load_queue", return_value={}), patch.object(
            youtube_publisher.autopost, "find_job", return_value=job
        ), patch.object(youtube_publisher.autopost, "build_publish_payload", return_value=payload), patch.object(
            youtube_publisher, "load_credentials", return_value={"client_id": "id", "client_secret": "secret", "refresh_token": "refresh"}
        ), patch.object(youtube_publisher, "refresh_access_token", return_value="access"), patch.object(
            youtube_publisher, "authenticated_channel", return_value={"id": "EXPECTED", "title": "CubeLoom Adventures"}
        ), patch.object(youtube_publisher.autopost, "load_config", return_value=(channels, {})), patch.object(
            youtube_publisher, "_upload_resumable", return_value={"id": "video123"}
        ), patch.object(youtube_publisher.autopost, "claim_job"), patch.object(
            youtube_publisher.autopost, "update_job_status"
        ), patch.object(youtube_publisher.autopost, "record_platform_result", side_effect=results) as record:
            result = youtube_publisher.publish_private("job")
        self.assertEqual(result["video_id"], "video123")
        self.assertEqual(result["privacy_status"], "private")
        self.assertEqual([call.args[1] for call in record.call_args_list], ["youtube", "youtube_shorts"])

    def test_explicit_target_channel_overrides_series_default_and_applies_target_policy(self) -> None:
        job = {"status": "READY", "channel_group": "kid"}
        payload = {"options": {"privacy_status": "private", "self_declared_made_for_kids": True}}
        channels = {"channels": {
            "kid": {"display_name": "CubeLoom Adventures", "youtube_channel_id": "KID"},
            "history": {
                "display_name": "War & History Vault", "youtube_channel_id": "HISTORY",
                "publishing_policy": {"youtube_category_id": "27", "youtube_made_for_kids": False},
            },
        }}
        results = [{"status": "PARTIAL"}, {"status": "PUBLISHED"}]
        with patch.object(youtube_publisher.autopost, "load_queue", return_value={}), patch.object(
            youtube_publisher.autopost, "find_job", return_value=job
        ), patch.object(youtube_publisher.autopost, "build_publish_payload", return_value=payload), patch.object(
            youtube_publisher, "load_credentials", return_value={"client_id": "id", "client_secret": "secret", "refresh_token": "refresh"}
        ), patch.object(youtube_publisher, "refresh_access_token", return_value="access"), patch.object(
            youtube_publisher, "authenticated_channel", return_value={"id": "HISTORY", "title": "War & History Vault"}
        ), patch.object(youtube_publisher.autopost, "load_config", return_value=(channels, {})), patch.object(
            youtube_publisher, "_upload_resumable", return_value={"id": "video456"}
        ) as upload, patch.object(youtube_publisher.autopost, "claim_job"), patch.object(
            youtube_publisher.autopost, "update_job_status"
        ), patch.object(youtube_publisher.autopost, "record_platform_result", side_effect=results):
            result = youtube_publisher.publish_private(
                "job", target_channel_group="history", target_youtube_channel_id="HISTORY",
                target_youtube_channel_name="War & History Vault",
            )
        self.assertEqual(result["channel_group"], "history")
        self.assertFalse(upload.call_args.args[1]["options"]["self_declared_made_for_kids"])
        self.assertEqual(upload.call_args.args[1]["options"]["category_id"], "27")

    def test_explicit_target_contract_mismatch_blocks_before_oauth_and_upload(self) -> None:
        job = {"status": "READY", "channel_group": "kid"}
        channels = {"channels": {"history": {
            "display_name": "War & History Vault", "youtube_channel_id": "HISTORY",
        }}}
        with patch.object(youtube_publisher.autopost, "load_queue", return_value={}), patch.object(
            youtube_publisher.autopost, "find_job", return_value=job
        ), patch.object(youtube_publisher.autopost, "load_config", return_value=(channels, {})), patch.object(
            youtube_publisher, "load_credentials"
        ) as credentials, patch.object(youtube_publisher, "_upload_resumable") as upload:
            with self.assertRaisesRegex(youtube_publisher.YouTubePublisherError, "YOUTUBE_TARGET_CHANNEL_CONTRACT_MISMATCH"):
                youtube_publisher.publish_private(
                    "job", target_channel_group="history", target_youtube_channel_id="WRONG",
                    target_youtube_channel_name="War & History Vault",
                )
        credentials.assert_not_called()
        upload.assert_not_called()


if __name__ == "__main__":
    unittest.main()
