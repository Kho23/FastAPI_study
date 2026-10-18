XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def upload(client, content):
    return client.post("/imports/kookmin", files={"file": ("kookmin.xlsx", content, XLSX_TYPE)})

def create_category(client, name: str, *keywords: str) -> int:
    """카테고리와 규칙을 만들고 카테고리 id를 돌려준다"""
    category_id = client.post("/categories", json={"name": name}).json()["id"]
    for keyword in keywords:
        client.post(f"/categories/{category_id}/rules", json={"keyword": keyword})
    return category_id

def merchant_categories(client, **params) -> dict:
    """{가맹점명: 카테고리명 또는 None}"""
    items = client.get("/transactions", params=params).json()["items"]
    return {t["merchant"]: t["category"] and t["category"]["name"] for t in items}


def test_create_category_and_rule(client):
    res = client.post("/categories", json={"name": "카페"})
    assert res.status_code == 201
    category_id = res.json()["id"]

    res = client.post(f"/categories/{category_id}/rules", json={"keyword": "커피"})
    assert res.status_code == 201

    categories = client.get("/categories").json()
    assert categories[0]["name"] == "카페"
    assert categories[0]["rules"][0]["keyword"] == "커피"

def test_duplicate_category_returns_400(client):
    create_category(client, "카페")
    res = client.post("/categories", json={"name": "카페"})
    assert res.status_code == 400

def test_rule_for_unknown_category_returns_404(client):
    res = client.post("/categories/999/rules", json={"keyword": "커피"})
    assert res.status_code == 404

def test_empty_category_name_returns_422(client):
    res = client.post("/categories", json={"name": ""})
    assert res.status_code == 422

def test_upload_classifies_by_rule(client, kookmin_xlsx):
    create_category(client, "카페", "커피")
    upload(client, kookmin_xlsx)

    result = merchant_categories(client)
    assert result["테스트커피"] == "카페"
    assert result["테스트마트"] is None

def test_filter_by_category(client, kookmin_xlsx):
    cafe_id = create_category(client, "카페", "커피")
    upload(client, kookmin_xlsx)

    assert client.get("/transactions").json()["total"] == 3   # 필터 없으면 전부
    assert list(merchant_categories(client, category_id=cafe_id)) == ["테스트커피"]

def test_patch_sets_and_clears_category(client, kookmin_xlsx):
    cafe_id = create_category(client, "카페")
    upload(client, kookmin_xlsx)
    transaction_id = client.get("/transactions").json()["items"][0]["id"]

    res = client.patch(f"/transactions/{transaction_id}", json={"category_id": cafe_id})
    assert res.status_code == 200
    assert res.json()["category"]["name"] == "카페"

    res = client.patch(f"/transactions/{transaction_id}", json={"category_id": None})
    assert res.json()["category"] is None

def test_patch_unknown_returns_404(client, kookmin_xlsx):
    upload(client, kookmin_xlsx)
    transaction_id = client.get("/transactions").json()["items"][0]["id"]

    assert client.patch(f"/transactions/{transaction_id}", json={"category_id": 999}).status_code == 404
    assert client.patch("/transactions/999", json={"category_id": None}).status_code == 404

def test_reclassify_keeps_manual_category(client, kookmin_xlsx):
    upload(client, kookmin_xlsx)                     # 규칙이 없어서 전부 미분류
    manual_id = create_category(client, "생활")
    mart = [t for t in client.get("/transactions").json()["items"] if t["merchant"] == "테스트마트"][0]
    client.patch(f"/transactions/{mart['id']}", json={"category_id": manual_id})

    create_category(client, "기타", "테스트")         # 세 가맹점 모두에 걸리는 규칙
    res = client.post("/categories/reclassify")

    assert res.json()["updated"] == 2                 # 미분류였던 2건만
    result = merchant_categories(client)
    assert result["테스트마트"] == "생활"             # 직접 지정한 건 그대로
    assert result["테스트커피"] == "기타"