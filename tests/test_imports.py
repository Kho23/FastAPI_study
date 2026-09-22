XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def upload(client, content, filename = "kookmin.xlsx"):
    return client.post("/imports/excel", files = {"file": (filename, content, XLSX_TYPE)})

def test_upload_saves_transactions(client, kookmin_xlsx):
    res = upload(client, kookmin_xlsx)

    assert res.status_code == 200
    body = res.json()
    assert body['count'] == 3
    assert body['saved'] == 3
    assert body['skipped'] == 0
    assert body['total_amount'] == 45500

def test_upload_same_file_twice_skips_duplicates(client, kookmin_xlsx):
    upload(client, kookmin_xlsx)
    kookmin_xlsx.seek(0)
    res = upload(client, kookmin_xlsx)

    body = res.json()
    assert body['saved'] == 0
    assert body['skipped'] == 3

def test_uploaded_transactions_can_be_listed(client, kookmin_xlsx):
    res = upload(client, kookmin_xlsx)
    assert res.status_code == 200

def test_upload_rejects_non_xlsx_extension(client, kookmin_xlsx):
    response = upload(client, kookmin_xlsx, filename="kookmin.xls")

    assert response.status_code == 400


def test_upload_rejects_broken_file(client):
    response = upload(client, b"this is not an excel file")

    assert response.status_code == 400


def test_upload_without_file_returns_422(client):
    response = client.post("/imports/excel")

    assert response.status_code == 422
