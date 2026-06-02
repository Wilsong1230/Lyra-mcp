from __future__ import annotations

import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lyra")

EMBODIMENT_URL = os.getenv("EMBODIMENT_URL", "http://localhost:8000")
VOICE_URL = os.getenv("VOICE_URL", "http://localhost:8001")


@mcp.tool()
def set_emotion(state: str) -> str:
    """Set the emotional state of the Lyra avatar."""
    try:
        data = httpx.post(f"{EMBODIMENT_URL}/state", json={"state": state}, timeout=5).json()
        return f"State set to '{data['state']}' (color: {data['color']})"
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return f"Error: could not reach lyra-embodiment — {e}"


@mcp.tool()
def get_state() -> str:
    """Get the current emotional state of the Lyra avatar."""
    try:
        data = httpx.get(f"{EMBODIMENT_URL}/state", timeout=5).json()
        return f"Current state: '{data['state']}' (color: {data['color']})"
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return f"Error: could not reach lyra-embodiment — {e}"


@mcp.tool()
def speak(text: str, sync_emotion: bool = True) -> str:
    """Speak text aloud using Lyra's voice. Optionally syncs avatar emotion state."""
    try:
        resp = httpx.post(
            f"{VOICE_URL}/speak",
            json={"text": text, "sync_emotion": sync_emotion},
            timeout=30,
        )
        resp.raise_for_status()
        return f"Spoke: {text!r}"
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return f"Error: could not reach lyra-voice — {e}"


@mcp.tool()
def transcribe(audio_path: str) -> str:
    """Transcribe a local audio file to text using Whisper."""
    try:
        with open(audio_path, "rb") as f:
            resp = httpx.post(f"{VOICE_URL}/transcribe", files={"file": f}, timeout=60)
        resp.raise_for_status()
        return resp.json()["text"]
    except FileNotFoundError:
        return f"Error: file not found — {audio_path}"
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return f"Error: could not reach lyra-voice — {e}"


@mcp.tool()
def list_voices() -> str:
    """List available Kokoro voices."""
    try:
        data = httpx.get(f"{VOICE_URL}/voices", timeout=5).json()
        return ", ".join(data["voices"])
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        return f"Error: could not reach lyra-voice — {e}"


if __name__ == "__main__":
    mcp.run()
