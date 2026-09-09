import requests
from datetime import datetime, timedelta, timezone
import time

api_key = "%2BuM79zOaknHRa1k50yjOYkVBO8dYs8LEuXF7tjb1WIOwVO7gBjBryQJQ8XYdYDmWwXpaMEtkIckNG40qy9jqug%3D%3D"
bot_token = "8855852977:AAFSc3R9TJlSnp1UY66nY-4jYGL0RGg0I0I"
chat_id = "-5450647167" 

target_keywords = ["자연재해", "풍수해", "지방하천", "재해예방", "하천기본계획", "소하천", "소규모공공시설", "재해", "하천정비사업"]
exclude_keywords = ["공사", "물품", "구매", "제조", "관급자재", "폐기물", "항온습기", "전기", "통신", "소방", "도서관", "학교", "아파트", "환경영향평가", "건설사업", "기술지도", "안전점검"]

def run_sniper_bot():
    KST = timezone(timedelta(hours=9))
    now_kst = datetime.now(KST)
    
    today = now_kst
    yesterday = today - timedelta(days=1)
    bgn_dt = yesterday.strftime('%Y%m%d0000') 
    end_dt = today.strftime('%Y%m%d2359') 

    endpoints = {
        "1단계_발주계획": f"https://apis.data.go.kr/1230000/ao/OrderPlanSttusService/getOrderPlanSttusListServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json",
        "2단계_사전규격": f"https://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json",
        "3단계_입찰공고": f"https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={bgn_dt}&inqryEndDt={end_dt}&type=json"
    }

    for stage_name, url in endpoints.items():
        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200 or not res.text.lstrip().startswith('{'):
                continue
            data = res.json()
            items = data.get('response', {}).get('body', {}).get('items', [])
            
            for item in items:
                title = item.get('pblancNm') or item.get('bidNtceNm') or item.get('bsnsNm') or item.get('prdctNm') or item.get('rcptNm') or item.get('swBizNm') or "제목 없음"
                dept = item.get('dminsttNm') or item.get('demandInsttNm') or item.get('orderInsttNm') or item.get('insttNm') or "기관명 없음"
                
                has_target = any(keyword in title for keyword in target_keywords)
                has_exclude = any(bad_word in title for bad_word in exclude_keywords)
                
                if has_target and not has_exclude:
                    notice_no = item.get('bidNtceNo') or item.get('pblancNo') or "번호없음"
                    notice_ord = item.get('bidNtceOrd') or item.get('pblancOrd') or "00"
                    full_notice_no = f"{notice_no}-{notice_ord}" if notice_no != "번호없음" else "번호없음"
                    order_agency = item.get('orderInsttNm') or dept 
                    notice_dt = item.get('bidNtceDt') or item.get('pblancDt') or item.get('rgstDt') or "정보없음"
                    close_dt = item.get('bidClseDt') or "정보없음"
                    open_dt = item.get('opengDt') or "정보없음"
                    contract_method = item.get('cntrctMthdNm') or item.get('cntrctMthd') or "정보없음"
                    budget = item.get('asignBdgtAmt') or item.get('presmptPrce') or item.get('bsnsBdgtAmt') or item.get('totPrce') or "0"
                    
                    try:
                        budget_str = f"{int(float(budget)):,}원" if budget != "0" else "정보없음"
                    except:
                        budget_str = str(budget)

                    detail_url = item.get('bidNtceDtlUrl') or item.get('pblancDtlUrl') or ""
                    if not detail_url and notice_no != "번호없음":
                        detail_url = f"https://www.g2b.go.kr/link/PNPE027_01/single/?bidPbancNo={notice_no}&bidPbancOrd={notice_ord}"

                    msg = (
                        f"🚨 [{stage_name}] 새 입찰공고\n"
                        f"공고명: {title}\n"
                        f"공고번호: {full_notice_no}\n"
                        f"수요기관: {dept}\n"
                        f"공고기관: {order_agency}\n"
                        f"공고일시: {notice_dt}\n"
                        f"마감일시: {close_dt}\n"
                        f"개찰일: {open_dt}\n"
                        f"계약방법: {contract_method}\n"
                        f"배정예산액: {budget_str}\n"
                        f"{detail_url}"
                    )
                    
                    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    while True:
                        tg_res = requests.post(tg_url, data={'chat_id': chat_id, 'text': msg})
                        if tg_res.status_code == 429:
                            retry_after = tg_res.json().get("parameters", {}).get("retry_after", 10)
                            time.sleep(retry_after + 1)
                        else:
                            break
                    time.sleep(2.0) 
        except Exception as e:
            print(f"통신 에러: {e}")

if __name__ == "__main__":
    run_sniper_bot()
