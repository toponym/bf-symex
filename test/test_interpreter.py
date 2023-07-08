"""Tests for Interpreter class"""
import io
import os
from bfsymex import Interpreter

def test_hello_world(capsys):
    """Test using hello-world.bf program"""
    filename = "hello-world.bf"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    expected = "Hello world!\n"
    with open(file_path, 'r', encoding='ascii') as file:
        code = file.read()
        interp = Interpreter(list(code))
        interp.interpret()
    captured = capsys.readouterr()
    assert captured.out == expected

def test_pipe(capsys, monkeypatch):
    """Test using pipe.bf program"""
    filename = "pipe.bf"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    stdin = "hi0 there!\nfriend"
    expected = "hi0 there!"
    monkeypatch.setattr('sys.stdin', io.StringIO(stdin))
    with open(file_path, 'r', encoding='ascii') as file:
        code = file.read()
        interp = Interpreter(list(code))
        interp.interpret()
    captured = capsys.readouterr()
    assert captured.out == expected
