import os
import pytest
import respx


@pytest.fixture
def no_http_mocks():
    """Disable respx mocking within a test to allow real HTTP calls."""
    try:
        router = respx.get_router()
        if router and router.is_started:
            router.stop()
    except Exception:
        pass
    yield


@pytest.fixture
def require_live_llm():
    """Skip the test unless live LLM env is configured."""
    if not (os.getenv("RUN_LIVE_LLM") == "1" and os.getenv("OPENROUTER_API_KEY")):
        pytest.skip("live LLM test requires RUN_LIVE_LLM=1 and OPENROUTER_API_KEY")
    return True


