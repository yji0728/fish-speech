#!/usr/bin/env python3
"""
Example script demonstrating how to use Fish Speech MCP Server
This script shows how an LLM client would interact with the MCP server.

Note: This is a demonstration of the MCP protocol interactions.
In production, MCP clients like Claude Desktop would handle this automatically.
"""

import asyncio
import base64
import json
from pathlib import Path


async def demonstrate_mcp_workflow():
    """
    Demonstrate a typical workflow with the Fish Speech MCP Server.
    
    This shows the sequence of operations an LLM would perform:
    1. Get parameter recommendations
    2. Upload a reference audio
    3. Synthesize speech
    4. List available references
    """
    
    print("=" * 80)
    print("Fish Speech MCP Server - Example Workflow")
    print("=" * 80)
    print()
    
    # Example 1: Get parameter recommendations
    print("1. Getting parameter recommendations for text synthesis...")
    print("-" * 80)
    
    text_to_synthesize = "Welcome to our podcast about artificial intelligence."
    print(f"Text: {text_to_synthesize}")
    print(f"Use case: narrative")
    print()
    
    # This would be sent as an MCP tool call:
    tool_call = {
        "tool": "get_parameter_recommendations",
        "arguments": {
            "text": text_to_synthesize,
            "use_case": "narrative"
        }
    }
    print("MCP Tool Call:")
    print(json.dumps(tool_call, indent=2))
    print()
    
    # Expected response (example)
    expected_response = """
Parameter Recommendations for 'narrative' use case:

1. **temperature** = 0.75
   - Controls randomness in speech generation
   - Lower values = more consistent, predictable speech

2. **top_p** = 0.85
   - Controls diversity of word choices
   - Higher values = more diverse vocabulary

3. **repetition_penalty** = 1.05
   - Prevents repetitive phrases
   - Lower values = more natural flow

4. **max_new_tokens** = 512
   - Maximum length of generated speech
   - Automatically adjusted based on input text length

Text length: 55 characters
Recommended max_new_tokens: 512

Use these parameters in synthesize_speech tool for optimal results!
    """
    print("Expected MCP Response:")
    print(expected_response)
    print()
    
    # Example 2: Upload reference audio
    print("2. Uploading reference audio for voice cloning...")
    print("-" * 80)
    
    # In a real scenario, you would encode actual audio data
    example_audio_path = "example_voice.wav"  # Hypothetical file
    print(f"Reference ID: podcast_host")
    print(f"Audio file: {example_audio_path}")
    print(f"Transcription: Hello, this is my voice for the podcast...")
    print()
    
    tool_call = {
        "tool": "upload_reference_audio",
        "arguments": {
            "reference_id": "podcast_host",
            "audio_base64": "UklGRiQAAABXQVZFZm10...",  # Example base64 (truncated)
            "text": "Hello, this is my voice for the podcast..."
        }
    }
    print("MCP Tool Call:")
    print(json.dumps(tool_call, indent=2))
    print()
    
    expected_response = """
Successfully uploaded reference audio with ID: podcast_host
Audio saved to: references/podcast_host/audio.wav
Text: Hello, this is my voice for the podcast...
    """
    print("Expected MCP Response:")
    print(expected_response)
    print()
    
    # Example 3: Synthesize speech
    print("3. Synthesizing speech with the reference voice...")
    print("-" * 80)
    
    tool_call = {
        "tool": "synthesize_speech",
        "arguments": {
            "text": text_to_synthesize,
            "reference_id": "podcast_host",
            "format": "wav",
            "optimize": True
        }
    }
    print("MCP Tool Call:")
    print(json.dumps(tool_call, indent=2))
    print()
    
    expected_response = """
Successfully synthesized speech!
Format: wav
Sample rate: 44100 Hz
Audio size: 264600 bytes
Parameters used: {'temperature': 0.75, 'top_p': 0.85, 'repetition_penalty': 1.05, 'max_new_tokens': 512}

Base64-encoded audio:
UklGRkBAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQRAAAAAAAAA...
    """
    print("Expected MCP Response:")
    print(expected_response)
    print()
    
    # Example 4: List references
    print("4. Listing all available reference voices...")
    print("-" * 80)
    
    tool_call = {
        "tool": "list_references",
        "arguments": {}
    }
    print("MCP Tool Call:")
    print(json.dumps(tool_call, indent=2))
    print()
    
    expected_response = """
Available reference voices (1):
- podcast_host: Hello, this is my voice for the podcast... [audio: ✓]
    """
    print("Expected MCP Response:")
    print(expected_response)
    print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print()
    print("The Fish Speech MCP Server provides 4 main tools:")
    print("1. upload_reference_audio - Upload voice samples for cloning")
    print("2. get_parameter_recommendations - Get optimized synthesis parameters")
    print("3. synthesize_speech - Convert text to speech with cloned voice")
    print("4. list_references - View all uploaded reference voices")
    print()
    print("These tools enable LLMs to:")
    print("- Understand optimal TTS parameters for different contexts")
    print("- Manage voice cloning references")
    print("- Generate high-quality speech synthesis")
    print()
    print("For actual usage, configure your MCP client (e.g., Claude Desktop)")
    print("to connect to the Fish Speech MCP Server.")
    print()


def print_configuration_example():
    """Print example configuration for MCP clients."""
    print("=" * 80)
    print("Configuration Example for Claude Desktop")
    print("=" * 80)
    print()
    
    config = {
        "mcpServers": {
            "fish-speech": {
                "command": "python",
                "args": [
                    "/path/to/fish-speech/tools/mcp_server.py",
                    "--device",
                    "cuda",
                    "--half"
                ],
                "env": {
                    "PYTHONPATH": "/path/to/fish-speech"
                }
            }
        }
    }
    
    print("Add this to your claude_desktop_config.json:")
    print()
    print(json.dumps(config, indent=2))
    print()
    print("Location:")
    print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print()


if __name__ == "__main__":
    print()
    print("This is a demonstration script showing how LLMs interact with")
    print("the Fish Speech MCP Server using the Model Context Protocol.")
    print()
    input("Press Enter to continue...")
    print()
    
    asyncio.run(demonstrate_mcp_workflow())
    
    print()
    input("Press Enter to see configuration example...")
    print()
    
    print_configuration_example()
    
    print()
    print("For more information, see docs/MCP_SERVER.md")
    print()
