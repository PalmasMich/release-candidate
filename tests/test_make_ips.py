from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/release_candidate/make_ips.py"


def apply_ips(source: bytes, patch: bytes) -> bytes:
    if not patch.startswith(b"PATCH") or not patch.endswith(b"EOF"):
        raise AssertionError("Invalid IPS envelope")

    output = bytearray(source)
    cursor = 5
    end = len(patch) - 3

    while cursor < end:
        offset = int.from_bytes(patch[cursor:cursor + 3], "big")
        cursor += 3
        size = int.from_bytes(patch[cursor:cursor + 2], "big")
        cursor += 2

        if size == 0:
            run_length = int.from_bytes(patch[cursor:cursor + 2], "big")
            cursor += 2
            value = patch[cursor]
            cursor += 1
            output[offset:offset + run_length] = bytes([value]) * run_length
        else:
            output[offset:offset + size] = patch[cursor:cursor + size]
            cursor += size

    return bytes(output)


class MakeIpsTests(unittest.TestCase):
    def test_cli_creates_patch_that_reconstructs_target(self):
        source = bytes(range(64))
        target = bytearray(source)
        target[4:9] = b"BUILD"
        target[20:25] = b"PATCH"
        target = bytes(target)

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            source_path = tmpdir / "source.gbc"
            target_path = tmpdir / "target.gbc"
            patch_path = tmpdir / "release-candidate.ips"
            source_path.write_bytes(source)
            target_path.write_bytes(target)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source_path), str(target_path), str(patch_path)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(patch_path.exists())
            reconstructed = apply_ips(source, patch_path.read_bytes())
            self.assertEqual(reconstructed, target)

    def test_cli_rejects_different_rom_sizes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            source_path = tmpdir / "source.gbc"
            target_path = tmpdir / "target.gbc"
            patch_path = tmpdir / "release-candidate.ips"
            source_path.write_bytes(b"1234")
            target_path.write_bytes(b"12345")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source_path), str(target_path), str(patch_path)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("same size", result.stderr)
            self.assertFalse(patch_path.exists())


if __name__ == "__main__":
    unittest.main()
