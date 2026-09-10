import requests
from datetime import datetime, timedelta, timezone
import time

api_key = "%2BuM79zOaknHRa1k50yjOYkVBO8dYs8LEuXF7tjb1WIOwVO7gBjBryQJQ8XYdYDmWwXpaMEtkIckNG40qy9jqug%3D%3D"
bot_token = "8855852977:AAFSc3R9TJlSnp1UY66nY-4jYGL0RGg0I0I"
chat_id = "-5450647167" 

target_keywords = ["자연재해", "풍수해", "지방하천", "재해예방", "하천기본계획", "소하천", "소규모공공시설", "재해", "하천정비사업"]
exclude_keywords = ["공사", "물품", "구매", "제조", "관급자재", "폐기물", "항온습기", "전기", "통신", "소방", "도서관", "학교", "아파트", "환경영향평가", "건설사업", "기술지도", "안전점검"]

def send_tg(msg):
    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(tg_url, data={'chat_id': chat_id, 'text': msg}, timeout=5)
    except:
        pass

def run_sniper_bot():
    KST = timezone(timedelta(hours=9))
    now_kst = datetime.now(KST)
    
    # 1. 텔레그램 생존 보고 (시작)
    send_tg(f"🟢 [작전 개시] 조달청 레이더망 가동 ({now_kst.strftime('%H:%M')})")
    
    end_dt = now_kst.strftime('%Y%m%d2359') 
    
    # 🎯 맞춤형 날짜 세팅
    # 사전규격용 (유령등록 잡기위해 14일 전부터 넉넉하게)
    past_14_dt = (now_kst - timedelta(days=14)).strftime('%Y%m%d0000')
    # 입찰공고용 (데이터 짤림 방지위해 어제부터)
    past_1_dt = (now_kst - timedelta(days=1)).strftime('%Y%m%d0000')

    # 필터링용 날짜 텍스트
    today_str = now_kst.strftime('%Y-%m-%d')
    today_str_no_dash = now_kst.strftime('%Y%m%d')
    yesterday_str = (now_kst - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_str_no_dash = (now_kst - timedelta(days=1)).strftime('%Y%m%d')

    endpoints = {
        "사전규격_용역": f"https://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureServcInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={past_14_dt}&inqryEndDt={end_dt}&type=json",
        "사전규격_공사": f"https://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureCnstwkInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={past_14_dt}&inqryEndDt={end_dt}&type=json",
        "사전규격_물품": f"https://apis.data.go.kr/1230000/ao/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=1&inqryBgnDt={past_14_dt}&inqryEndDt={end_dt}&type=json",
        "입찰공고": f"https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServc?serviceKey={api_key}&numOfRows=999&pageNo=1&inqryDiv=2&inqryBgnDt={past_1_dt}&inqryEndDt={end_dt}&type=json"
    }
    
    found_count = 0
    total_scanned = 0

    for stage_name, url in endpoints.items():
        try:
            res = requests.get(url, timeout=15)
            # 서버가 데이터를 안 주거나 튕겨내면 즉시 에러 보고
            if res.status_code != 200 or not res.text.lstrip().startswith('{'):
                send_tg(f"⚠️ [{stage_name}] 조달청 통신 실패 (API 권한없음 또는 서버에러)")
                continue
            
            data = res.json()
            items = data.get('response', {}).get('body', {}).get('items', [])
            total_scanned += len(items)
            
            for item in items:
                item_str = str(item)
                
                title_candidates = [item.get('pblancNm'), item.get('bidNtceNm'), item.get('bsnsNm'), item.get('rcptNm'), item.get('prdctNm'), item.get('swBizNm'), item.get('cnstwkNm'), item.get('servcNm')]
                title = next((t for t in title_candidates if t), "제목 없음")
                dept = item.get('dminsttNm') or item.get('demandInsttNm') or item.get('orderInsttNm') or item.get('insttNm') or "기관명 없음"
                
                has_target = any(keyword in item_str for keyword in target_keywords)
                has_exclude = any(bad_word in title for bad_word in exclude_keywords)
                
                if has_target and not has_exclude:
                    notice_dt = item.get('bidNtceDt') or item.get('pblancDt') or item.get('rgstDt') or item.get('opnnRegClseDt') or "정보없음"
                    
                    # 🔥 어제 또는 오늘 달력이 찍힌 공고만 발송 (과거 쓰레기 데이터 도배 차단)
                    is_recent = (today_str in notice_dt) or (today_str_no_dash in notice_dt) or (yesterday_str in notice_dt) or (yesterday_str_no_dash in notice_dt)
                    
                    if is_recent:
                        found_count += 1
                        notice_no = item.get('bidNtceNo') or item.get('pblancNo') or item.get('bfSpecRegNo') or "번호없음"
                        notice_ord = item.get('bidNtceOrd') or item.get('pblancOrd') or "00"
                        
                        if notice_no != "번호없음" and "사전규격" not in stage_name:
                            full_notice_no = f"{notice_no}-{notice_ord}"
                        else:
                            full_notice_no = notice_no

                        budget = item.get('asignBdgtAmt') or item.get('presmptPrce') or item.get('bsnsBdgtAmt') or item.get('totPrce') or item.get('asignBdgtAm') or "0"
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
                            f"기관명: {dept}\n"
                            f"날짜: {notice_dt}\n"
                            f"예산: {budget_str}\n"
                            f"{detail_url}"
                        )
                        send_tg(msg)
                        time.sleep(1.0)
        except Exception as e:
            send_tg(f"⚠️ [{stage_name}] 통신 에러: {e}")

    # 2. 텔레그램 생존 보고 (종료 및 결과)
    send_tg(f"🏁 [스캔 완료] 조달청 공고 총 {total_scanned}건 검사 완료.\n- 타겟 발견 및 전송: {found_count}건")

if __name__ == "__main__":
    run_sniper_bot()
