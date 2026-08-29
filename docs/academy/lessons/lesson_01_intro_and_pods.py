"""Lesson 01 - Introduction to Kubernetes and Pods.

Pure content: the narration for each beat and the boxes that pop in with it.
All machinery lives in `engine.py`.
"""

from engine import (
    COLOR_ACCENT,
    COLOR_CONTAINER,
    COLOR_NAMESPACE,
    COLOR_NODE,
    COLOR_POD,
    Beat,
    Box,
    Lesson,
)

BEAT_NODE = 0
BEAT_NAMESPACE = 1
BEAT_POD = 2
BEAT_CONTAINER = 3
BEAT_SIDECAR = 4
BEAT_RECAP = 5

NAMESPACE_NAMES = ("kube-system", "default", "payments")
NAMESPACE_LEFTS = (20, 96, 172)
NAMESPACE_TOP = 48
NAMESPACE_WIDTH = 64
NAMESPACE_HEIGHT = 116

POD_NAMES = (("coredns",), ("web", "job"), ("api",))
POD_TOPS = (64, 116)
POD_WIDTH = 48
POD_HEIGHT = 42

CONTAINER_SIZE = 14
SIDECAR_POD = ("payments", "api")

BEATS = (
    Beat(
        (
            "A NODE IS ONE MACHINE IN YOUR CLUSTER.",
            "IT LENDS ITS CPU, MEMORY AND DISK TO KUBERNETES,",
            "AND EVERYTHING YOU DEPLOY HAS TO LAND ON ONE.",
        )
    ),
    Beat(
        (
            "A NAMESPACE IS A VIRTUAL CLUSTER INSIDE THE CLUSTER.",
            "IT SCOPES NAMES, QUOTAS AND ACCESS, SO TWO TEAMS CAN",
            "BOTH RUN A POD CALLED WEB WITHOUT COLLIDING.",
        )
    ),
    Beat(
        (
            "A POD IS THE SMALLEST THING KUBERNETES DEPLOYS.",
            "IT IS SCHEDULED ONTO ONE NODE, LIVES IN A NAMESPACE,",
            "AND GETS ITS OWN IP AND ITS OWN LIFECYCLE.",
        )
    ),
    Beat(
        (
            "A CONTAINER RUNS INSIDE THE POD.",
            "IT IS THE IMAGE, THE PORT AND THE PROCESS:",
            "THE PART THAT ACTUALLY SERVES YOUR TRAFFIC.",
        )
    ),
    Beat(
        (
            "A POD CAN HOLD MORE THAN ONE CONTAINER.",
            "SIDECARS - PROXIES, LOG SHIPPERS - SHARE THE POD'S",
            "NETWORK AND VOLUMES, AND LIVE AND DIE WITH IT.",
        )
    ),
    Beat(
        (
            "NODE > NAMESPACE > POD > CONTAINER.",
            "THAT HIERARCHY IS WHAT KUBECTL GET SHOWS YOU,",
            "AND EVERY LATER LESSON BUILDS ON IT.",
        )
    ),
)


def _boxes():
    boxes = [Box(BEAT_NODE, 12, 30, 232, 142, COLOR_NODE, "NODE  node-1")]
    for namespace_index, namespace in enumerate(NAMESPACE_NAMES):
        namespace_left = NAMESPACE_LEFTS[namespace_index]
        boxes.append(
            Box(
                BEAT_NAMESPACE,
                namespace_left,
                NAMESPACE_TOP,
                NAMESPACE_WIDTH,
                NAMESPACE_HEIGHT,
                COLOR_NAMESPACE,
                f"NS {namespace}",
            )
        )
        for pod_index, pod in enumerate(POD_NAMES[namespace_index]):
            pod_left = namespace_left + 8
            pod_top = POD_TOPS[pod_index]
            boxes.append(
                Box(BEAT_POD, pod_left, pod_top, POD_WIDTH, POD_HEIGHT, COLOR_POD, f"POD {pod}")
            )
            boxes.append(
                Box(
                    BEAT_CONTAINER,
                    pod_left + 6,
                    pod_top + 16,
                    CONTAINER_SIZE,
                    CONTAINER_SIZE,
                    COLOR_CONTAINER,
                )
            )
            if (namespace, pod) == SIDECAR_POD:
                boxes.append(
                    Box(
                        BEAT_SIDECAR,
                        pod_left + 26,
                        pod_top + 16,
                        CONTAINER_SIZE,
                        CONTAINER_SIZE,
                        COLOR_ACCENT,
                        note="SIDECAR",
                    )
                )
    return tuple(boxes)


LESSON = Lesson(
    number=1,
    title="INTRO TO KUBERNETES AND PODS",
    subtitle="THE RETRO TUI ACADEMY FOR LEARNING KUBERNETES",
    beats=BEATS,
    boxes=_boxes(),
)
