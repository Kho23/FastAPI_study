XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def upload(client, content, filename = "kookmin.xlsx"):
    return client.post("/imports/kookmin", files = {"file": (filename, content, XLSX_TYPE)})

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
    res = upload(client, kookmin_xlsx, filename="kookmin.xls")

    assert res.status_code == 400


def test_upload_rejects_broken_file(client):
    res = upload(client, b"this is not an excel file")

    assert res.status_code == 400


def test_upload_without_file_returns_422(client):
    res = client.post("/imports/kookmin")

    assert res.status_code == 422

def test_unknown_source_returns_400(client, kookmin_xlsx):
    res = client.post("/imports/samsung", files={"file": ("a.xlsx", kookmin_xlsx)})
    assert res.status_code == 400
    assert "카드사는 지원하지 않습니다." in res.json()["detail"]

def test_wrong_layout_xlsx_returns_400(client):
    from io import BytesIO
    from openpyxl import Workbook

    wb = Workbook()
    wb.active.append(["아무", "관계없는", "표"])
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    res = client.post("/imports/kookmin", files={"file": ("x.xlsx", buf, XLSX_TYPE)})

    assert res.status_code == 400
    assert res.json()['detail'] == "KB국민카드 이용내역 형식이 아닙니다."

def test_get_missing_transactions_returns_404(client):
    res = client.get("/transactions/99999")

    assert res.status_code == 404
    assert res.json()['detail'] == "조회된 거래내역이 없습니다."