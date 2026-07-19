"""Terminal sandbox behaviour for hosted labs."""

from __future__ import annotations

from hosted_labs.core.terminal import build_kubectl_argv, execute_terminal_line


def test_build_kubectl_argv_records_blocked_namespace_flag() -> None:
    argv, violations = build_kubectl_argv("kubectl get pods -n kube-system", "player-ns")
    assert "--namespace" in argv
    assert argv[argv.index("--namespace") + 1] == "player-ns"
    assert any(violation["type"] == "blocked_flag" for violation in violations)


def test_execute_terminal_line_blocks_shell_operator() -> None:
    result = execute_terminal_line("kubectl get pods; id", "player-ns", "player-ns")
    assert result.blocked is True
    assert result.policy_violations[0]["type"] == "shell_operator"
