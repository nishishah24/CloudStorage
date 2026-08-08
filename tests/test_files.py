def create_authenticated_user(
    client,
    username="fileuser",
    email="fileuser@example.com",
):
    password = "TestPass123"

    register_response = client.post(
        "/users/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }

def test_upload_file(client):
    headers = create_authenticated_user(client)

    response = client.post(
        "/files/upload",
        headers=headers,
        files={
            "uploaded_file": (
                "test.txt",
                b"Hello from PyTest!",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["original_name"] == "test.txt"
    assert data["content_type"] == "text/plain"
    assert data["size"] == len(b"Hello from PyTest!")
    assert "id" in data

def test_list_files(client):
    headers = create_authenticated_user(
        client,
        username="listuser",
        email="listuser@example.com",
    )

    upload_response = client.post(
        "/files/upload",
        headers=headers,
        files={
            "uploaded_file": (
                "list-test.txt",
                b"File for list test",
                "text/plain",
            ),
        },
    )

    assert upload_response.status_code == 201

    response = client.get(
        "/files",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["original_name"] == "list-test.txt"
    assert data[0]["content_type"] == "text/plain"


def test_rename_file(client):
    headers = create_authenticated_user(
        client,
        username="renameuser",
        email="renameuser@example.com",
    )

    upload_response = client.post(
        "/files/upload",
        headers=headers,
        files={
            "uploaded_file": (
                "before.txt",
                b"Rename test file",
                "text/plain",
            ),
        },
    )

    assert upload_response.status_code == 201

    file_id = upload_response.json()["id"]

    response = client.patch(
        f"/files/{file_id}/rename",
        headers=headers,
        json={
            "new_name": "after.txt",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == file_id
    assert data["original_name"] == "after.txt"
    assert "stored_name" in data

def test_download_file(client):
    headers = create_authenticated_user(
        client,
        username="downloaduser",
        email="downloaduser@example.com",
    )

    file_content = b"Download test content"

    upload_response = client.post(
        "/files/upload",
        headers=headers,
        files={
            "uploaded_file": (
                "download.txt",
                file_content,
                "text/plain",
            ),
        },
    )

    assert upload_response.status_code == 201

    file_id = upload_response.json()["id"]

    response = client.get(
        f"/files/{file_id}/download",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.content == file_content


def test_delete_file(client):
    headers = create_authenticated_user(
        client,
        username="deleteuser",
        email="deleteuser@example.com",
    )

    upload_response = client.post(
        "/files/upload",
        headers=headers,
        files={
            "uploaded_file": (
                "delete.txt",
                b"Delete test content",
                "text/plain",
            ),
        },
    )

    assert upload_response.status_code == 201

    file_id = upload_response.json()["id"]

    response = client.delete(
        f"/files/{file_id}",
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "File deleted successfully",
    }


def test_user_cannot_access_another_users_file(client):
    user_a_headers = create_authenticated_user(
        client,
        username="usera",
        email="usera@example.com",
    )

    upload_response = client.post(
        "/files/upload",
        headers=user_a_headers,
        files={
            "uploaded_file": (
                "private.txt",
                b"Private content",
                "text/plain",
            ),
        },
    )

    assert upload_response.status_code == 201

    file_id = upload_response.json()["id"]

    user_b_headers = create_authenticated_user(
        client,
        username="userb",
        email="userb@example.com",
    )

    response = client.get(
        f"/files/{file_id}/download",
        headers=user_b_headers,
    )

    assert response.status_code == 403

    assert response.json() == {
        "success": False,
        "error": "You do not have permission to perform this action",
    }