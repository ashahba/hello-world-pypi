import pytest

from hello_world import __version__, hello
from hello_world.cli import main


def test_default_greeting():
    assert hello() == "Hello, World!"


def test_named_greeting():
    assert hello("PyPI") == "Hello, PyPI!"


def test_cli_default(capsys):
    assert main([]) == 0
    assert capsys.readouterr().out == "Hello, World!\n"


def test_cli_with_name(capsys):
    assert main(["PyPI"]) == 0
    assert capsys.readouterr().out == "Hello, PyPI!\n"


def test_cli_version(capsys):
    # argparse's --version action exits with code 0 after printing.
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out
