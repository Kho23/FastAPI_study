from app.categories.models import CategoryRule, Category

def normalize(text: str) -> str:
    """비교를 위해 공백 제거 및 소문자화"""
    return text.replace(" ", "").lower()

def classify(merchant: str, rules: list[CategoryRule]) -> Category:
    """가맹정명의 키워드로 카테고리를 찾는다.

    긴 키워드부터 검사하며, "쿠팡이츠" "쿠팡" 규칙이 있을 때
    "쿠팡이츠" 가 "쿠팡" 규칙에 걸리는 것을 방지하기 위함
    어느 규칙에도 맞지 않으면 None
    """
    target = normalize(merchant)
    for rule in sorted(rules, key=lambda r: len(r.keyword), reverse=True):
        if normalize(rule.keyword) in target:
            return rule.category
    return None

