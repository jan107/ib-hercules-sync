import os

import pytest

from rdflib.namespace import XSD

from hercules_sync.git import GitFile
from hercules_sync.synchronization import AdditionOperation, RemovalOperation, \
                                          GraphDiffSyncAlgorithm, NaiveSyncAlgorithm, \
                                          RDFSyncAlgorithm
from hercules_sync.triplestore import LiteralElement, URIElement
from hercules_sync.util.uri_constants import RDFS_COMMENT, RDFS_LABEL, RDFS_SUBCLASSOF, \
                                             RDF_TYPE, OWL_CLASS, OWL_DISJOINT_WITH

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'synchronization')
SOURCE_FILE = 'source.ttl'
TARGET_FILE = 'target.ttl'

ASIO_PREFIX = 'http://www.asio.es/asioontologies/asio#'
EX_PREFIX = 'http://www.semanticweb.org/spitxa/ontologies/2020/1/asio-human-resource#'

@pytest.fixture(scope='module')
def input():
    with open(os.path.join(DATA_DIR, SOURCE_FILE), 'r') as f:
        source_content = f.read()
    with open(os.path.join(DATA_DIR, TARGET_FILE), 'r') as f:
        target_content = f.read()
    return GitFile(None, source_content, target_content)

class TestNaiveSyncAlgorithm:
    @pytest.fixture(scope='class')
    def algorithm(self):
        return NaiveSyncAlgorithm()

    def test_not_implemented(self, algorithm, input):
        with pytest.raises(NotImplementedError) as excpt:
            algorithm.do_algorithm(input)
        assert 'has not been implemented yet' in str(excpt.value)

class TestRDFSyncAlgorithm:
    @pytest.fixture(scope='class')
    def algorithm(self):
        return RDFSyncAlgorithm()

    def test_not_implemented(self, algorithm, input):
        with pytest.raises(NotImplementedError) as excpt:
            algorithm.do_algorithm(input)
        assert 'has not been implemented yet' in str(excpt.value)

class TestGraphSyncAlgorithm:
    @pytest.fixture(scope='class')
    def algorithm(self):
        return GraphDiffSyncAlgorithm()

    def test_basic(self, algorithm, input):
        operations = algorithm.do_algorithm(input)

        administrative_personnel = EX_PREFIX + 'AdministrativePersonnel'
        changed_personnel = EX_PREFIX + 'ChangedPersonnel'
        human_resource = ASIO_PREFIX + 'HumanResource'
        research_personnel = EX_PREFIX + 'ResearchPersonnel'
        technical_personnel = ASIO_PREFIX + 'TechnicalPersonnel'

        addition_ops = [
            AdditionOperation(URIElement(administrative_personnel),
                              URIElement(OWL_DISJOINT_WITH),
                              URIElement(changed_personnel)),
            AdditionOperation(URIElement(changed_personnel),
                              URIElement(RDF_TYPE),
                              URIElement(OWL_CLASS)),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDF_TYPE),
                              URIElement(OWL_CLASS)),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_SUBCLASSOF),
                              URIElement(human_resource)),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_COMMENT),
                              LiteralElement('Personnel devoted to technical suport.', lang='en')),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_LABEL),
                              LiteralElement('Personal tècnic', lang='ca-ad')),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_LABEL),
                              LiteralElement('Personal tècnic', lang='ca-es')),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_LABEL),
                              LiteralElement('Personal técnico', lang='es')),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_LABEL),
                              LiteralElement('Personnel technique', lang='fr')),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_LABEL),
                              LiteralElement('Pessoal técnico', lang='pt')),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_LABEL),
                              LiteralElement(12, datatype=XSD.integer)),
            AdditionOperation(URIElement(technical_personnel),
                              URIElement(RDFS_LABEL),
                              LiteralElement('Technical personnel', lang='en'))
        ]
        removal_ops = [
            RemovalOperation(URIElement(administrative_personnel),
                             URIElement(OWL_DISJOINT_WITH),
                             URIElement(research_personnel)),
            RemovalOperation(URIElement(research_personnel),
                             URIElement(RDF_TYPE),
                             URIElement(OWL_CLASS)),
            RemovalOperation(URIElement(research_personnel),
                             URIElement(RDFS_SUBCLASSOF),
                             URIElement(EX_PREFIX + 'HumanResource'))
        ]
        expected = addition_ops + removal_ops

        assert len(operations) == len(expected)
        _assert_lists_have_same_elements(expected, operations)

def _assert_lists_have_same_elements(expected, result):
    for el in result:
        assert el in expected
    for el in expected:
        assert el in result