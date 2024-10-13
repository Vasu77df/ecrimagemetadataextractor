import pytest
from unittest.mock import Mock, patch
from ecrimagemetadataextractor.capture_metadata import EcrImageMetadataExtractor, capture_manifest, capture_image_metadata, get_region


@pytest.fixture
def mock_boto3_session():
    with patch('boto3.Session') as mock_session:
        yield mock_session


@pytest.fixture
def mock_requests():
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def ecr_extractor(mock_boto3_session):
    mock_client = Mock()
    mock_boto3_session.return_value.client.return_value = mock_client
    mock_client.get_authorization_token.return_value = {
        'authorizationData': [{'authorizationToken': 'test_token'}]
    }
    return EcrImageMetadataExtractor('123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:latest', 'us-east-1')


def test_parse_ecr_image():
    extractor = EcrImageMetadataExtractor(
        '123456789012.dkr.ecr.us-east-1.amazonaws.com/test-repo:latest', 'us-east-1')
    assert extractor.account == '123456789012'
    assert extractor.registry == '123456789012.dkr.ecr.us-east-1.amazonaws.com'
    assert extractor.ecr_image_name == 'test-repo'
    assert extractor.tag == 'latest'


def test_get_registry_auth_token(ecr_extractor):
    assert ecr_extractor.auth_token == 'test_token'


def test_get_image_manifest(ecr_extractor, mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"layers": [], "config": {"digest": "sha256:1234"}}'
    mock_requests.return_value = mock_response

    manifest = ecr_extractor.get_image_manifest()
    assert manifest == '{"layers": [], "config": {"digest": "sha256:1234"}}'


def test_get_image_manifest_failure(ecr_extractor, mock_requests):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = 'Not Found'
    mock_requests.return_value = mock_response

    with pytest.raises(SystemExit):
        ecr_extractor.get_image_manifest()


def test_get_digest_manifest(ecr_extractor, mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"architecture": "amd64", "os": "linux"}'
    mock_requests.return_value = mock_response

    metadata = ecr_extractor.get_digest_manifest('sha256:1234')
    assert metadata == '{"architecture": "amd64", "os": "linux"}'


def test_get_digest_manifest_failure(ecr_extractor, mock_requests):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = 'Not Found'
    mock_requests.return_value = mock_response

    with pytest.raises(SystemExit):
        ecr_extractor.get_digest_manifest('sha256:1234')


@patch('ecrimagemetadataextractor.capture_metadata.get_region')
@patch('ecrimagemetadataextractor.capture_metadata.EcrImageMetadataExtractor')
def test_capture_manifest(mock_extractor, mock_get_region):
    mock_get_region.return_value = 'us-east-1'
    mock_extractor.return_value.get_image_manifest.return_value = '{"manifest": "data"}'

    capture_manifest('test-image', 'us-east-1')
    mock_extractor.assert_called_once_with('test-image', 'us-east-1')
    mock_extractor.return_value.get_image_manifest.assert_called_once()


@patch('ecrimagemetadataextractor.capture_metadata.get_region')
@patch('ecrimagemetadataextractor.capture_metadata.EcrImageMetadataExtractor')
def test_capture_image_metadata(mock_extractor, mock_get_region):
    mock_get_region.return_value = 'us-east-1'
    mock_extractor.return_value.get_image_manifest.return_value = '{"config": {"digest": "sha256:1234"}}'
    mock_extractor.return_value.get_digest_manifest.return_value = '{"metadata": "data"}'

    capture_image_metadata('test-image', 'us-east-1')
    mock_extractor.assert_called_once_with('test-image', 'us-east-1')
    mock_extractor.return_value.get_image_manifest.assert_called_once()
    mock_extractor.return_value.get_digest_manifest.assert_called_once_with(
        'sha256:1234')


def test_get_region():
    import os

    # Test with provided region
    assert get_region('us-west-2') == 'us-west-2'

    # Test with AWS_REGION environment variable
    os.environ['AWS_REGION'] = 'eu-central-1'
    assert get_region(None) == 'eu-central-1'

    # Test with no region provided and no environment variable
    del os.environ['AWS_REGION']
    with pytest.raises(SystemExit):
        get_region(None)
