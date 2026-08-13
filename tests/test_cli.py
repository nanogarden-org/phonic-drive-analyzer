from pathlib import Path

import phonic_drive_analysis_v2 as analyzer


def test_parser_accepts_single_input():
    args = analyzer.parser().parse_args(["example.wav", "--no-plots"])
    assert args.inputs == ["example.wav"]
    assert args.no_plots is True


def test_resolve_inputs_accepts_filelist(tmp_path: Path):
    # Unsupported/nonexistent audio paths should simply produce no resolved files.
    listing = tmp_path / "tracks.txt"
    listing.write_text("# comment\nmissing.mp3\n", encoding="utf-8")
    assert analyzer.resolve_inputs([f"@{listing}"], recursive=False) == []


def test_slugify_is_filesystem_friendly():
    assert analyzer.slugify("A Track: 01 / Mix") == "A_Track_01_Mix"
