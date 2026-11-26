import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="안타 수와 팀 승률 데이터 탐색", layout="wide")

st.title("⚾ 안타 수가 많으면 팀의 승률도 높은가?")
st.caption("KBO 팀 기록 데이터(UTF-8) 초기 탐색 화면")

# 다른 UTF-8 CSV 파일도 업로드하여 확인할 수 있는 기능
uploaded_file = st.file_uploader("다른 CSV 파일을 확인하려면 업로드하세요 (UTF-8 인코딩)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="utf-8")
    st.success("업로드한 CSV 파일(UTF-8)을 불러왔습니다.")
else:
    df = pd.read_csv("kbo_hits_winrate.csv", encoding="utf-8")
    st.info("깃허브 저장소의 KBO 데이터(kbo_hits_winrate.csv, UTF-8)를 불러왔습니다.")

st.divider()

# 1. 행 개수와 열 개수
rows, cols = df.shape
st.subheader("1. 행 개수와 열 개수")
col1, col2 = st.columns(2)
col1.metric("행 개수", f"{rows}행")
col2.metric("열 개수", f"{cols}열")

# 2. 앞의 10행
st.subheader("2. 앞의 10행")
st.dataframe(df.head(10), use_container_width=True)

# 3. 열마다 자료형
st.subheader("3. 열마다 자료형")
dtypes_df = pd.DataFrame({
    "열 이름": df.dtypes.index,
    "자료형": df.dtypes.astype(str).values
})
st.table(dtypes_df)

# 4. 열마다 빈 값(결측치) 개수 - 표 & Plotly 막대그래프
st.subheader("4. 열마다 빈 값(결측치) 개수")

missing_counts = df.isnull().sum()
missing_df = pd.DataFrame({
    "열 이름": missing_counts.index,
    "빈 값 개수": missing_counts.values
})

left_col, right_col = st.columns([1, 2])

with left_col:
    st.markdown("**열별 빈 값 개수 표**")
    st.table(missing_df)

with right_col:
    st.markdown("**열별 빈 값 개수 막대그래프**")
    fig = px.bar(
        missing_df,
        x="열 이름",
        y="빈 값 개수",
        text="빈 값 개수",
        title="열별 빈 값(결측치) 현황"
    )
    fig.update_traces(textposition="outside")
    fig.update_yaxes(rangemode="tozero", dtick=1)
    st.plotly_chart(fig, use_container_width=True)
