import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="2026 KBO 안타 수와 팀 승률 탐색", layout="wide")

st.title("⚾ 2026 KBO: 안타 수가 많으면 팀의 승률도 높은가?")
st.caption("KBO 공식 기록실(koreabaseball.com) 2026 정규시즌 팀 기록 데이터(UTF-8) 초기 탐색 화면")

# 1. CSV 파일 불러오기 (기본: 깃허브 저장소의 2026 KBO CSV)
uploaded_file = st.file_uploader("다른 CSV 파일을 확인하려면 업로드하세요 (UTF-8 인코딩)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="utf-8")
    st.success("업로드한 CSV 파일(UTF-8)을 불러왔습니다.")
else:
    df = pd.read_csv("kbo_2026_hits_winrate.csv", encoding="utf-8")
    st.info("2026 KBO 정규시즌 데이터(kbo_2026_hits_winrate.csv, UTF-8)를 불러왔습니다.")

st.divider()

# 1. 행 개수와 열 개수
rows, cols = df.shape
st.subheader("1. 데이터 크기 (행 개수 및 열 개수)")
col1, col2 = st.columns(2)
col1.metric("행 개수 (팀 수)", f"{rows}행")
col2.metric("열 개수 (기록 항목 수)", f"{cols}열")

# 2. 앞의 10행
st.subheader("2. 데이터 미리보기 (앞의 10행)")
st.dataframe(df.head(10), use_container_width=True)

# 3. 열마다 자료형
st.subheader("3. 열마다 자료형")
dtypes_df = pd.DataFrame({
    "열 이름": df.dtypes.index,
    "자료형": df.dtypes.astype(str).values
})
st.table(dtypes_df)

st.divider()

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
    fig_missing = px.bar(
        missing_df,
        x="열 이름",
        y="빈 값 개수",
        text="빈 값 개수",
        title="열별 빈 값(결측치) 현황"
    )
    fig_missing.update_traces(textposition="outside")
    fig_missing.update_yaxes(rangemode="tozero", dtick=1)
    st.plotly_chart(fig_missing, use_container_width=True)

st.divider()

# 5. 숫자 열 분포(히스토그램) 및 요약 통계
st.subheader("5. 숫자 열 분포(히스토그램) 및 요약 통계")
numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

if numeric_cols:
    default_idx = numeric_cols.index("안타") if "안타" in numeric_cols else 0
    selected_col = st.selectbox("분포를 확인할 숫자 열을 선택하세요", numeric_cols, index=default_idx)
    series = pd.to_numeric(df[selected_col], errors="coerce").dropna()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("최솟값 (Min)", f"{series.min():.3f}" if series.max() < 1 else f"{series.min():.1f}")
    m2.metric("평균 (Mean)", f"{series.mean():.3f}" if series.max() < 1 else f"{series.mean():.1f}")
    m3.metric("중앙값 (Median)", f"{series.median():.3f}" if series.max() < 1 else f"{series.median():.1f}")
    m4.metric("최댓값 (Max)", f"{series.max():.3f}" if series.max() < 1 else f"{series.max():.1f}")

    stat_col, hist_col = st.columns([1, 2])
    with stat_col:
        st.markdown(f"**`{selected_col}` 요약 통계**")
        summary_df = pd.DataFrame({
            "통계 항목": ["유효 데이터 수", "최솟값", "중앙값", "평균", "최댓값"],
            "값": [
                f"{int(series.count())}개",
                round(float(series.min()), 3),
                round(float(series.median()), 3),
                round(float(series.mean()), 3),
                round(float(series.max()), 3)
            ]
        })
        st.table(summary_df)

    with hist_col:
        st.markdown(f"**`{selected_col}` 히스토그램**")
        fig_hist = px.histogram(
            df,
            x=selected_col,
            nbins=8,
            title=f"2026 KBO 팀별 {selected_col} 분포",
            labels={selected_col: selected_col, "count": "팀 수"}
        )
        fig_hist.update_layout(bargap=0.08)
        st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# 6. 주제 핵심 확인: 안타 수와 팀 승률의 관계 (산점도 & 상관계수)
st.subheader("6. 주제 확인: 안타 수와 팀 승률의 관계")

if "안타" in df.columns and "승률" in df.columns:
    corr_val = df["안타"].corr(df["승률"])
    st.metric("안타 수와 승률의 피어슨 상관계수 (r)", f"{corr_val:.3f}")

    fig_scatter = px.scatter(
        df,
        x="안타",
        y="승률",
        text="팀명" if "팀명" in df.columns else None,
        size="득점" if "득점" in df.columns else None,
        color="팀명" if "팀명" in df.columns else None,
        title="2026 KBO 팀별 안타 수 vs 정규시즌 승률 (원 크기: 팀 득점)",
        labels={"안타": "팀 총 안타 수", "승률": "정규시즌 승률"}
    )
    fig_scatter.update_traces(textposition="top center")
    st.plotly_chart(fig_scatter, use_container_width=True)
