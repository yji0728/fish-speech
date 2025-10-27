# Fish Speech MCP Server

The Fish Speech MCP (Model Context Protocol) Server provides LLM-friendly access to Fish Speech text-to-speech capabilities through a standardized protocol.

## Overview

The MCP server enables Large Language Models to:
1. **Upload reference audio files** for voice cloning
2. **Synthesize text to speech** with optimized parameters
3. **Get parameter recommendations** for optimal voice synthesis
4. **Manage reference voices** (list, add, delete)

## Installation

The MCP server is included in Fish Speech. Ensure you have the MCP dependency installed:

```bash
pip install mcp
```

Or install Fish Speech with all dependencies:

```bash
pip install -e .
```

## Usage

### Starting the MCP Server

```bash
python tools/mcp_server.py
```

Options:
- `--device`: Device to run models on (`cuda` or `cpu`, default: auto-detect)
- `--half` / `--no-half`: Enable/disable half precision (default: enabled)
- `--compile`: Compile models for faster inference (default: disabled)

Example:
```bash
# Run on CUDA with half precision
python tools/mcp_server.py --device cuda --half

# Run on CPU without compilation
python tools/mcp_server.py --device cpu --no-half
```

## Available Tools

### 1. upload_reference_audio

Upload a reference audio file for voice cloning.

**Parameters:**
- `reference_id` (string, required): Unique identifier for this reference voice
- `audio_base64` (string, required): Base64-encoded audio file (wav/mp3/etc.)
- `text` (string, required): Transcription of the audio content

**Returns:** Confirmation message with reference ID

**Example:**
```json
{
  "reference_id": "my_voice",
  "audio_base64": "UklGRi4...",
  "text": "This is a sample of my voice for cloning."
}
```

### 2. synthesize_speech

Synthesize text to speech using a reference voice.

**Parameters:**
- `text` (string, required): Text to synthesize into speech
- `reference_id` (string, optional): ID of previously uploaded reference voice
- `format` (string, optional): Output audio format (`wav`, `mp3`, or `pcm`, default: `wav`)
- `optimize` (boolean, optional): Whether to use optimized parameters (default: `true`)

**Returns:** Base64-encoded audio and synthesis information

**Example:**
```json
{
  "text": "Hello, this is a test of the text-to-speech system.",
  "reference_id": "my_voice",
  "format": "wav",
  "optimize": true
}
```

### 3. get_parameter_recommendations

Get optimized parameter recommendations for text-to-speech synthesis.

**Parameters:**
- `text` (string, required): The text that will be synthesized
- `use_case` (string, optional): Intended use case (`conversational`, `narrative`, `expressive`, or `stable`)

**Returns:** Detailed parameter recommendations with explanations

**Example:**
```json
{
  "text": "Welcome to our podcast. Today we'll discuss artificial intelligence.",
  "use_case": "narrative"
}
```

### 4. list_references

List all uploaded reference voices and their IDs.

**Parameters:** None

**Returns:** List of available reference voices

## Parameter Optimization

The MCP server provides intelligent parameter recommendations based on:

### Use Cases

1. **Conversational** (default)
   - Natural, dynamic speech
   - Temperature: 0.8, Top-p: 0.8, Repetition penalty: 1.1
   - Best for: Dialogues, casual speech

2. **Narrative**
   - Smooth, storytelling style
   - Temperature: 0.75, Top-p: 0.85, Repetition penalty: 1.05
   - Best for: Audiobooks, podcasts, narration

3. **Expressive**
   - More variation and emotion
   - Temperature: 0.9, Top-p: 0.75, Repetition penalty: 1.15
   - Best for: Character voices, dramatic readings

4. **Stable**
   - Consistent, predictable output
   - Temperature: 0.7, Top-p: 0.9, Repetition penalty: 1.0
   - Best for: Professional announcements, technical content

### Parameters Explained

- **temperature**: Controls randomness (0.1-1.0)
  - Higher = more varied/expressive
  - Lower = more consistent/predictable

- **top_p**: Controls diversity of word choices (0.1-1.0)
  - Higher = more diverse vocabulary
  - Lower = more focused/natural

- **repetition_penalty**: Prevents repetitive phrases (0.9-2.0)
  - Higher = stronger prevention
  - Lower = more natural flow

- **max_new_tokens**: Maximum length of generated speech
  - Automatically adjusted based on input text length

## Integration with LLMs

The MCP server follows the Model Context Protocol standard, making it compatible with:
- Claude Desktop
- Other MCP-compatible LLM clients

### Configuration Example (Claude Desktop)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fish-speech": {
      "command": "python",
      "args": ["/path/to/fish-speech/tools/mcp_server.py", "--device", "cuda"],
      "env": {
        "PYTHONPATH": "/path/to/fish-speech"
      }
    }
  }
}
```

## Workflow Example

Here's a typical workflow using the MCP server:

1. **Upload a reference voice:**
   ```
   LLM calls: upload_reference_audio
   - reference_id: "podcast_host"
   - audio_base64: [base64 encoded 15-second sample]
   - text: "Welcome to our weekly tech podcast..."
   ```

2. **Get parameter recommendations:**
   ```
   LLM calls: get_parameter_recommendations
   - text: "In today's episode, we explore the future of AI..."
   - use_case: "narrative"
   ```

3. **Synthesize speech:**
   ```
   LLM calls: synthesize_speech
   - text: "In today's episode, we explore the future of AI..."
   - reference_id: "podcast_host"
   - format: "mp3"
   - optimize: true
   ```

4. **List available voices:**
   ```
   LLM calls: list_references
   Returns: List of all uploaded reference voices
   ```

## Best Practices

### Reference Audio
- **Duration**: 10-30 seconds optimal
- **Quality**: Clear speech, minimal background noise
- **Content**: Natural speech in target voice/style
- **Format**: WAV recommended, but MP3/other formats supported

### Text Input
- **Length**: Keep under 500 characters per request for best results
- **Formatting**: Include punctuation for natural prosody
- **Special markers**: Use emotion markers like `(excited)`, `(sad)` for expressive synthesis

### Performance
- **CUDA recommended**: 10-20x faster than CPU
- **Half precision**: Reduces memory usage with minimal quality impact
- **Compilation**: Enable for repeated synthesis (slight startup cost)

## Troubleshooting

### Common Issues

1. **Model loading errors**
   - Ensure models are downloaded: `python tools/download_models.py`
   - Check disk space for model cache

2. **CUDA out of memory**
   - Reduce batch size or use `--no-half` flag
   - Use CPU mode: `--device cpu`

3. **Audio quality issues**
   - Ensure reference audio is high quality
   - Try different use_case parameters
   - Adjust temperature and top_p values

### Logs

The server uses `loguru` for logging. Check console output for detailed error messages.

## API Compatibility

The MCP server complements the existing Fish Speech REST API:
- **MCP Server**: LLM-friendly tool interface
- **REST API**: Traditional HTTP endpoints (see `tools/api_server.py`)

Both can run simultaneously on different ports.

## Development

To extend the MCP server:

1. Add new tools in `tools/mcp_server.py`
2. Register tools in `_register_tools()` method
3. Implement handler in `call_tool()` method
4. Update documentation

## License

Same as Fish Speech project: Apache License 2.0 for code, CC-BY-NC-SA-4.0 for models.

## Support

- GitHub Issues: https://github.com/fishaudio/fish-speech/issues
- Discord: https://discord.gg/Es5qTB9BcN
- Documentation: https://speech.fish.audio
