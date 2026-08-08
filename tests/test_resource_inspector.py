"""Resource inspector kubectl argument construction and result handling."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from services import resource_inspector


def _kubectl_result(returncode=0, stdout="", stderr=""):
    return returncode, stdout, stderr, False


@pytest.mark.parametrize(
    "getter, args, expected_kind",
    [
        (resource_inspector.get_config_map, ("bathhouse-rules", "yumoto-springs"), "configmap"),
        (resource_inspector.get_secret, ("spring-seal", "yumoto-springs"), "secret"),
        (
            resource_inspector.get_persistent_volume_claim,
            ("spring-deed", "yumoto-springs"),
            "persistentvolumeclaim",
        ),
    ],
)
def test_namespaced_getters_query_the_right_kind(getter, args, expected_kind) -> None:
    with patch.object(
        resource_inspector, "_run_kubectl", return_value=_kubectl_result(stdout="{}")
    ) as run_kubectl:
        ok, payload = getter(*args)

    assert ok is True
    assert payload == {}
    kubectl_args = run_kubectl.call_args.args[0]
    assert kubectl_args[:3] == ["get", expected_kind, args[0]]
    assert kubectl_args[3:5] == ["-n", args[1]]


@pytest.mark.parametrize(
    "getter, name, expected_kind",
    [
        (resource_inspector.get_persistent_volume, "pvc-abc", "persistentvolume"),
        (resource_inspector.get_storage_class, "standard", "storageclass"),
    ],
)
def test_cluster_scoped_getters_omit_namespace(getter, name, expected_kind) -> None:
    with patch.object(
        resource_inspector, "_run_kubectl", return_value=_kubectl_result(stdout="{}")
    ) as run_kubectl:
        ok, _ = getter(name)

    assert ok is True
    kubectl_args = run_kubectl.call_args.args[0]
    assert kubectl_args == ["get", expected_kind, name, "-o", "json"]
    assert "-n" not in kubectl_args


def test_missing_resource_returns_player_readable_message() -> None:
    with patch.object(
        resource_inspector,
        "_run_kubectl",
        return_value=_kubectl_result(returncode=1, stderr='Error: configmaps "x" not found'),
    ):
        ok, message = resource_inspector.get_config_map("x", "yumoto-springs")

    assert ok is False
    assert "not found" in message
    assert "yumoto-springs" in message


def test_storage_class_payload_is_parsed_json() -> None:
    body = {"metadata": {"name": "standard"}, "provisioner": "k8s.io/minikube-hostpath"}
    with patch.object(
        resource_inspector, "_run_kubectl", return_value=_kubectl_result(stdout=json.dumps(body))
    ):
        ok, payload = resource_inspector.get_storage_class("standard")

    assert ok is True
    assert payload["provisioner"] == "k8s.io/minikube-hostpath"


def test_exec_in_pod_without_container_has_no_container_flag() -> None:
    with patch.object(
        resource_inspector, "_run_kubectl", return_value=_kubectl_result(stdout="42\n")
    ) as run_kubectl:
        ok, stdout = resource_inspector.exec_in_pod(
            "front-desk", "yumoto-springs", ["printenv", "WATER_TEMP"]
        )

    assert (ok, stdout) == (True, "42\n")
    kubectl_args = run_kubectl.call_args.args[0]
    assert "-c" not in kubectl_args
    assert kubectl_args == [
        "exec",
        "front-desk",
        "-n",
        "yumoto-springs",
        "--",
        "printenv",
        "WATER_TEMP",
    ]


def test_exec_in_pod_targets_the_named_container() -> None:
    with patch.object(
        resource_inspector, "_run_kubectl", return_value=_kubectl_result(stdout="ok")
    ) as run_kubectl:
        resource_inspector.exec_in_pod(
            "shared-basin",
            "yumoto-springs",
            ["cat", "/basin/note"],
            container="front-desk",
        )

    kubectl_args = run_kubectl.call_args.args[0]
    assert kubectl_args == [
        "exec",
        "shared-basin",
        "-n",
        "yumoto-springs",
        "-c",
        "front-desk",
        "--",
        "cat",
        "/basin/note",
    ]


def test_exec_command_flags_are_not_swallowed_by_kubectl() -> None:
    """Args after ``--`` belong to the container command, not kubectl."""
    with patch.object(
        resource_inspector, "_run_kubectl", return_value=_kubectl_result(stdout="")
    ) as run_kubectl:
        resource_inspector.exec_in_pod(
            "ledger", "yumoto-springs", ["ls", "-la", "/var/olive"], container="ledger"
        )

    kubectl_args = run_kubectl.call_args.args[0]
    separator = kubectl_args.index("--")
    assert kubectl_args[separator + 1 :] == ["ls", "-la", "/var/olive"]


def test_exec_failure_surfaces_stderr() -> None:
    with patch.object(
        resource_inspector,
        "_run_kubectl",
        return_value=_kubectl_result(returncode=1, stderr="cat: /etc/yumoto/schedule.yaml: not found"),
    ):
        ok, message = resource_inspector.exec_in_pod(
            "front-desk", "yumoto-springs", ["cat", "/etc/yumoto/schedule.yaml"]
        )

    assert ok is False
    assert "schedule.yaml" in message


def test_exec_timeout_is_reported_as_failure() -> None:
    with patch.object(resource_inspector, "_run_kubectl", return_value=(None, "", "", True)):
        ok, message = resource_inspector.exec_in_pod("ledger", "yumoto-springs", ["sleep", "60"])

    assert ok is False
    assert "Timed out" in message
