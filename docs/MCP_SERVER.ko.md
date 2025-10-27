# Fish Speech MCP 서버

Fish Speech의 MCP (Model Context Protocol) 서버 구현입니다.

## 개요

이 MCP 서버는 LLM이 Fish Speech의 텍스트-음성 변환 기능을 사용할 수 있도록 합니다:

1. **참조 오디오 업로드**: 음성 복제를 위한 오디오 파일 업로드
2. **음성 합성**: 최적화된 파라미터로 텍스트를 음성으로 변환
3. **파라미터 추천**: 최적의 음성 합성을 위한 파라미터 제안
4. **참조 목록**: 업로드된 모든 참조 음성 조회

## 사용 방법

### MCP 서버 시작

```bash
python tools/mcp_server.py --device cuda --half
```

### Claude Desktop 설정

`claude_desktop_config.json` 파일에 다음을 추가하세요:

```json
{
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
```

## 주요 기능

### 1. 파라미터 최적화

사용 사례에 따른 자동 파라미터 추천:

- **대화형(conversational)**: 자연스럽고 역동적인 음성
- **서사형(narrative)**: 부드러운 스토리텔링 스타일
- **표현형(expressive)**: 다양하고 감정적인 음성
- **안정형(stable)**: 일관되고 예측 가능한 음성

### 2. 음성 복제

10-30초 길이의 오디오 샘플로 음성 복제:

```python
# LLM이 자동으로 호출하는 MCP 도구
upload_reference_audio(
    reference_id="내음성",
    audio_base64="UklGRi4...",
    text="음성 샘플의 텍스트"
)
```

### 3. 텍스트-음성 변환

참조 음성을 사용한 텍스트 음성 변환:

```python
# LLM이 자동으로 호출하는 MCP 도구
synthesize_speech(
    text="안녕하세요. 테스트입니다.",
    reference_id="내음성",
    format="wav",
    optimize=True
)
```

## 파라미터 설명

- **temperature** (0.1-1.0): 음성 생성의 무작위성 제어
  - 높을수록 더 다양하고 표현적인 음성
  - 낮을수록 더 일관되고 예측 가능한 음성

- **top_p** (0.1-1.0): 단어 선택의 다양성 제어
  - 높을수록 더 다양한 어휘 사용
  - 낮을수록 더 집중되고 자연스러운 음성

- **repetition_penalty** (0.9-2.0): 반복 문구 방지
  - 높을수록 강한 방지
  - 낮을수록 더 자연스러운 흐름

- **max_new_tokens**: 생성되는 음성의 최대 길이
  - 입력 텍스트 길이에 따라 자동 조정

## 예제

데모 스크립트 실행:

```bash
python examples/mcp_server_demo.py
```

## 문서

자세한 내용은 다음 문서를 참조하세요:
- [영문 문서](../MCP_SERVER.md)
- [메인 README](../../README.md)

## 지원

- GitHub Issues: https://github.com/fishaudio/fish-speech/issues
- Discord: https://discord.gg/Es5qTB9BcN

## 라이선스

Fish Speech 프로젝트와 동일:
- 코드: Apache License 2.0
- 모델: CC-BY-NC-SA-4.0
