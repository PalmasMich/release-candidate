from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")

    if new in text:
        return False

    occurrences = text.count(old)
    if occurrences != 1:
        raise RuntimeError(
            f"Expected exactly one bootstrap target in {path}, found {occurrences}. "
            "The upstream source may have changed."
        )

    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def apply_bootstrap(root: Path = ROOT) -> int:
    changes = 0

    changes += _replace_once(
        root / "Makefile",
        "RGBFIXFLAGS += -Cjv -t PM_CRYSTAL -k 01 -l 0x33 -m MBC3+TIMER+RAM+BATTERY -r 3 -p 0",
        "RGBFIXFLAGS += -Cjv -t REL_CANDIDATE -k 01 -l 0x33 -m MBC3+TIMER+RAM+BATTERY -r 3 -p 0",
    )

    changes += _replace_once(
        root / "data/maps/landmarks.asm",
        'NewBarkTownName:     db "NEW BARK<BSP>TOWN@"',
        'NewBarkTownName:     db "CAGLIARI@"',
    )

    changes += _replace_once(
        root / "maps/NewBarkTown.asm",
        '''NewBarkTownSignText:\n\ttext "NEW BARK TOWN"\n\n\tpara "The Town Where the"\n\tline "Winds of a New"\n\tcont "Beginning Blow"\n\tdone''',
        '''NewBarkTownSignText:\n\ttext "CAGLIARI"\n\n\tpara "Prima build."\n\tline "Zero bug."\n\tcont "Forse."\n\tdone''',
    )

    return changes


if __name__ == "__main__":
    changed = apply_bootstrap()
    print(f"Release Candidate bootstrap applied ({changed} file(s) changed).")
