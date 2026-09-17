import pandas as pd
import plotly.express as px
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 진입했던 개봉작 216편의 장르, 국가, 스크린수, 관객수 등의 분포와 상관관계를 분석함.")

# 2. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 및 국가 결측치 및 빈 문자열 처리
    df["genre"] = df["genre"].fillna("기타").astype(str).str.split("|").str[0].str.strip()
    df["genre"] = df["genre"].replace("", "기타")
    df["nation"] = df["nation"].fillna("기타").astype(str).str.strip()
    df["nation"] = df["nation"].replace("", "기타")
    
    # 수치형 데이터 캐스팅
    numeric_columns = ["first_scrn", "first_show", "first_week_audi", "total_audi", "days_in_top10"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        
    return df

# 데이터 로딩
try:
    df = load_data()
except Exception as e:
    st.error(f"❌ 데이터를 불러오는 중 오류가 발생함: {e}")
    st.stop()

st.divider()

# ==========================================
# 📌 구역 1: 장르별 영화 편수 (도넛 그래프)
# ==========================================
st.header("🍩 섹션 1. 장르별 영화 편수 분포")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화편수"]

fig1 = px.pie(
    genre_counts,
    values="영화편수",
    names="장르",
    title="🍕 개봉 영화 장르별 편수 비중",
    hole=0.4
)

fig1.update_traces(
    textinfo="percent+label",
    hovertemplate="<b>장르:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>점유율:</b> %{percent}<extra></extra>"
)

fig1.update_layout(
    legend_title_text="장르 선택 (클릭 시 토글)"
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "1년 동안 박스오피스 상위권에 진입한 영화들의 장르 다변화 정도와 특정 대표 장르의 시장 편중 현상을 한눈에 파악할 수 있음."
)

st.divider()

# ==========================================
# 📌 구역 2: 장르 및 영화별 총 관객 수 (트리맵)
# ==========================================
st.header("🌳 섹션 2. 장르 및 영화별 총 관객 수 분포 (트리맵)")

treemap_df = (
    df[df["total_audi"] > 0]
    .groupby(["genre", "movieNm"], as_index=False)["total_audi"]
    .sum()
)

fig2 = px.treemap(
    treemap_df,
    path=[px.Constant("전체 장르"), "genre", "movieNm"],
    values="total_audi",
    title="🎬 장르 및 영화별 총 관객 수 비중",
    labels={"total_audi": "총 관객 수 (명)", "genre": "장르", "movieNm": "영화명"}
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br><b>총 관객 수:</b> %{value:,}명<extra></extra>"
)

fig2.update_layout(
    margin=dict(t=50, l=10, r=10, b=10)
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "장르별 전체 관객 수 규모와 함께 각 장르 내부에서 특정 대형 흥행작이 차지하는 관객 독점 비율을 면적 크기로 직관적으로 비교할 수 있음."
)

st.divider()

# ==========================================
# 📌 구역 3: 총 관객 수 분포 (히스토그램)
# ==========================================
st.header("📊 섹션 3. 총 관객 수 분포 (히스토그램)")

top_movie_row = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = top_movie_row["total_audi"]

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="🎟️ 개봉작 총 관객 수 구간별 분포",
    labels={"total_audi": "총 관객 수 (명)", "count": "영화 수"},
    color_discrete_sequence=["#636EFA"]
)

fig3.update_traces(
    hovertemplate="<b>관객 수 구간:</b> %{x}명<br><b>영화 수:</b> %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객 수 (명)",
    yaxis_title="영화 수 (편)",
    bargap=0.1
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** "
    f"대부분의 영화가 관객 수 50만 명 이하의 하위 구간에 밀집해 있는 극단적인 롱테일 양상을 보임. "
    f"기간 내 가장 많은 관객을 동원한 최상위 영화는 '{top_movie_name}'({top_movie_audi:,}명)임."
)

st.divider()

# ==========================================
# 📌 구역 4: 개봉일 스크린수와 총 관객수의 관계 (산점도)
# ==========================================
st.header("🎯 섹션 4. 개봉일 스크린수 대비 총 관객수 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="🎬 개봉일 스크린수 대비 총 관객수 분포 (장르별 색상)",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객 수 (명)",
        "genre": "장르"
    }
)

fig4.update_traces(
    hovertemplate="<b>영화명:</b> %{hovertext}<br><b>개봉일 스크린수:</b> %{x:,}개<br><b>총 관객수:</b> %{y:,}명<extra></extra>"
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수 (개)",
    yaxis_title="총 관객 수 (명)",
    legend_title_text="장르"
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "개봉일 스크린수가 많을수록 대체로 총 관객수도 증가하는 비례 관계를 보이지만, "
    "적은 스크린수로 시작해 입소문으로 높은 흥행을 거둔 이외작이나 초기 스크린 대비 아쉬운 성적을 거둔 사례도 함께 확인 가능함."
)

st.divider()

# ==========================================
# 📌 구역 5: 주요 장르별 총 관객 수 분포 (박스플롯)
# ==========================================
st.header("📦 섹션 5. 주요 장르별 총 관객 수 분포 (박스플롯)")

genre_counts_series = df["genre"].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
filtered_df = df[df["genre"].isin(top_genres)]

fig5 = px.box(
    filtered_df,
    x="genre",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="🎬 영화 10편 이상 주요 장르별 총 관객 수 분포",
    labels={"genre": "장르", "total_audi": "총 관객 수 (명)"},
    points="outliers"
)

fig5.update_traces(
    hovertemplate="<b>영화명:</b> %{hovertext}<br><b>총 관객수:</b> %{y:,}명<extra></extra>"
)

fig5.update_layout(
    xaxis_title="장르 (10편 이상)",
    yaxis_title="총 관객 수 (명)",
    showlegend=False
)

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "주요 장르별 관객 수의 중간값과 일반적인 분포 범위를 비교할 수 있으며, "
    "상자 밖으로 튀어나온 이상치(Outlier) 점들을 통해 장르 평균 성적을 압도적으로 뛰어넘은 대형 흥행작을 쉽게 식별할 수 있음."
)

st.divider()

# ==========================================
# 📌 구역 6: 스크린수·총관객수·첫주관객수 관계 (버블 차트)
# ==========================================
st.header("🫧 섹션 6. 스크린수·총관객수·첫주관객수 관계 (버블 차트)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
    title="🎬 개봉일 스크린수 대비 총 관객수 및 첫 주 관객수 분포",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객 수 (명)",
        "first_week_audi": "첫 주 관객 수 (명)",
        "genre": "장르"
    }
)

fig6.update_traces(
    hovertemplate="<b>영화명:</b> %{hovertext}<br><b>개봉일 스크린수:</b> %{x:,}개<br><b>총 관객수:</b> %{y:,}명<br><b>첫 주 관객수:</b> %{marker.size:,}명<extra></extra>"
)

fig6.update_layout(
    xaxis_title="개봉일 스크린수 (개)",
    yaxis_title="총 관객 수 (명)",
    legend_title_text="장르"
)

st.plotly_chart(fig6, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "버블의 크기를 통해 개봉 첫 주 관객 동원력을 시각적으로 비교할 수 있으며, "
    "첫 주 관객 비중이 커서 빠르게 흥행을 거둔 영화와 후반 장기 흥행(입소문)으로 총 관객수를 채운 영화를 쉽게 구분할 수 있음."
)

st.divider()

# ==========================================
# 📌 구역 7: 제작 국가 및 장르별 영화 편수 (선버스트 차트)
# ==========================================
st.header("☀️ 섹션 7. 제작 국가 및 장르별 영화 편수 분포 (선버스트)")

# 계층 구조 데이터 생성 시 중복 제거 및 그룹화 집계 적용
sunburst_df = df.groupby(["nation", "genre"], as_index=False).size()

fig7 = px.sunburst(
    sunburst_df,
    path=["nation", "genre"],
    values="size",
    title="🎬 제작 국가 및 장르별 영화 편수 계층 구조",
    labels={"nation": "제작 국가", "genre": "장르", "size": "영화 편수"}
)

fig7.update_traces(
    hovertemplate="<b>%{label}</b><br><b>영화 편수:</b> %{value}편<extra></extra>"
)

fig7.update_layout(
    margin=dict(t=50, l=10, r=10, b=10)
)

st.plotly_chart(fig7, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "국가별 개봉작 수의 비중과 함께 각 국가가 어떤 장르 위주로 한국 박스오피스 상위권에 진입했는지 계층적 구조로 비교 파악할 수 있음."
)

st.divider()

# ==========================================
# 📌 구역 8: 10위권 체류 일수와 총 관객수의 관계 (산점도)
# ==========================================
st.header("🎯 섹션 8. 10위권에 오래 머문 영화는 총 관객도 많은가")

fig8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={
        "days_in_top10": "10위권에 머문 날수 (일)",
        "total_audi": "총 관객 수 (명)",
        "genre": "장르"
    }
)

fig8.update_traces(
    hovertemplate="<b>영화명:</b> %{hovertext}<br><b>10위권 머문 날수:</b> %{x}일<br><b>총 관객수:</b> %{y:,}명<extra></extra>"
)

fig8.update_layout(
    xaxis_title="10위권에 머문 날수 (일)",
    yaxis_title="총 관객 수 (명)",
    legend_title_text="장르"
)

st.plotly_chart(fig8, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "10위권 체류 일수가 길수록 대체로 총 관객수도 증가하는 양의 상관관계를 보이지만, "
    "짧은 기간 관객을 폭발적으로 모은 단기 흥행작이나 오랜 체류 대비 관객 폭이 넓지 않았던 작품 사례도 함께 확인 가능함."
)
