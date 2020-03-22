from unittest import mock

import pytest

from hercules_sync.synchronization import AdditionOperation, RemovalOperation
from hercules_sync.triplestore import LiteralElement, TripleInfo, URIElement
from hercules_sync.util.uri_constants import RDFS_LABEL

@pytest.fixture
def mock_triplestore():
    return mock.MagicMock()

@pytest.fixture
def triple():
    subject = URIElement('http://example.org/onto#Person')
    predicate = URIElement(RDFS_LABEL)
    objct = LiteralElement('Persona', 'es')
    return (subject, predicate, objct)

def test_init(triple):
    addition_op = AdditionOperation(*triple)
    assert addition_op._triple_info == TripleInfo(*triple)

def test_str(triple):
    addition_op = AdditionOperation(*triple)
    assert str(addition_op) == f"AdditionOperation: {triple[0]} - {triple[1]} - {triple[2]}"

    removal_op = RemovalOperation(*triple)
    assert str(removal_op) == f"RemovalOperation: {triple[0]} - {triple[1]} - {triple[2]}"

def test_addition(mock_triplestore, triple):
    addition_op = AdditionOperation(*triple)
    addition_op.execute(mock_triplestore)
    mock_triplestore.create_triple.assert_called_once_with(TripleInfo(*triple))

def test_removal(mock_triplestore, triple):
    removal_op = RemovalOperation(*triple)
    removal_op.execute(mock_triplestore)
    mock_triplestore.remove_triple.assert_called_once_with(TripleInfo(*triple))

def test_two_operations_with_same_triple_are_distinct(triple):
    add = AdditionOperation(*triple)
    remove = RemovalOperation(*triple)
    assert add != remove
