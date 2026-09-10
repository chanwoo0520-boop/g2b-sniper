import requests
from datetime import datetime, timedelta, timezone
import time

api_key = "%2BuM79zOaknHRa1k50yjOYkVBO8dYs8LEuXF7tjb1WIOwVO7gBjBryQJQ8XYdYDmWwXpaMEtkIckNG40qy9jqug%3D%3D"
bot_token = "8855852977:AAFSc3R9TJlSnp1UY66nY-4jYGL0RGg0I0I"
chat_id = "-5450647167" 

target_keywords = ["자연재해", "풍수해", "지방하천", "재해예방", "하천기본계획", "소하천", "소규모공공시설", "재해", "하천정비사업"]
# 🔥 산업재해, 연구용역 방어막 완벽 추가 완료!
exclude_keywords = ["공사", "물품", "구매", "제조", "관급자재", "폐기물", "폐아스콘", "처리용역", "항온항습기", "전기", "통신", "소방", "도서관", "학교", "아파트", "환경영향평가", "건설사업", "기술지도", "안전점검", "유지보수", "재구축", "시스템", "S/W", "소프트웨어", "산업재해", "연구용역"]

def send_tg(msg):
    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(tg_url, data={'chat_id': chat_id, 'text': msg}, timeout=10)
    except:
        pass

def get_title(item):
    for key in ['bidNtceNm', 'pblancNm', 'bsnsNm', 'rcptNm', 'prdctNm', 'cnstwkNm', 'servcNm', 'korPrcureTgtPrdctNm', 'prdctClsfcNoNm']:
        if item.get(key):
            return str(item.get(key)).strip()
    
    for k, v in item.items():
        if isinstance(v, str) and k.endswith('Nm') and 'instt' not in k.lower() and len(v) > 5:
            return v.strip()
    return "제목 없음"

def get_no(item):
    for key in ['bidNtceNo', 'pblancNo', 'bfSpecRegNo', 'rcptNo', 'prcureRqNo', 'rgstNo', 'ntceNo']:
        if item.get(key):
            return str(item.get(key)).strip()
    return "번호없음"

def run_sniper_bot():
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST)
    send_tg(f"🚀 [V6.1 찐최종] 완벽한 방어막으로 정밀 타격을 시작합니다. ({now.strftime('%H:%M')})")
    
    past = now - timedelta(days=3)
    bgn_dt = past.strftime('%Y%m%d0000') 
    end_dt = now.strftime('%Y%m%d2359') 

    endpoints = {
        "1단계_발주계획": f"https://apis.data.go.kr/1230000/ao/OrderPlanSttusService/getOrderPlanSttusListServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json",
        "2단계_사전규격_용역": f"https://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureServcInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json",
        "2단계_사전규격_공사": f"https://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureCnstwkInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json",
        "2단계_사전규격_물품": f"https://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json",
        "3단계_입찰공고": f"https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json"
    }

    found_count = 0
    total_scanned = 0

    for stage_name, url in endpoints.items():
        try:
            res = requests.get(url, timeout=15)
            if res.status_code != 200 or not res.text.lstrip().startswith('{'):
                continue
            
            data = res.json()
            items = data.get('response', {}).get('body', {}).get('items', [])
            if not items:
                continue
                
            if isinstance(items, dict):
                items = [items]
                
            total_scanned += len(items)
            
            for item in items:
                title = get_title(item)
                dept = item.get('dminsttNm') or item.get('demandInsttNm') or item.get('orderInsttNm') or item.get('insttNm') or "기관명 없음"
                
                has_target = any(kw in title for kw in target_keywords)
                has_exclude = any(bw in title for bw in exclude_keywords)
                
                if has_target and not has_exclude:
                    found_count += 1
                    notice_no = get_no(item)
                    notice_ord = item.get('bidNtceOrd') or item.get('pblancOrd') or "00"
                    
                    if notice_no != "번호없음" and "사전규격" not in stage_name:
                        full_notice_no = f"{notice_no}-{notice_ord}"
                    else:
                        full_notice_no = notice_no

                    notice_dt = item.get('bidNtceDt') or item.get('pblancDt') or item.get('rgstDt') or "정보없음"
                    
                    budget = item.get('asignBdgtAmt') or item.get('presmptPrce') or item.get('bsnsBdgtAmt') or item.get('totPrce') or "0"
                    try:
                        budget_str = f"{int(float(budget)):,}원" if budget != "0" else "정보없음"
                    except:
                        budget_str = str(budget)

                    if "사전규격" in stage_name:
                        detail_url = f"https://www.g2b.go.kr/link/PRVA004_02/?bfSpecRegNo={notice_no}"
                    else:
                        detail_url = f"https://www.g2b.go.kr/link/PNPE027_01/single/?bidPbancNo={notice_no}&bidPbancOrd={notice_ord}"

                    msg = (
                        f"🚨 [{stage_name}] 새 공고 포착\n"
                        f"공고명: {title}\n"
                        f"공고번호: {full_notice_no}\n"
                        f"수요기관: {dept}\n"
                        f"공고일시: {notice_dt}\n"
                        f"배정예산액: {budget_str}\n"
                        f"{detail_url}"
                    )
                    send_tg(msg)
                    time.sleep(1.0)
                    
        except Exception as e:
            continue

    send_tg(f"🏁 [스캔 완료] 총 {total_scanned}건 검사, {found_count}건 전송 완료.")

if __name__ == "__main__":
    run_sniper_bot()
