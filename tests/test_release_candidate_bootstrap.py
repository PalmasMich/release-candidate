from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseCandidateBootstrapTests(unittest.TestCase):
    def test_rom_header_uses_gbc_compatible_release_candidate_title(self):
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("RGBFIXFLAGS += -Cjv -t RELEASECAND", makefile)
        self.assertNotIn("RGBFIXFLAGS += -Cjv -t PM_CRYSTAL", makefile)
        self.assertNotIn("RGBFIXFLAGS += -Cjv -t REL_CANDIDATE", makefile)

    def test_starting_landmark_is_cagliari(self):
        landmarks = (ROOT / "data/maps/landmarks.asm").read_text(encoding="utf-8")
        self.assertIn('NewBarkTownName:     db "CAGLIARI@"', landmarks)

    def test_starting_town_sign_identifies_release_candidate_bootstrap(self):
        map_script = (ROOT / "maps/NewBarkTown.asm").read_text(encoding="utf-8")
        expected = (
            'NewBarkTownSignText:\n'
            '\ttext "CAGLIARI"\n\n'
            '\tpara "Prima build."\n'
            '\tline "Zero bug."\n'
            '\tcont "Forse."\n'
            '\tdone'
        )
        self.assertIn(expected, map_script)


if __name__ == "__main__":
    unittest.main()
