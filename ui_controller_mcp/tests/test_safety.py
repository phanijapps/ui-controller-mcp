from ui_controller_mcp.utils.safety import SafetyGuard


def test_rejects_dangerous_launch_target():
    guard = SafetyGuard()
    result = guard.validate_launch_target("rm -rf /")
    assert not result.allowed
    assert "disallowed" in (result.reason or "")


def test_allows_safe_launch_target():
    guard = SafetyGuard()
    result = guard.validate_launch_target("code")
    assert result.allowed


def test_rejects_dangerous_text():
    guard = SafetyGuard()
    result = guard.validate_text("shutdown now")
    assert not result.allowed


def test_allowed_text_passes():
    guard = SafetyGuard()
    result = guard.validate_text("hello world")
    assert result.allowed
