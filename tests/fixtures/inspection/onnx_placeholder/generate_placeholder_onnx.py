from __future__ import annotations

from pathlib import Path


MODEL_PATH = Path(__file__).with_name("placeholder_identity.onnx")


def main() -> None:
    MODEL_PATH.write_bytes(_placeholder_model())


def _placeholder_model() -> bytes:
    graph = (
        _message(1, _identity_node())
        + _string(2, "kalibra_placeholder_boundary_graph")
        + _message(11, _value_info("raw_input"))
        + _message(12, _value_info("raw_output"))
    )
    opset_import = _int(2, 13)
    return (
        _int(1, 7)
        + _string(2, "kalibra-sprint-1c-fixture")
        + _message(7, graph)
        + _message(8, opset_import)
    )


def _identity_node() -> bytes:
    return (
        _string(1, "raw_input")
        + _string(2, "raw_output")
        + _string(3, "kalibra_placeholder_identity")
        + _string(4, "Identity")
    )


def _value_info(name: str) -> bytes:
    tensor_type = _int(1, 1) + _message(2, _message(1, _int(1, 1)))
    return _string(1, name) + _message(2, _message(1, tensor_type))


def _int(field_number: int, value: int) -> bytes:
    return _key(field_number, 0) + _varint(value)


def _string(field_number: int, value: str) -> bytes:
    return _message(field_number, value.encode("utf-8"))


def _message(field_number: int, value: bytes) -> bytes:
    return _key(field_number, 2) + _varint(len(value)) + value


def _key(field_number: int, wire_type: int) -> bytes:
    return _varint((field_number << 3) | wire_type)


def _varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("varint value must be non-negative")
    parts: list[int] = []
    while value >= 0x80:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    parts.append(value)
    return bytes(parts)


if __name__ == "__main__":
    main()
