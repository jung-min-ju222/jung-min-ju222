import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="주식회사 NK - 소화장비 WMS", layout="wide"
)

# ---------------------------------------------------------
# 0. 로그인 인증 세션 상태 관리
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

if not st.session_state.authenticated:
  st.title("🔐 주식회사 NK WMS 물류·재고 프로그램 로그인")
  st.markdown("스테이션 카파 재고관리 시스템 접근을 위해 암호를 입력하세요.")

  ADMIN_PASSWORD = "nk1234"  # 필요 시 변경 가능
  input_password = st.text_input("시스템 암호 입력", type="password")

  if st.button("로그인"):
    if input_password == ADMIN_PASSWORD:
      st.session_state.authenticated = True
      st.success("로그인 성공! 시스템에 접속합니다...")
      st.rerun()
    else:
      st.error("❌ 암호가 틀렸습니다. 다시 확인해 주세요.")

  st.stop()


# ---------------------------------------------------------
# 1. WMS 본문 프로그램 (로그인 성공 후)
# ---------------------------------------------------------

st.sidebar.title("👤 사용자 계정")
if st.sidebar.button("로그아웃"):
  st.session_state.authenticated = False
  st.rerun()

st.sidebar.markdown("---")

# 샘플 데이터베이스 초기화
if "inventory_df" not in st.session_state:
  st.session_state.inventory_df = pd.DataFrame([
      {
          "호선 프로젝트": "H-2025 (Engine Room)",
          "랙 위치": "Rack 01~02 (Zone A)",
          "품번": "CY-CO2-68L",
          "품명 및 사양": "68L 고압실린더 + 시리얼",
          "단가(원)": 450000,
          "총 입고": 50,
          "정규 출고": 35,
          "중간 반출": 5,
          "타 호선 할당": 45,
          "안전재고": 10,
          "상태": "🔥 긴급 (D-7일)",
      },
      {
          "호선 프로젝트": "H-2025 (Cargo Hold)",
          "랙 위치": "Rack 03~06 (Zone B)",
          "품번": "VAL-SEL-080",
          "품명 및 사양": "80A 선택밸브 (수입산)",
          "단가(원)": 1800000,
          "총 입고": 10,
          "정규 출고": 6,
          "중간 반출": 2,
          "타 호선 할당": 8,
          "안전재고": 4,
          "상태": "🚨 품절 위험 (D-3일)",
      },
      {
          "호선 프로젝트": "H-2026 (ECR 전장품실)",
          "랙 위치": "Rack 07~10 (Zone C)",
          "품번": "CTR-PAN-CO2",
          "품명 및 사양": "마이크로프로세서 제어반",
          "단가(원)": 5500000,
          "총 입고": 3,
          "정규 출고": 3,
          "중간 반출": 0,
          "타 호선 할당": 3,
          "안전재고": 2,
          "상태": "✅ 안정 (출하대기)",
      },
      {
          "호선 프로젝트": "H-2026 (공통 방호구역)",
          "랙 위치": "Rack 07~10 (Zone C)",
          "품번": "MAN-FLG-50",
          "품명 및 사양": "매니폴드 플랜지 및 노즐",
          "단가(원)": 65000,
          "총 입고": 120,
          "정규 출고": 80,
          "중간 반출": 10,
          "타 호선 할당": 70,
          "안전재고": 30,
          "상태": "✅ 안정",
      },
  ])

df = st.session_state.inventory_df

# 실시간 데이터 연산 (재고 및 금액 자동 계산)
df["현재 잔고"] = df["총 입고"] - (df["정규 출고"] + df["중간 반출"])
df["가용 재고"] = df["현재 잔고"] - df["타 호선 할당"]
df["총 재고 금액(원)"] = df["현재 잔고"] * df["단가(원)"]

# 창고 보관율(%) 계산 로직
MAX_WAREHOUSE_CAPACITY = 500  # 창고 최대 수용 가능 총 수량
current_total_stock = df["현재 잔고"].sum()
warehouse_usage_rate = min(
    float(current_total_stock / MAX_WAREHOUSE_CAPACITY * 100), 100.0
)

# ---------------------------------------------------------
# UI 대시보드 화면 구성 (로고 영역 배치)
# ---------------------------------------------------------
col_logo, col_title = st.columns([1, 4])

with col_logo:
  # 방법 A: 로고 이미지 파일이 있다면 파일명 입력 (예: 'nk_logo.png')
  # 방법 B: 아래처럼 웹 이미지 주소나 공백 처리 가능
  # st.image("nk_logo.png", width=150)
  st.markdown("### 🛡️ 주식회사 NK")
  st.caption("FIRE PROTECTION")

with col_title:
  st.title("조선소 CO2 소화장비 WMS 통합 대시보드")
  st.markdown("호선별 자재 관리, 창고 보관율 모니터링 및 실시간 물류 시스템")

st.divider()

# 상단 KPI 요약 (창고 보관율 % 포함)
col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric(
      label="📦 창고 총 보유 부품 수",
      value=f"{current_total_stock:,} 개",
  )
with col2:
  st.metric(
      label="📊 창고 현재 보관율",
      value=f"{warehouse_usage_rate:.1f} %",
      delta="12줄 랙 기준",
  )
with col3:
  st.metric(
      label="💰 총 재고 자산 가치",
      value=f"{df['총 재고 금액(원)'].sum():,}",
      delta="KRW",
  )
with col4:
  st.metric(label="🚨 공정 지연 리스크 경보", value="2 건", delta_color="inverse")

# 시각적인 창고 보관율 프로그레스 바 표시
st.write(
    f"🏭 **창고 적재 상태 ({current_total_stock}개 / 최대"
    f" {MAX_WAREHOUSE_CAPACITY}개 수용 가능)**"
)
st.progress(warehouse_usage_rate / 100.0)

st.divider()

# 호선별 / 품번 통합 조회
st.subheader("🔍 조선소 프로젝트(호선별) / 품번 통합 조회")
search_hull = st.selectbox(
    "조회할 선박 프로젝트를 선택하세요",
    ["전체 보기"] + list(df["호선 프로젝트"].unique()),
)

if search_hull != "전체 보기":
  filtered_df = df[df["호선 프로젝트"] == search_hull]
else:
  filtered_df = df

st.dataframe(filtered_df, use_container_width=True)

# ---------------------------------------------------------
# 사이드바: 입출고 반영 및 호선 추가 기능
# ---------------------------------------------------------
st.sidebar.header("⚙️ WMS 실시간 물류 작업")

menu_choice = st.sidebar.selectbox(
    "작업을 선택하세요",
    [
        "📦 신규 입고 반영",
        "📤 출고 반영 (정규/중간)",
        "🚢 신규 호선(프로젝트) 추가",
    ],
)

# [1] 신규 입고 반영
if menu_choice == "📦 신규 입고 반영":
  st.sidebar.subheader("📥 신규 입고 등록")
  target_item = st.sidebar.selectbox(
      "입고할 품번 선택", df["품번"].unique().tolist()
  )
  add_qty = st.sidebar.number_input("입고 수량", min_value=1, value=10)

  if st.sidebar.button("입고 반영하기"):
    df.loc[df["품번"] == target_item, "총 입고"] += add_qty
    st.sidebar.success(
        f"✅ [{target_item}] 품목이 {add_qty}개 정상 입고 반영되었습니다!"
    )
    st.rerun()

# [2] 출고 반영
elif menu_choice == "📤 출고 반영 (정규/중간)":
  st.sidebar.subheader("📤 출고 처리")
  out_item = st.sidebar.selectbox(
      "출고할 품번 선택", df["품번"].unique().tolist()
  )
  out_type = st.sidebar.radio(
      "출고 유형", ["정규 출고 (킷팅)", "중간 반출 (AS/시험)"]
  )
  out_qty = st.sidebar.number_input("출고 수량", min_value=1, value=1)

  if st.sidebar.button("출고 반영하기"):
    col_name = "정규 출고" if out_type == "정규 출고 (킷팅)" else "중간 반출"
    current_stock = df.loc[df["품번"] == out_item, "현재 잔고"].values[0]
    if out_qty > current_stock:
      st.sidebar.error("❌ 현재 잔고보다 출고 수량이 많습니다!")
    else:
      df.loc[df["품번"] == out_item, col_name] += out_qty
      st.sidebar.success(
          f"✅ [{out_item}] 품목이 {out_type}으로 {out_qty}개 출고 반영되었습니다!"
      )
      st.rerun()

# [3] 신규 호선 추가
elif menu_choice == "🚢 신규 호선(프로젝트) 추가":
  st.sidebar.subheader("➕ 새로운 조선소 호선 등록")
  new_hull = st.sidebar.text_input(
      "신규 호선명 입력 (예: H-2027 (LNG선))"
  )
  new_loc = st.sidebar.text_input("배정 랙 위치 (예: Rack 11 (Zone D))")
  new_item_code = st.sidebar.text_input("대표 품번 (예: CY-CO2-45L)")
  new_item_name = st.sidebar.text_input(
      "품명 및 사양 (예: 45L 실린더 세트)"
  )
  new_price = st.sidebar.number_input(
      "단가 (원)", min_value=0, value=500000, step=10000
  )
  new_in = st.sidebar.number_input("초기 입고 수량", min_value=0, value=20)

  if st.sidebar.button("호선 추가하기"):
    if new_hull:
      new_row = {
          "호선 프로젝트": new_hull,
          "랙 위치": new_loc if new_loc else "Rack 미지정",
          "품번": new_item_code if new_item_code else "NEW-ITEM",
          "품명 및 사양": new_item_name if new_item_name else "신규 소화장비",
          "단가(원)": new_price,
          "총 입고": new_in,
          "정규 출고": 0,
          "중간 반출": 0,
          "타 호선 할당": 0,
          "안전재고": 5,
          "상태": "🆕 신규 등록",
      }
      st.session_state.inventory_df = pd.concat(
          [df, pd.DataFrame([new_row])], ignore_index=True
      )
      st.sidebar.success(
          f"✅ 새로운 호선 프로젝트 [{new_hull}]가 성공적으로 추가되었습니다!"
      )
      st.rerun()
    else:
      st.sidebar.error("❌ 호선명을 입력해주세요!")
