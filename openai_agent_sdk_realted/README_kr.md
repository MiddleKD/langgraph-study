
# OpenAI Agent SDK 이슈 분석

## 중요 설정 참고

```python
from agents import set_default_openai_api
set_default_openapi_api("chat_completions")  # 반드시 설정 필요
```

- `respond` 엔드포인트에서는 기본적으로 동작하지 않음
- `chat_completions` 엔드포인트를 명시적으로 설정해야 정상 동작

## 발견된 주요 이슈

### 1. aiohttp 세션 관리 문제
- **문제점**: Litellm 사용 시 aiohttp 세션이 제대로 정리되지 않는 문제 발생
- **증상**: `Unclosed client session` 및 `Unclosed connector` 경고 메시지 출력
- **임시 해결책**: 
  ```python
  import os
  os.environ["DISABLE_AIOHTTP_TRANSPORT"] = "True"
  ```
- **영향**: 세션 관리 문제로 인해 장기 실행 시 리소스 누수 가능성

### 2. Tool Call ID 길이 제한 문제
- **문제점**: Tool Call ID가 40자 제한을 초과하여 API 오류 발생
- **오류 메시지**:
  ```
  openai.BadRequestError: Error code: 400 - {
    'error': {
      'message': "Invalid 'messages[2].tool_calls[0].id': string too long. 
      Expected a string with maximum length 40, but got a string with length 41",
      'type': 'invalid_request_error',
      'param': 'messages[2].tool_calls[0].id',
      'code': 'string_above_max_length'
    }
  }
  ```
- **원인**: `'call_' + uuid.uuid4()` 형식(41자)이 OpenAI API의 40자 제한 초과
- **영향**: Tool 기능 사용 불가, 백엔드 간 호환성 문제 발생

## OpenAI Agent SDK 채택 시 우려사항

1. **호환성 문제**
   - Litellm 프록시를 통한 백엔드 연동 시 ID 생성 방식으로 인한 호환성 문제 발생
   - 다른 모델(Gemini, Azure 등)과의 연동 시 추가적인 문제 발생 가능성

2. **불안정한 세션 관리**
   - aiohttp 세션 관리 문제로 인한 리소스 누수 가능성
   - 장기 실행 시 안정성 저하 우려

3. **제한된 유연성**
   - ID 생성 방식이 하드코딩되어 있어 유연한 커스터마이징 어려움
   - 다양한 환경에서의 테스트 부족으로 인한 예상치 못한 문제 발생 가능성

## 결론

현재 OpenAI Agent SDK는 위와 같은 근본적인 문제들로 인해 프로덕션 환경에서의 사용이 제한적일 수 있습니다. 특히:
- 다양한 백엔드 서비스와의 호환성 문제
- 리소스 관리 관련 이슈
- 제한된 유연성

으로 인해 신중한 검토가 필요합니다. 이러한 문제들이 해결되기 전까지는 제한된 환경에서의 테스트를 통한 검증이 권장됩니다.

## 관련 이슈
- [aiohttp Warning Issue #11657](https://github.com/BerriAI/litellm/issues/11657)
- [Tool Call ID Length Issue #11392](https://github.com/BerriAI/litellm/issues/11392)