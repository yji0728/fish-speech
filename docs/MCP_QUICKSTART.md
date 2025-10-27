# Quick Start: Fish Speech MCP Server

This guide will help you quickly set up and use the Fish Speech MCP Server.

## What is MCP?

MCP (Model Context Protocol) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). The Fish Speech MCP Server allows LLMs like Claude to directly use Fish Speech's text-to-speech and voice cloning capabilities.

## Quick Setup

### 1. Install Dependencies

```bash
# Install Fish Speech with MCP support
pip install -e .
```

### 2. Download Models

```bash
# Download required models
python tools/download_models.py
```

### 3. Start the MCP Server

```bash
# For CUDA (GPU)
python tools/mcp_server.py --device cuda --half

# For CPU
python tools/mcp_server.py --device cpu --no-half
```

## Integration with Claude Desktop

### Configuration

1. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add Fish Speech MCP Server:

```json
{
  "mcpServers": {
    "fish-speech": {
      "command": "python",
      "args": [
        "/absolute/path/to/fish-speech/tools/mcp_server.py",
        "--device",
        "cuda",
        "--half"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/fish-speech"
      }
    }
  }
}
```

3. Restart Claude Desktop

### Using with Claude

Once configured, you can ask Claude to:

**Example 1: Upload a reference voice**
```
"Please upload this audio file as a reference voice called 'my_voice'. 
The audio says: 'Hello, this is my voice for testing.'"
```

**Example 2: Get parameter recommendations**
```
"What parameters should I use for synthesizing a podcast narration 
with this text: 'Welcome to our weekly tech podcast...'"
```

**Example 3: Synthesize speech**
```
"Please synthesize this text using my_voice: 
'Hello everyone, welcome to today's episode.'"
```

**Example 4: List available voices**
```
"Show me all the reference voices I have uploaded."
```

## How It Works

### MCP Tools

The server provides 4 tools that Claude can use:

1. **upload_reference_audio**
   - Upload 10-30 second audio samples
   - Create voice clones for TTS
   - Requires: reference_id, audio (base64), transcription

2. **synthesize_speech**
   - Convert text to speech
   - Use uploaded reference voices
   - Automatic parameter optimization

3. **get_parameter_recommendations**
   - Get optimal TTS parameters
   - Based on text content and use case
   - 4 use cases: conversational, narrative, expressive, stable

4. **list_references**
   - View all uploaded voices
   - Check which voices are available

### Parameter Optimization

The server automatically optimizes parameters based on:

- **Text length**: Adjusts max_new_tokens
- **Use case**: Sets temperature, top_p, repetition_penalty
  - Conversational: Natural, dynamic (temp=0.8, top_p=0.8)
  - Narrative: Smooth, storytelling (temp=0.75, top_p=0.85)
  - Expressive: Emotional, varied (temp=0.9, top_p=0.75)
  - Stable: Consistent, predictable (temp=0.7, top_p=0.9)

## Demo Script

Run the demonstration to see example interactions:

```bash
python examples/mcp_server_demo.py
```

This shows:
- How Claude would call the MCP tools
- Expected input/output formats
- Configuration examples

## Troubleshooting

### "Model not found" error
```bash
# Download models first
python tools/download_models.py
```

### "CUDA out of memory"
```bash
# Use CPU mode or disable half precision
python tools/mcp_server.py --device cpu --no-half
```

### Claude Desktop doesn't show tools
1. Check the config file path is correct
2. Ensure absolute paths are used (not relative)
3. Restart Claude Desktop
4. Check logs for errors

## Advanced Usage

### Custom Parameters

You can override automatic optimization:

```python
# Claude will call synthesize_speech with:
{
  "text": "Your text here",
  "reference_id": "my_voice",
  "optimize": false  # Disable auto-optimization
}
```

### Multiple Reference Voices

Upload different voices for different purposes:
- `narrator` - For story narration
- `character1` - For character dialogue
- `announcer` - For announcements

Switch between them by specifying different `reference_id` values.

## Best Practices

### Reference Audio Quality
- ✅ Clear speech, minimal background noise
- ✅ 10-30 seconds duration
- ✅ Natural speaking style
- ✅ Good audio quality (not compressed)
- ❌ Music or multiple speakers
- ❌ Very short clips (<5 seconds)
- ❌ Heavy accents (unless desired)

### Text Input
- ✅ Include proper punctuation
- ✅ Break long texts into chunks
- ✅ Use emotion markers: `(excited)`, `(sad)`, etc.
- ❌ Don't exceed 500 characters per request
- ❌ Avoid special characters that affect speech

## Documentation

For detailed information:
- [Full MCP Server Documentation (English)](../docs/MCP_SERVER.md)
- [MCP Server Documentation (Korean)](../docs/MCP_SERVER.ko.md)
- [Fish Speech Main Documentation](https://speech.fish.audio)

## Support

- **GitHub Issues**: https://github.com/fishaudio/fish-speech/issues
- **Discord**: https://discord.gg/Es5qTB9BcN
- **Documentation**: https://speech.fish.audio

## What's Next?

After setup, try:
1. Upload your first reference voice
2. Ask Claude for parameter recommendations
3. Synthesize your first speech
4. Experiment with different voices and use cases

Happy voice cloning! 🎤
