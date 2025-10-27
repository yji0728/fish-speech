#!/usr/bin/env python3
"""
Fish Speech MCP Server

This MCP server provides LLM-friendly access to Fish Speech text-to-speech capabilities.
It allows LLMs to:
1. Upload reference audio files for voice cloning
2. Synthesize text to speech with optimized parameters
3. Get parameter recommendations for optimal voice synthesis
"""

import argparse
import base64
import io
import os
import sys
from pathlib import Path
from typing import Any, TYPE_CHECKING

from loguru import logger
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)

# Lazy imports to avoid heavy dependencies at startup
if TYPE_CHECKING:
    import pyrootutils
    import soundfile as sf
    import torch
    from fish_speech.utils.schema import ServeTTSRequest, ServeReferenceAudio
    from tools.server.inference import inference_wrapper as inference
    from tools.server.model_manager import ModelManager


class FishSpeechMCPServer:
    """MCP Server for Fish Speech TTS functionality."""

    def __init__(self, device: str = "cuda", half: bool = True, compile: bool = False):
        """Initialize the Fish Speech MCP server.
        
        Args:
            device: Device to run models on (cuda/cpu)
            half: Whether to use half precision
            compile: Whether to compile models
        """
        self.device = device
        self.half = half
        self.compile = compile
        self.model_manager = None
        self.references_dir = Path("references")
        self.references_dir.mkdir(exist_ok=True)
        
        # Create MCP server
        self.server = Server("fish-speech-mcp")
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="upload_reference_audio",
                    description=(
                        "Upload a reference audio file for voice cloning. "
                        "The audio should be 10-30 seconds long and contain clear speech. "
                        "Returns a reference_id that can be used for TTS synthesis."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "reference_id": {
                                "type": "string",
                                "description": "Unique identifier for this reference voice",
                            },
                            "audio_base64": {
                                "type": "string",
                                "description": "Base64-encoded audio file (wav/mp3/etc.)",
                            },
                            "text": {
                                "type": "string",
                                "description": "Transcription of the audio content",
                            },
                        },
                        "required": ["reference_id", "audio_base64", "text"],
                    },
                ),
                Tool(
                    name="synthesize_speech",
                    description=(
                        "Synthesize text to speech using a reference voice. "
                        "Can use previously uploaded reference_id or provide inline reference audio. "
                        "Returns base64-encoded audio in the requested format."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to synthesize into speech",
                            },
                            "reference_id": {
                                "type": "string",
                                "description": "ID of previously uploaded reference voice",
                            },
                            "format": {
                                "type": "string",
                                "enum": ["wav", "mp3", "pcm"],
                                "description": "Output audio format (default: wav)",
                            },
                            "optimize": {
                                "type": "boolean",
                                "description": "Whether to use optimized parameters (default: true)",
                            },
                        },
                        "required": ["text"],
                    },
                ),
                Tool(
                    name="get_parameter_recommendations",
                    description=(
                        "Get optimized parameter recommendations for text-to-speech synthesis "
                        "based on the text content and desired output characteristics."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text that will be synthesized",
                            },
                            "use_case": {
                                "type": "string",
                                "enum": ["conversational", "narrative", "expressive", "stable"],
                                "description": "Intended use case for the speech",
                            },
                        },
                        "required": ["text"],
                    },
                ),
                Tool(
                    name="list_references",
                    description="List all uploaded reference voices and their IDs.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "upload_reference_audio":
                    return await self._upload_reference_audio(arguments)
                elif name == "synthesize_speech":
                    return await self._synthesize_speech(arguments)
                elif name == "get_parameter_recommendations":
                    return await self._get_parameter_recommendations(arguments)
                elif name == "list_references":
                    return await self._list_references(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _upload_reference_audio(self, args: dict[str, Any]) -> list[TextContent]:
        """Upload reference audio for voice cloning."""
        reference_id = args["reference_id"]
        audio_base64 = args["audio_base64"]
        text = args["text"]
        
        # Decode audio
        try:
            audio_data = base64.b64decode(audio_base64)
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error decoding audio: {str(e)}"
            )]
        
        # Create reference directory
        ref_dir = self.references_dir / reference_id
        if ref_dir.exists():
            return [TextContent(
                type="text",
                text=f"Error: Reference ID '{reference_id}' already exists. Use a different ID or delete the existing one first."
            )]
        
        ref_dir.mkdir(parents=True, exist_ok=True)
        
        # Save audio file
        audio_path = ref_dir / "audio.wav"
        try:
            with open(audio_path, "wb") as f:
                f.write(audio_data)
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error saving audio file: {str(e)}"
            )]
        
        # Save text
        text_path = ref_dir / "text.txt"
        try:
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error saving text file: {str(e)}"
            )]
        
        return [TextContent(
            type="text",
            text=f"Successfully uploaded reference audio with ID: {reference_id}\n"
                 f"Audio saved to: {audio_path}\n"
                 f"Text: {text[:100]}{'...' if len(text) > 100 else ''}"
        )]
    
    async def _synthesize_speech(self, args: dict[str, Any]) -> list[TextContent]:
        """Synthesize text to speech."""
        # Lazy import heavy dependencies
        import pyrootutils
        pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
        
        import soundfile as sf
        from fish_speech.utils.schema import ServeTTSRequest
        from tools.server.inference import inference_wrapper as inference
        from tools.server.model_manager import ModelManager
        
        text = args["text"]
        reference_id = args.get("reference_id")
        format_type = args.get("format", "wav")
        optimize = args.get("optimize", True)
        
        # Initialize model manager if not already done
        if self.model_manager is None:
            try:
                logger.info("Initializing model manager...")
                self.model_manager = ModelManager(
                    mode="tts",
                    device=self.device,
                    half=self.half,
                    compile=self.compile,
                )
                logger.info("Model manager initialized successfully")
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error initializing models: {str(e)}"
                )]
        
        # Get optimized parameters if requested
        if optimize:
            params = self._get_optimized_params(text, "conversational")
        else:
            params = {
                "temperature": 0.8,
                "top_p": 0.8,
                "repetition_penalty": 1.1,
                "max_new_tokens": 1024,
            }
        
        # Create TTS request
        try:
            tts_request = ServeTTSRequest(
                text=text,
                reference_id=reference_id,
                format=format_type,
                normalize=True,
                streaming=False,
                **params,
            )
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating TTS request: {str(e)}"
            )]
        
        # Perform inference
        try:
            logger.info(f"Synthesizing speech for text: {text[:100]}...")
            engine = self.model_manager.tts_inference_engine
            fake_audios = next(inference(tts_request, engine))
            
            # Save to buffer
            buffer = io.BytesIO()
            sample_rate = engine.decoder_model.sample_rate
            sf.write(buffer, fake_audios, sample_rate, format=format_type)
            
            # Encode to base64
            audio_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            return [TextContent(
                type="text",
                text=f"Successfully synthesized speech!\n"
                     f"Format: {format_type}\n"
                     f"Sample rate: {sample_rate} Hz\n"
                     f"Audio size: {len(buffer.getvalue())} bytes\n"
                     f"Parameters used: {params}\n\n"
                     f"Base64-encoded audio:\n{audio_base64}"
            )]
        except Exception as e:
            logger.error(f"Error during synthesis: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error during synthesis: {str(e)}"
            )]
    
    def _get_optimized_params(self, text: str, use_case: str) -> dict[str, Any]:
        """Get optimized parameters based on text and use case."""
        # Base parameters
        params = {
            "temperature": 0.8,
            "top_p": 0.8,
            "repetition_penalty": 1.1,
            "max_new_tokens": 1024,
        }
        
        # Adjust based on use case
        if use_case == "conversational":
            # Natural, dynamic speech
            params["temperature"] = 0.8
            params["top_p"] = 0.8
            params["repetition_penalty"] = 1.1
        elif use_case == "narrative":
            # Smooth, storytelling style
            params["temperature"] = 0.75
            params["top_p"] = 0.85
            params["repetition_penalty"] = 1.05
        elif use_case == "expressive":
            # More variation and emotion
            params["temperature"] = 0.9
            params["top_p"] = 0.75
            params["repetition_penalty"] = 1.15
        elif use_case == "stable":
            # Consistent, predictable output
            params["temperature"] = 0.7
            params["top_p"] = 0.9
            params["repetition_penalty"] = 1.0
        
        # Adjust max_new_tokens based on text length
        text_length = len(text)
        if text_length < 100:
            params["max_new_tokens"] = 512
        elif text_length < 300:
            params["max_new_tokens"] = 1024
        else:
            params["max_new_tokens"] = 2048
        
        return params
    
    async def _get_parameter_recommendations(self, args: dict[str, Any]) -> list[TextContent]:
        """Get parameter recommendations for TTS synthesis."""
        text = args["text"]
        use_case = args.get("use_case", "conversational")
        
        params = self._get_optimized_params(text, use_case)
        
        explanation = f"""
Parameter Recommendations for '{use_case}' use case:

1. **temperature** = {params['temperature']}
   - Controls randomness in speech generation
   - Higher values (0.8-1.0) = more varied, expressive speech
   - Lower values (0.6-0.7) = more consistent, predictable speech

2. **top_p** = {params['top_p']}
   - Controls diversity of word choices
   - Higher values (0.9-1.0) = more diverse vocabulary
   - Lower values (0.7-0.8) = more focused, natural speech

3. **repetition_penalty** = {params['repetition_penalty']}
   - Prevents repetitive phrases
   - Higher values (1.1-1.2) = strong prevention
   - Lower values (1.0-1.05) = more natural flow

4. **max_new_tokens** = {params['max_new_tokens']}
   - Maximum length of generated speech
   - Automatically adjusted based on input text length

Text length: {len(text)} characters
Recommended max_new_tokens: {params['max_new_tokens']}

Use these parameters in synthesize_speech tool for optimal results!
"""
        
        return [TextContent(
            type="text",
            text=explanation
        )]
    
    async def _list_references(self, args: dict[str, Any]) -> list[TextContent]:
        """List all uploaded reference voices."""
        if not self.references_dir.exists():
            return [TextContent(
                type="text",
                text="No reference voices uploaded yet."
            )]
        
        references = []
        for ref_dir in self.references_dir.iterdir():
            if ref_dir.is_dir():
                text_file = ref_dir / "text.txt"
                audio_file = ref_dir / "audio.wav"
                
                if text_file.exists():
                    with open(text_file, "r", encoding="utf-8") as f:
                        text = f.read()
                else:
                    text = "(no text)"
                
                audio_exists = audio_file.exists()
                references.append(f"- {ref_dir.name}: {text[:50]}{'...' if len(text) > 50 else ''} [audio: {'✓' if audio_exists else '✗'}]")
        
        if not references:
            return [TextContent(
                type="text",
                text="No reference voices uploaded yet."
            )]
        
        return [TextContent(
            type="text",
            text=f"Available reference voices ({len(references)}):\n" + "\n".join(references)
        )]
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Fish Speech MCP Server...")
        logger.info(f"Device: {self.device}")
        logger.info(f"Half precision: {self.half}")
        logger.info(f"Compile: {self.compile}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def parse_args():
    """Parse command line arguments."""
    import torch
    
    parser = argparse.ArgumentParser(
        description="Fish Speech MCP Server - LLM-friendly TTS interface"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to run models on (cuda/cpu)",
    )
    parser.add_argument(
        "--half",
        action="store_true",
        default=True,
        help="Use half precision for models",
    )
    parser.add_argument(
        "--no-half",
        action="store_false",
        dest="half",
        help="Disable half precision",
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        default=False,
        help="Compile models for faster inference",
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    
    server = FishSpeechMCPServer(
        device=args.device,
        half=args.half,
        compile=args.compile,
    )
    
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
