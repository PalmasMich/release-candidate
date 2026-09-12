from pathlib import Path
import sys


MAX_IPS_OFFSET = 0xFFFFFF
MAX_RECORD_SIZE = 0xFFFF


def build_ips(source: bytes, target: bytes) -> bytes:
    if len(source) != len(target):
        raise ValueError("Source and target ROMs must have the same size")

    patch = bytearray(b"PATCH")
    index = 0
    length = len(source)

    while index < length:
        if source[index] == target[index]:
            index += 1
            continue

        start = index
        data = bytearray()

        while (
            index < length
            and source[index] != target[index]
            and len(data) < MAX_RECORD_SIZE
        ):
            data.append(target[index])
            index += 1

        if start > MAX_IPS_OFFSET:
            raise ValueError("Difference lies beyond the IPS 24-bit offset limit")

        patch.extend(start.to_bytes(3, "big"))
        patch.extend(len(data).to_bytes(2, "big"))
        patch.extend(data)

    patch.extend(b"EOF")
    return bytes(patch)


def write_ips(source_path: Path, target_path: Path, output_path: Path) -> None:
    source = source_path.read_bytes()
    target = target_path.read_bytes()
    patch = build_ips(source, target)
    output_path.write_bytes(patch)


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(
            "Usage: make_ips.py <source.gbc> <target.gbc> <output.ips>",
            file=sys.stderr,
        )
        return 2

    source_path = Path(argv[1])
    target_path = Path(argv[2])
    output_path = Path(argv[3])

    try:
        write_ips(source_path, target_path, output_path)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Wrote {output_path} ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
