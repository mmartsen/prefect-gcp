import pytest
from prefect import flow

from prefect_gcp.secret_manager import (
    create_secret,
    delete_secret,
    delete_secret_version,
    read_secret,
    update_secret,
)


def test_create_secret(gcp_credentials):
    @flow
    def test_flow():
        return create_secret("secret_name", gcp_credentials)

    assert test_flow() == "secret_name"


@pytest.mark.parametrize("secret_value", ["secret", b"secret_byte"])
def test_update_secret(secret_value, gcp_credentials):
    @flow
    def test_flow():
        return update_secret("secret_name", secret_value, gcp_credentials)

    if isinstance(secret_value, str):
        secret_value = secret_value.encode("UTF-8")

    assert test_flow() == secret_value


def test_read_secret(gcp_credentials):
    @flow
    def test_flow():
        return read_secret("secret_name", gcp_credentials)

    expected = "projects/gcp_credentials_project/secrets/secret_name/versions/latest"
    assert test_flow() == expected


@pytest.mark.parametrize("project", [None, "override_project"])
def test_delete_secret(project, gcp_credentials):

    secret_name = "secret_name"

    @flow
    def test_flow():
        return delete_secret(secret_name, gcp_credentials, project=project)

    project = project or gcp_credentials.project
    path = f"projects/{project}/secrets/{secret_name}/"
    assert test_flow() == path


@pytest.mark.parametrize("project", [None, "override_project"])
@pytest.mark.parametrize("version_id", ["latest", 1])
def test_delete_secret_version_id(project, version_id, gcp_credentials):

    secret_name = "secret_name"

    @flow
    def test_flow():
        return delete_secret_version(
            secret_name, version_id, gcp_credentials, project=project
        )

    if version_id == "latest":
        with pytest.raises(ValueError):
            test_flow().result()
    else:
        project = project or gcp_credentials.project
        path = f"projects/{project}/secrets/{secret_name}/versions/{version_id}"
        assert test_flow() == path
