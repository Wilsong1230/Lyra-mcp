from unittest.mock import MagicMock, patch
import httpx


def mock_response(data):
    m = MagicMock(spec=httpx.Response)
    m.json.return_value = data
    m.raise_for_status.return_value = None
    return m


@patch("mcp_server.httpx.post")
def test_set_emotion_valid(mock_post):
    mock_post.return_value = mock_response({"state": "thinking", "color": "#9B59FF"})
    from mcp_server import set_emotion
    result = set_emotion("thinking")
    assert "thinking" in result
    assert "#9B59FF" in result


@patch("mcp_server.httpx.post")
def test_set_emotion_service_down(mock_post):
    mock_post.side_effect = httpx.ConnectError("refused")
    from mcp_server import set_emotion
    result = set_emotion("idle")
    assert "Error" in result


@patch("mcp_server.httpx.get")
def test_get_state_returns_current(mock_get):
    mock_get.return_value = mock_response({"state": "curious", "color": "#00D4FF"})
    from mcp_server import get_state
    result = get_state()
    assert "curious" in result
    assert "#00D4FF" in result


@patch("mcp_server.httpx.get")
def test_get_state_service_down(mock_get):
    mock_get.side_effect = httpx.ConnectError("refused")
    from mcp_server import get_state
    result = get_state()
    assert "Error" in result


@patch("mcp_server.httpx.post")
def test_speak_returns_confirmation(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp
    from mcp_server import speak
    result = speak("Hello, this is Lyra.")
    assert "Hello, this is Lyra." in result


@patch("mcp_server.httpx.post")
def test_speak_service_down(mock_post):
    mock_post.side_effect = httpx.ConnectError("refused")
    from mcp_server import speak
    result = speak("Hello.")
    assert "Error" in result


@patch("mcp_server.httpx.post")
def test_transcribe_returns_text(mock_post, tmp_path):
    mock_post.return_value = mock_response({"text": "hello world"})
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"RIFF" + b"\x00" * 36)
    from mcp_server import transcribe
    result = transcribe(str(audio_file))
    assert "hello world" in result
    # Verify it called lyra-listen (port 8002), not lyra-voice (port 8001)
    call_url = mock_post.call_args[0][0]
    assert "8002" in call_url


def test_transcribe_missing_file():
    from mcp_server import transcribe
    result = transcribe("/nonexistent/path.wav")
    assert "Error" in result


@patch("mcp_server.httpx.get")
def test_list_voices_returns_names(mock_get):
    mock_get.return_value = mock_response({"voices": ["bf_emma", "bm_george"]})
    from mcp_server import list_voices
    result = list_voices()
    assert "bf_emma" in result
    assert "bm_george" in result
