from pieces.runtime_readiness import pieces_os_not_ready_lines


def test_pieces_os_not_ready_lines_include_context_and_next_steps():
    lines = pieces_os_not_ready_lines("opening a Pieces app")
    text = "\n".join(lines)

    assert lines[0] == "❌ PiecesOS is not reachable while opening a Pieces app."
    assert "pieces install" in text
    assert "pieces open --pieces_os" in text
    assert "pieces version" in text


def test_pieces_os_not_ready_lines_default_context():
    lines = pieces_os_not_ready_lines()

    assert lines[0] == "❌ PiecesOS is not reachable from Pieces CLI."
