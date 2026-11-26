import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="데이터 초기 탐색 및 분포 확인", layout="wide")

st.title("📊 데이터 초기 탐색 대시보드")
st.caption("UTF-8 CSV 파일 기본 정보, 결측치 현황, 숫자 열 및 글자 열 분포 탐색")

# 1. CSV 파일 업로드 (UTF-8 인코딩)
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (UTF-8 인코딩)", type=["csv"])

# 파일 업로드 전에도 바로 확인할 수 있는 예시 데이터
sample_csv = """id,gender,age,hypertension,heart_disease,ever_married,work_type,Residence_type,avg_glucose_level,bmi,smoking_status,stroke
9046,Male,67.0,0,1,Yes,Private,Urban,228.69,36.6,formerly smoked,1
51676,Female,61.0,0,0,Yes,Self-employed,Rural,202.21,,never smoked,1
31112,Male,80.0,0,1,Yes,Private,Rural,105.92,32.5,never smoked,1
60182,Female,49.0,0,0,Yes,Private,Urban,171.23,34.4,smokes,1
1665,Female,79.0,1,0,Yes,Self-employed,Rural,174.12,24.0,never smoked,1
56669,Male,81.0,0,0,Yes,Private,Urban,186.21,29.0,formerly smoked,1
53882,Male,74.0,1,1,Yes,Private,Rural,70.09,27.4,never smoked,1
10434,Female,69.0,0,0,No,Private,Urban,94.39,22.8,never smoked,0
27419,Female,59.0,0,0,Yes,Private,Rural,76.15,,Unknown,0
60491,Female,78.0,0,0,Yes,Private,Urban,58.57,24.2,Unknown,0
12109,Female,81.0,1,0,Yes,Private,Rural,80.43,29.7,never smoked,0
12095,Female,61.0,0,1,Yes,Govt_job,Rural,120.46,36.8,smokes,0
"""

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="utf-8")
    st.success("업로드한 CSV 파일(UTF-8)을 불러왔습니다.")
else:
    df = pd.read_csv(io.StringIO(sample_csv), encoding="utf-8")
    st.info("현재는 예시 데이터가 표시됩니다. 위에서 보유하신 UTF-8 CSV 파일을 업로드해 보세요.")

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

num_target_cols = ["age", "avg_glucose_level", "bmi"]
available_num_cols = [c for c in num_target_cols if c in df.columns]

if available_num_cols:
    selected_num_col = st.selectbox("분포를 확인할 숫자 열을 선택하세요", available_num_cols)

    series = pd.to_numeric(df[selected_num_col], errors="coerce").dropna()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("최솟값 (Min)", f"{series.min():.2f}")
    m2.metric("평균 (Mean)", f"{series.mean():.2f}")
    m3.metric("중앙값 (Median)", f"{series.median():.2f}")
    m4.metric("최댓값 (Max)", f"{series.max():.2f}")

    summary_df = pd.DataFrame({
        "통계 항목": ["유효 데이터 수", "최솟값 (min)", "25% (Q1)", "중앙값 (50%)", "평균 (mean)", "75% (Q3)", "최댓값 (max)", "표준편차 (std)"],
        "값": [
            f"{int(series.count())}개",
            round(series.min(), 2),
            round(series.quantile(0.25), 2),
            round(series.median(), 2),
            round(series.mean(), 2),
            round(series.quantile(0.75), 2),
            round(series.max(), 2),
            round(series.std(), 2)
        ]
    })

    stat_col, hist_col = st.columns([1, 2])

    with stat_col:
        st.markdown(f"**`{selected_num_col}` 요약 통계**")
        st.table(summary_df)

    with hist_col:
        st.markdown(f"**`{selected_num_col}` 히스토그램**")
        fig_hist = px.histogram(
            df,
            x=selected_num_col,
            nbins=20,
            title=f"{selected_num_col} 값 분포 히스토그램",
            labels={selected_num_col: selected_num_col, "count": "빈도수(행 개수)"}
        )
        fig_hist.update_layout(bargap=0.05)
        st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.warning("현재 데이터에 age, avg_glucose_level, bmi 열이 없습니다.")

st.divider()

# 6. 글자 열(범주형) 값별 개수 확인
st.subheader("6. 글자 열(`gender`, `smoking_status`, `work_type`) 값별 개수")

cat_target_cols = ["gender", "smoking_status", "work_type"]
available_cat_cols = [c for c in cat_target_cols if c in df.columns]

if available_cat_cols:
    selected_cat_col = st.selectbox("값별 개수를 확인할 글자 열을 선택하세요", available_cat_cols)

    # 결측치 포함 여부까지 한눈에 보이도록 value_counts(dropna=False) 사용
    counts = df[selected_cat_col].fillna("빈 값(NaN)").value_counts()
    ratios = (counts / len(df) * 100).round(1)

    cat_df = pd.DataFrame({
        "항목 값": counts.index.astype(str),
        "개수": counts.values,
        "비율(%)": ratios.values
    })

    cat_left, cat_right = st.columns([1, 2])

    with cat_left:
        st.markdown(f"**`{selected_cat_col}` 항목별 개수 표**")
        st.table(cat_df)

    with cat_right:
        st.markdown(f"**`{selected_cat_col}` 항목별 개수 막대그래프**")
        fig_cat = px.bar(
            cat_df,
            x="항목 값",
            y="개수",
            text="개수",
            color="항목 값",
            title=f"{selected_cat_col} 값별 개수 분포"
        )
        fig_cat.update_traces(textposition="outside")
        fig_cat.update_yaxes(rangemode="tozero", dtick=1)
        fig_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.warning("현재 데이터에 gender, smoking_status, work_type 열이 없습니다.")

st.divider()

# 7. smoking_status 'Unknown' vs 나머지 그룹 나이(age) 비교
st.subheader("7. smoking_status 'Unknown' 그룹과 나머지 그룹의 나이(age) 비교")

if "smoking_status" in df.columns and "age" in df.columns:
    # 분석용 복사본 생성 및 그룹 구분
    comp_df = df.copy()
    comp_df["age"] = pd.to_numeric(comp_df["age"], errors="coerce")
    comp_df = comp_df.dropna(subset=["age"])

    comp_df["흡연상태_구분"] = comp_df["smoking_status"].apply(
        lambda x: "Unknown (미상)" if str(x).strip() == "Unknown" else "나머지 (응답 있음)"
    )

    unknown_age = comp_df[comp_df["흡연상태_구분"] == "Unknown (미상)"]["age"]
    other_age = comp_df[comp_df["흡연상태_구분"] == "나머지 (응답 있음)"]["age"]
    total_age = comp_df["age"]

    # 요약 통계 비교표
    age_compare_df = pd.DataFrame({
        "구분": ["전체", "Unknown (미상)", "나머지 (응답 있음)"],
        "인원수(명)": [len(total_age), len(unknown_age), len(other_age)],
        "최솟값": [round(total_age.min(), 1), round(unknown_age.min(), 1) if len(unknown_age) > 0 else None, round(other_age.min(), 1) if len(other_age) > 0 else None],
        "25% (Q1)": [round(total_age.quantile(0.25), 1), round(unknown_age.quantile(0.25), 1) if len(unknown_age) > 0 else None, round(other_age.quantile(0.25), 1) if len(other_age) > 0 else None],
        "중앙값 (Median)": [round(total_age.median(), 1), round(unknown_age.median(), 1) if len(unknown_age) > 0 else None, round(other_age.median(), 1) if len(other_age) > 0 else None],
        "평균 (Mean)": [round(total_age.mean(), 1), round(unknown_age.mean(), 1) if len(unknown_age) > 0 else None, round(other_age.mean(), 1) if len(other_age) > 0 else None],
        "75% (Q3)": [round(total_age.quantile(0.75), 1), round(unknown_age.quantile(0.75), 1) if len(unknown_age) > 0 else None, round(other_age.quantile(0.75), 1) if len(other_age) > 0 else None],
        "최댓값": [round(total_age.max(), 1), round(unknown_age.max(), 1) if len(unknown_age) > 0 else None, round(other_age.max(), 1) if len(other_age) > 0 else None]
    })

    st.markdown("**그룹별 나이(age) 요약 통계 비교표**")
    st.table(age_compare_df)

    # 색상으로 나눈 나이 히스토그램
    st.markdown("**Unknown vs 나머지 그룹 나이(age) 분포 히스토그램**")
    fig_age_comp = px.histogram(
        comp_df,
        x="age",
        color="흡연상태_구분",
        barmode="overlay",
        nbins=30,
        opacity=0.65,
        color_discrete_map={
            "Unknown (미상)": "#EF553B",
            "나머지 (응답 있음)": "#636EFA"
        },
        labels={"age": "나이 (age)", "count": "인원수", "흡연상태_구분": "구분"},
        title="smoking_status 'Unknown' vs 나머지 그룹의 나이 분포 비교"
    )
    fig_age_comp.update_layout(bargap=0.05)
    st.plotly_chart(fig_age_comp, use_container_width=True)
else:
    st.warning("현재 데이터에 smoking_status 또는 age 열이 없습니다.")
st.divider()

# 8. stroke(뇌졸중 여부) 1인 사람의 수와 비율 및 원그래프
st.subheader("8. stroke(뇌졸중 여부) 분포 및 비율")

if "stroke" in df.columns:
    stroke_series = pd.to_numeric(df["stroke"], errors="coerce").dropna().astype(int)
    total_count = len(stroke_series)
    stroke_1_count = int((stroke_series == 1).sum())
    stroke_0_count = int((stroke_series == 0).sum())

    stroke_1_ratio = (stroke_1_count / total_count * 100) if total_count > 0 else 0
    stroke_0_ratio = (stroke_0_count / total_count * 100) if total_count > 0 else 0

    # 핵심 지표 카드
    s_col1, s_col2, s_col3 = st.columns(3)
    s_col1.metric("전체 인원수", f"{total_count:,}명")
    s_col2.metric("stroke = 1 (발생) 인원수", f"{stroke_1_count:,}명")
    s_col3.metric("stroke = 1 비율", f"{stroke_1_ratio:.2f}%")

    # 요약 표 데이터
    stroke_df = pd.DataFrame({
        "구분": ["stroke = 0 (미발생)", "stroke = 1 (발생)"],
        "인원수(명)": [stroke_0_count, stroke_1_count],
        "비율(%)": [round(stroke_0_ratio, 2), round(stroke_1_ratio, 2)]
    })

    pie_left, pie_right = st.columns([1, 2])

    with pie_left:
        st.markdown("**stroke 값별 인원수 및 비율 표**")
        st.table(stroke_df)

    with pie_right:
        st.markdown("**stroke 비율 원그래프**")
        fig_pie = px.pie(
            stroke_df,
            names="구분",
            values="인원수(명)",
            color="구분",
            color_discrete_map={
                "stroke = 0 (미발생)": "#636EFA",
                "stroke = 1 (발생)": "#EF553B"
            },
            title="전체 데이터 중 stroke(0 vs 1) 비율"
        )
        fig_pie.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("현재 데이터에 stroke 열이 없습니다.")
