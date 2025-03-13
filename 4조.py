import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

 ### 여기에 아이디 비밀번호 자기꺼 입력해야함
# ID, PW 값
id = '아이디'
pw = '비번'

# Site Open (Driver Load)
target = 'https://selc.or.kr/lms/main/MainView.do'

driver = webdriver.Chrome()
driver.get(url=target)

# 요소 Timeout 설정 (암묵적 대기)
driver.implicitly_wait(time_to_wait=3)

# ✅ 팝업 닫기 함수 (여러 개의 팝업을 감지하고 닫음)
def handle_popups():
    """현재 화면에 나타난 모든 팝업을 찾아 닫는 함수"""
    try:
        # 1️⃣ z-index가 높은 팝업 먼저 제거 (화면을 가리는 팝업 숨기기)
        popups = driver.find_elements(By.XPATH, "//div[contains(@class,'popupLayout')]")
        for popup in popups:
            driver.execute_script("arguments[0].style.display='none';", popup)
            print("📌 가려진 팝업을 숨겼습니다!")

        # 2️⃣ 닫기 버튼 클릭 시도 (alt 속성에 '창닫기'가 포함된 모든 이미지 버튼 클릭)
        close_buttons = driver.find_elements(By.XPATH, "//img[contains(@alt,'창닫기')]")
        for close_button in close_buttons:
            driver.execute_script("arguments[0].click();", close_button)
            print("✅ 창닫기 버튼을 클릭했습니다!")

        time.sleep(1)  # 안정성을 위해 약간의 대기 추가

    except Exception as e:
        print(f"🚨 팝업 닫기 중 오류 발생: {e}")

# 🔄 로그인 전 팝업 닫기 실행
handle_popups()

print("✅ 모든 팝업이 닫혔습니다!")



# 로그인 시작
univ_list = driver.find_element(By.ID, 'univ_nm_back')
driver.execute_script("arguments[0].click();", univ_list)
WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick,'한양대학교 ERICA')]"))).click()

driver.find_element(By.ID, 'loginbox_user_id_back').clear()
driver.find_element(By.ID, 'loginbox_user_id_back').send_keys(id)
driver.find_element(By.ID, 'loginbox_user_password_back').clear()
driver.find_element(By.ID, 'loginbox_user_password_back').send_keys(pw)
driver.find_element(By.ID, 'btn_login_action').click()

# 수업 홈으로 이동
driver.find_element(By.XPATH, "//img[contains(@alt,'수업홈')]").click()
driver.get('https://selc.or.kr/lms/lms/class/courseSchedule/doListView.do')
print('메인 화면에 진입 성공했습니다!')

# 미완료 영상 버튼 클릭 함수 정의
def click_first_no_see_btn():
    need_watches = driver.find_elements(By.CSS_SELECTOR, '.lec_cont')
    for element in need_watches:
        status = element.find_elements(By.CSS_SELECTOR, '.learn_act_box dd strong')
        if status:  # (완료가 존재해야 함)
            if status[0].text == '(미완료)':
                print('미완료 입니다. 첫번째 미완료 element를 return 합니다.')
                no_see = element.find_element(By.CSS_SELECTOR, '.btn_lecture_view a')
                return no_see
    print('시청할 영상이 없습니다.')
    return None

# 영상 종료까지 대기 함수 정의
def wait_until_video_end():
    driver.switch_to.frame("popCourseContent")  # iframe 이동

    print('영상이 다 끝날때까지 대기를 시작합니다...')

    while True:
        try:
            # 요소의 텍스트를 가져와서 분할
            calcul_time_text = driver.find_element(By.ID, 'calcul_time').text
            time_parts = calcul_time_text.split(':')

            if len(time_parts) < 2:
                print(f"현재 시간 텍스트 형식이 잘못되었습니다: {calcul_time_text}")
                time.sleep(5)
                continue

            current_minutes = int(time_parts[1])
            target_minutes_text = driver.find_element(By.ID, 'total_time').text.strip()

            if target_minutes_text != '/ 분':  # 로딩이 되야 분이 뜬다. 주의!
                target_minutes = int(re.findall(r"\d+", target_minutes_text)[0])

                # 영상 재생이 끝났으면
                if current_minutes >= target_minutes:
                    print("끝났습니다")
                    break
                else:
                    pass
            time.sleep(10)
        except Exception as e:
            print(f"예외 발생: {e}")
            time.sleep(5)

# 나가기 버튼 클릭 함수 정의
def click_exit():
    print('영상을 다봤으니 Exit합니다.')
    driver.find_element(By.CSS_SELECTOR, '.btn_func a').click()  # 닫기버튼 클릭

    WebDriverWait(driver, 5).until(EC.alert_is_present())
    driver.switch_to.alert.accept()
    driver.refresh()

# 주차별 영상 시청
week_btns = driver.find_elements(By.CSS_SELECTOR, '.module_quick li a')
btn_count = len(week_btns)

for i in range(btn_count):
    print(f'{i + 1}주차 탐색 시작...')
    week_btns[i].click()
    week_btns = driver.find_elements(By.CSS_SELECTOR, '.module_quick li a')  # DOM 구조가 변경되어 다시 버튼들을 가져온다.

    # --메인코드 시작--#
    print('시청해야 할 영상을 확인중입니다...')
    while True:
        no_see = click_first_no_see_btn()  # 첫번째 미완료 버튼을 찾아서 누르기.
        if no_see:
            print('미완료 버튼을 클릭하겠습니다.')
            try:
                # JavaScript를 사용하여 요소를 클릭
                driver.execute_script("arguments[0].click();", no_see)
                wait_until_video_end()  # 영상을 다볼때까지 기다리기
                click_exit()  # 나가기 버튼 누르기

                driver.switch_to.default_content()  # iframe 초기화

                time.sleep(5)  # 안정을 위해 delay
            except Exception as e:
                print(f"버튼 클릭 중 오류 발생: {e}")
        else:
            break
