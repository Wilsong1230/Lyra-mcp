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
