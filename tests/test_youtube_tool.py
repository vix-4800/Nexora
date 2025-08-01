from unittest.mock import patch

# fmt: off
# isort: off
from agent.tools.researcher.summarize_text_tool import summarize_text_tool
from agent.tools.researcher.summarize_youtube_tool import (
    extract_video_id,
    summarize_youtube_tool,
)
# isort: on
# fmt: on


class TestYouTubeTool:
    def test_extract_video_id(self):
        vid = extract_video_id("https://www.youtube.com/watch?v=abc123xyz12")
        assert vid == "abc123xyz12"

    def test_summarize_text(self):
        summary = summarize_text_tool.func(text="One. Two. Three.", sentences=2)
        assert summary == "One. Two."

    @patch("youtube_transcript_api.YouTubeTranscriptApi.fetch")
    def test_summarize_youtube(self, mock_get):
        mock_get.return_value = [
            {"text": "Hello world."},
            {"text": "Second sentence."},
        ]
        summary = summarize_youtube_tool.func(
            "https://youtu.be/abc123xyz12", sentences=1
        )
        assert summary == "Hello world."

    @patch("youtube_transcript_api.YouTubeTranscriptApi.fetch")
    def test_summarize_youtube_snippets(self, mock_get):
        from youtube_transcript_api import _transcripts

        snippet1 = _transcripts.FetchedTranscriptSnippet("Hello world.", 0, 1)
        snippet2 = _transcripts.FetchedTranscriptSnippet("Second sentence.", 1, 1)
        fetched = _transcripts.FetchedTranscript(
            [snippet1, snippet2], "abc123xyz12", "English", "en", True
        )
        mock_get.return_value = fetched

        summary = summarize_youtube_tool.func(
            "https://youtu.be/abc123xyz12", sentences=1
        )
        assert summary == "Hello world."
