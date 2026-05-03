from __future__ import annotations

from collections.abc import Mapping
from typing import Any
import re

import torch
import torch.nn as nn


_STATE_DICT_KEYS = (
    "state_dict",
    "model_state_dict",
    "model",
    "net",
    "weights",
)


def _looks_like_state_dict(obj: Any) -> bool:
    if not isinstance(obj, Mapping):
        return False
    if not obj:
        return False

    # Heuristic: a state_dict is a mapping of str -> Tensor-like.
    for key, value in obj.items():
        if not isinstance(key, str):
            return False
        if not torch.is_tensor(value):
            return False
    return True


def extract_state_dict(checkpoint: Any) -> Mapping[str, torch.Tensor]:
    """Extract a PyTorch state_dict from common checkpoint formats.

    Supports:
    - raw state_dict (mapping of parameter_name -> tensor)
    - wrapped checkpoints with keys like 'model_state_dict'/'state_dict'
    """

    if _looks_like_state_dict(checkpoint):
        return checkpoint

    if isinstance(checkpoint, Mapping):
        for key in _STATE_DICT_KEYS:
            candidate = checkpoint.get(key)
            if _looks_like_state_dict(candidate):
                return candidate

    raise ValueError(
        "Unsupported checkpoint format: expected a state_dict or a dict containing "
        f"one of {list(_STATE_DICT_KEYS)}"
    )


def normalize_state_dict_keys(state_dict: Mapping[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    """Normalize common key prefixes (e.g., DataParallel's 'module.')."""

    if any(k.startswith("module.") for k in state_dict.keys()):
        return {k.removeprefix("module."): v for k, v in state_dict.items()}

    return dict(state_dict)


def load_state_dict_from_path(path: str, *, map_location: str | torch.device = "cpu") -> dict[str, torch.Tensor]:
    checkpoint = torch.load(path, map_location=map_location)
    state_dict = extract_state_dict(checkpoint)
    return normalize_state_dict_keys(state_dict)


_CLASSIFIER_KEY_RE = re.compile(r"^classifier\.(\d+)\.(.+)$")


def build_classifier_from_state_dict(
    state_dict: Mapping[str, torch.Tensor],
    *,
    expected_num_classes: int | None = None,
) -> nn.Sequential | None:
    """Reconstruct a `model.classifier` Sequential from checkpoint keys.

    The saved models in this repo sometimes replace EfficientNet's default
    `classifier` head with a deeper Sequential (extra Linear/BatchNorm/etc).

    Because `state_dict` keys include the Sequential indices (e.g.
    `classifier.8.weight`), we must rebuild a Sequential with matching indices
    to successfully load weights.

    Returns None if the checkpoint does not contain any `classifier.*` keys.
    """

    linear_shapes: dict[int, tuple[int, int]] = {}  # idx -> (in_features, out_features)
    bn_features: dict[int, int] = {}  # idx -> num_features
    classifier_indices: set[int] = set()

    for key, tensor in state_dict.items():
        match = _CLASSIFIER_KEY_RE.match(key)
        if not match:
            continue

        idx = int(match.group(1))
        suffix = match.group(2)
        classifier_indices.add(idx)

        if suffix == "weight":
            if tensor.ndim == 2:
                out_features, in_features = tensor.shape
                linear_shapes[idx] = (int(in_features), int(out_features))
            elif tensor.ndim == 1:
                # Distinguish BatchNorm1d from LayerNorm by the presence of running stats.
                if (
                    f"classifier.{idx}.running_mean" in state_dict
                    and f"classifier.{idx}.running_var" in state_dict
                ):
                    bn_features[idx] = int(tensor.numel())

    if not classifier_indices:
        return None

    max_idx = max(classifier_indices)

    kind: dict[int, str] = {}
    for i in range(max_idx + 1):
        if i in linear_shapes:
            kind[i] = "linear"
        elif i in bn_features:
            kind[i] = "bn"
        else:
            kind[i] = "gap"

    def prev_param_kind(i: int) -> str | None:
        for j in range(i - 1, -1, -1):
            if kind.get(j) != "gap":
                return kind[j]
        return None

    def next_param_kind(i: int) -> str | None:
        for j in range(i + 1, max_idx + 1):
            if kind.get(j) != "gap":
                return kind[j]
        return None

    modules: list[nn.Module] = []
    for i in range(max_idx + 1):
        if kind[i] == "linear":
            in_features, out_features = linear_shapes[i]
            modules.append(nn.Linear(in_features, out_features))
            continue

        if kind[i] == "bn":
            modules.append(nn.BatchNorm1d(bn_features[i]))
            continue

        # For indices without parameters, try to approximate common patterns:
        # Linear -> ReLU -> BatchNorm -> Dropout -> Linear -> ...
        prev_kind = prev_param_kind(i)
        next_kind = next_param_kind(i)
        if i == 0:
            modules.append(nn.Dropout(p=0.2, inplace=True))
        elif prev_kind == "linear" and next_kind == "bn":
            modules.append(nn.ReLU(inplace=True))
        elif prev_kind == "bn" and next_kind == "linear":
            modules.append(nn.Dropout(p=0.2))
        elif prev_kind == "linear" and next_kind == "linear":
            modules.append(nn.ReLU(inplace=True))
        else:
            modules.append(nn.Identity())

    classifier = nn.Sequential(*modules)

    if expected_num_classes is not None and linear_shapes:
        last_linear_idx = max(linear_shapes)
        _, last_out_features = linear_shapes[last_linear_idx]
        if last_out_features != expected_num_classes:
            raise ValueError(
                "Checkpoint classifier output size does not match expected number of classes: "
                f"checkpoint={last_out_features}, expected={expected_num_classes}"
            )

    return classifier
