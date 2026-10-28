# ==========================================
# 01. 라이브러리 및 환경 설정
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ==========================================
# 02. 데이터 불러오기
# ==========================================

df = pd.read_excel("data/Online Retail.xlsx")


# ==========================================
# 03. 데이터 기본 구조 확인
# ==========================================

print("\n==============================")
print("데이터 기본 구조")
print("==============================")

print("행/열:", df.shape)
print("변수:", df.columns.tolist())

print("\n[데이터 타입]")
print(df.dtypes)

print("\n[결측치]")
print(df.isnull().sum())

print("\n[중복 데이터]")
print(df.duplicated().sum())


# ==========================================
# 04. 데이터 품질 확인
# ==========================================

print("\n==============================")
print("데이터 품질 확인")
print("==============================")

print("\n[수치형 변수 통계]")
print(df[["Quantity", "UnitPrice"]].describe())

print("\n[취소 주문 수]")
cancel_invoice = df["InvoiceNo"].astype(str).str.startswith("C")
print(cancel_invoice.sum())

print("\n[음수 수량 거래 수]")
negative_quantity = df["Quantity"] < 0
print(negative_quantity.sum())

print("\n[0원 거래 수]")
print((df["UnitPrice"] == 0).sum())

print("\n[음수 단가 거래 수]")
print((df["UnitPrice"] < 0).sum())


# ==========================================
# 05. 정상 구매 데이터 정의
# ==========================================

"""
분석 목적에 맞게 다음 조건을 만족하는 거래만 사용한다.

1. CustomerID가 존재하는 거래
2. Quantity가 0보다 큰 거래
3. UnitPrice가 0보다 큰 거래

이를 통해 취소/반품 거래와
구매 고객을 식별할 수 없는 거래를 제외한다.
"""

normal_data = df[
    (df["CustomerID"].notna()) &
    (df["Quantity"] > 0) &
    (df["UnitPrice"] > 0)
].copy()


# ==========================================
# 06. 거래금액 계산
# ==========================================

normal_data["TotalPrice"] = (
    normal_data["Quantity"] *
    normal_data["UnitPrice"]
)


# ==========================================
# 07. 중복 데이터 제거
# ==========================================

before = len(normal_data)

normal_data = normal_data.drop_duplicates()

after = len(normal_data)

print("\n==============================")
print("중복 데이터 제거")
print("==============================")

print("제거 전:", before)
print("제거 후:", after)
print("제거된 중복:", before - after)


# ==========================================
# 08. 최종 데이터 확인
# ==========================================

print("\n==============================")
print("최종 분석 데이터")
print("==============================")

print("행 개수:", len(normal_data))
print("열 개수:", len(normal_data.columns))

print("\n[결측치]")
print(normal_data.isnull().sum())

print("\n[데이터 타입]")
print(normal_data.dtypes)

# ==========================================
# STEP 1. 전체 구매 규모
# ==========================================

analysis_start = normal_data["InvoiceDate"].min()
analysis_end = normal_data["InvoiceDate"].max()

total_customers = normal_data["CustomerID"].nunique()
total_orders = normal_data["InvoiceNo"].nunique()
total_sales = normal_data["TotalPrice"].sum()
total_countries = normal_data["Country"].nunique()


print("\n==============================")
print("STEP 1. 전체 구매 규모")
print("==============================")

print(f"분석 기간: {analysis_start} ~ {analysis_end}")
print(f"고객 수: {total_customers:,}명")
print(f"주문 수: {total_orders:,}건")
print(f"총 구매금액: {total_sales:,.2f}")
print(f"국가 수: {total_countries}개")


# ==========================================
# STEP 2. 월별 구매 추이
# ==========================================

normal_data["YearMonth"] = (
    normal_data["InvoiceDate"].dt.to_period("M")
)


# 월별 매출
monthly_sales = (
    normal_data
    .groupby("YearMonth")["TotalPrice"]
    .sum()
)


# 월별 주문 수
monthly_orders = (
    normal_data
    .groupby("YearMonth")["InvoiceNo"]
    .nunique()
)


print("\n==============================")
print("STEP 2. 월별 구매 추이")
print("==============================")

print("\n[월별 매출]")
print(monthly_sales)

print("\n[월별 주문 수]")
print(monthly_orders)


# 월별 매출 시각화
plt.figure(figsize=(12, 6))

plt.plot(
    monthly_sales.index.astype(str),
    monthly_sales.values,
    marker="o"
)

plt.title("월별 매출 추이")
plt.xlabel("월")
plt.ylabel("매출")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "images/monthly_sales.png",
    dpi=300
)

# ==========================================
# STEP 3. 주문 분석
# ==========================================

# 주문별 총 구매금액
order_sales = (
    normal_data
    .groupby("InvoiceNo")["TotalPrice"]
    .sum()
)

# 주문당 평균 구매금액
aov = order_sales.mean()

# 구매금액이 높은 순서로 정렬
order_sales_sorted = order_sales.sort_values(
    ascending=False
)

# 상위 10개 주문 매출 비중
top10_sales = order_sales_sorted.head(10).sum()
top10_ratio = top10_sales / total_sales * 100

# 상위 1% 주문 매출 비중
top1_count = int(len(order_sales) * 0.01)

top1_sales = (
    order_sales_sorted
    .head(top1_count)
    .sum()
)

top1_ratio = top1_sales / total_sales * 100

print("\n==============================")
print("STEP 3. 주문 분석")
print("==============================")

print(f"주문당 평균 구매금액(AOV): {aov:,.2f}")

print("\n[주문금액 통계]")
print(order_sales.describe())

print("\n[구매금액 상위 10개 주문]")
print(order_sales_sorted.head(10))

print("\n[매출 집중도]")
print(f"상위 10개 주문 매출 비중: {top10_ratio:.2f}%")
print(f"상위 1% 주문 매출 비중: {top1_ratio:.2f}%")

# ==========================================
# STEP 4. 국가별 구매 분석
# ==========================================

country_analysis = (
    normal_data
    .groupby("Country")
    .agg(
        CustomerCount=("CustomerID", "nunique"),
        OrderCount=("InvoiceNo", "nunique"),
        TotalSales=("TotalPrice", "sum")
    )
)

# 고객 1인당 평균 매출
country_analysis["SalesPerCustomer"] = (
    country_analysis["TotalSales"] /
    country_analysis["CustomerCount"]
)

# 총 매출 기준 내림차순 정렬
country_sales = (
    country_analysis
    .sort_values("TotalSales", ascending=False)
)

print("\n==============================")
print("STEP 4. 국가별 구매 분석")
print("==============================")

print("\n[국가별 구매 분석]")
print(country_sales)

print("\n[매출 상위 10개 국가]")
print(
    country_sales
    .head(10)
)

# ==========================================
# STEP 5. 고객별 구매행동 분석
# ==========================================

customer_analysis = (
    normal_data
    .groupby("CustomerID")
    .agg(
        OrderCount=("InvoiceNo", "nunique"),
        TotalQuantity=("Quantity", "sum"),
        TotalSales=("TotalPrice", "sum")
    )
)

# 고객별 평균 주문금액
customer_analysis["AverageOrderValue"] = (
    customer_analysis["TotalSales"] /
    customer_analysis["OrderCount"]
)

print("\n==============================")
print("STEP 5. 고객별 구매행동 분석")
print("==============================")

print("\n[고객별 구매행동 통계]")
print(customer_analysis.describe())

print("\n[구매금액 상위 고객]")
print(
    customer_analysis
    .sort_values("TotalSales", ascending=False)
    .head(10)
)

print("\n[구매 빈도 상위 고객]")
print(
    customer_analysis
    .sort_values("OrderCount", ascending=False)
    .head(10)
)

# ==========================================
# STEP 6. RFM 고객 분석
# ==========================================

# 분석 기준일
analysis_date = normal_data["InvoiceDate"].max()

# 고객별 RFM 계산
rfm = (
    normal_data
    .groupby("CustomerID")
    .agg(
        Recency=("InvoiceDate", lambda x:
                 (analysis_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("TotalPrice", "sum")
    )
)

print("\n==============================")
print("STEP 6. RFM 고객 분석")
print("==============================")

print("\n[분석 기준일]")
print(analysis_date)

print("\n[RFM 통계]")
print(rfm.describe())

print("\n[최근 구매 고객]")
print(
    rfm
    .sort_values("Recency")
    .head(10)
)

print("\n[구매 빈도 상위 고객]")
print(
    rfm
    .sort_values("Frequency", ascending=False)
    .head(10)
)

print("\n[구매금액 상위 고객]")
print(
    rfm
    .sort_values("Monetary", ascending=False)
    .head(10)
)

# ==========================================
# STEP 6-2. RFM 점수화
# ==========================================

# Recency
# 최근 구매 고객일수록 높은 점수
rfm["R_Score"] = pd.qcut(
    rfm["Recency"],
    5,
    labels=[5, 4, 3, 2, 1]
)

# Frequency
# 구매 빈도가 높을수록 높은 점수
rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
)

# Monetary
# 구매금액이 높을수록 높은 점수
rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
)

# RFM 종합 점수
rfm["RFM_Score"] = (
    rfm["R_Score"].astype(int) +
    rfm["F_Score"].astype(int) +
    rfm["M_Score"].astype(int)
)

print("\n==============================")
print("STEP 6-2. RFM 점수화")
print("==============================")

print("\n[RFM 점수 통계]")
print(
    rfm[
        ["R_Score", "F_Score", "M_Score", "RFM_Score"]
    ].describe()
)

print("\n[RFM 점수 상위 고객]")
print(
    rfm
    .sort_values("RFM_Score", ascending=False)
    .head(10)
)

print("\n==============================")
print("STEP 6. 고객 세그먼트 생성")
print("==============================")

def segment_customer(row):

    if (
        row["R_Score"] >= 4 and
        row["F_Score"] >= 4 and
        row["M_Score"] >= 4
    ):
        return "VIP_핵심고객"

    elif (
        row["F_Score"] >= 4 and
        row["M_Score"] >= 3
    ):
        return "충성고객"

    elif (
        row["R_Score"] >= 4 and
        row["F_Score"] <= 3
    ):
        return "잠재우수고객"

    elif (
        row["R_Score"] <= 2 and
        row["F_Score"] >= 3
    ):
        return "이탈위험고객"

    else:
        return "일반고객"


rfm["Segment"] = rfm.apply(segment_customer, axis=1)

print("\n[세그먼트별 고객 수]")
print(rfm["Segment"].value_counts())

print("\n[세그먼트별 고객 비율]")
print(
    rfm["Segment"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\n==============================")
print("STEP 6-2. 세그먼트별 구매행동 비교")
print("==============================")

segment_analysis = (
    rfm
    .groupby("Segment")
    .agg(
        CustomerCount=("Monetary", "count"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        AvgMonetary=("Monetary", "mean"),
        TotalSales=("Monetary", "sum")
    )
)

# 전체 매출에서 각 세그먼트가 차지하는 비율
segment_analysis["SalesShare"] = (
    segment_analysis["TotalSales"]
    / segment_analysis["TotalSales"].sum()
    * 100
)

# 보기 좋게 반올림
segment_analysis = segment_analysis.round(2)

print("\n[세그먼트별 구매행동]")
print(segment_analysis)

# 세그먼트 순서 지정
segment_order = [
    "VIP_핵심고객",
    "충성고객",
    "잠재우수고객",
    "이탈위험고객",
    "일반고객"
]

# 데이터 정렬
plot_data = segment_analysis.reindex(segment_order)


# ==========================================
# STEP 6-3. 고객 세그먼트 분류
# ==========================================

def segment_customer(row):

    # 최근성, 빈도, 구매금액이 모두 높은 고객
    if (
        row["R_Score"] >= 4
        and row["F_Score"] >= 4
        and row["M_Score"] >= 4
    ):
        return "VIP_핵심고객"

    # 구매 빈도와 구매금액이 높은 고객
    elif (
        row["F_Score"] >= 4
        and row["M_Score"] >= 3
    ):
        return "충성고객"

    # 최근 구매했지만 구매 빈도가 낮은 고객
    elif (
        row["R_Score"] >= 4
        and row["F_Score"] <= 3
    ):
        return "잠재우수고객"

    # 과거 구매활동은 있지만 최근 구매가 뜸한 고객
    elif (
        row["R_Score"] <= 2
        and row["F_Score"] >= 3
    ):
        return "이탈위험고객"

    # 그 외 고객
    else:
        return "일반고객"


# 세그먼트 적용
rfm["Segment"] = rfm.apply(
    segment_customer,
    axis=1
)

print("\n==============================")
print("STEP 6-3. 고객 세그먼트 분류")
print("==============================")

print("\n[세그먼트별 고객 수]")
print(
    rfm["Segment"]
    .value_counts()
)

print("\n[세그먼트별 비율]")
print(
    rfm["Segment"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\n[세그먼트별 RFM 평균]")
print(
    rfm
    .groupby("Segment")[
        ["Recency", "Frequency", "Monetary"]
    ]
    .mean()
)


# ==========================================
# STEP 6-4. 세그먼트별 매출 기여도 분석
# ==========================================

segment_analysis = (
    rfm
    .groupby("Segment")
    .agg(
        CustomerCount=("Monetary", "size"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        AvgMonetary=("Monetary", "mean"),
        TotalSales=("Monetary", "sum")
    )
)

# 전체 고객 대비 비중
segment_analysis["CustomerShare"] = (
    segment_analysis["CustomerCount"]
    / total_customers * 100
)

# 전체 매출 대비 비중
segment_analysis["SalesShare"] = (
    segment_analysis["TotalSales"]
    / total_sales * 100
)

# 세그먼트 출력 순서
segment_order = [
    "VIP_핵심고객",
    "충성고객",
    "잠재우수고객",
    "이탈위험고객",
    "일반고객"
]

segment_analysis = segment_analysis.reindex(
    segment_order
)

print("\n==============================")
print("STEP 6-4. 세그먼트별 매출 기여도")
print("==============================")

print("\n[세그먼트별 분석]")
print(segment_analysis.round(2))

print("\n[전체 매출 비중 합계]")
print(
    segment_analysis["SalesShare"].sum().round(2)
)

print("\n[전체 고객 수 합계]")
print(
    segment_analysis["CustomerCount"].sum()
)

# ==========================================
# STEP 6-5. 세그먼트별 매출 비중 시각화
# ==========================================

plt.figure(figsize=(10, 6))

plt.bar(
    segment_analysis.index,
    segment_analysis["SalesShare"]
)

plt.title("세그먼트별 매출 비중")
plt.xlabel("고객 세그먼트")
plt.ylabel("매출 비중 (%)")

plt.tight_layout()

plt.savefig(
    "images/segment_share.png",
    dpi=300
)

# ==========================================
# STEP 7. 세그먼트별 상품 선호 분석
# ==========================================

# 고객별 세그먼트 정보를 거래 데이터에 연결
normal_data["Segment"] = (
    normal_data["CustomerID"]
    .map(rfm["Segment"])
)

print("\n==============================")
print("STEP 7. 세그먼트별 상품 선호 분석")
print("==============================")

print("\n[세그먼트 결측치 확인]")
print(normal_data["Segment"].isnull().sum())

# ==========================================
# STEP 7-2. 세그먼트별 상품 고객 침투율
# ==========================================

# 일반 상품만 분석
product_data = normal_data[
    ~normal_data["Description"].isin(
        ["POSTAGE", "Manual"]
    )
].copy()

# 세그먼트별 고객 수
segment_customer_count = (
    rfm["Segment"]
    .value_counts()
)

# 상품별 구매 고객 수
product_penetration = (
    product_data
    .groupby(
        ["Segment", "Description"]
    )["CustomerID"]
    .nunique()
    .reset_index(name="CustomerCount")
)

# 해당 세그먼트의 전체 고객 수 연결
product_penetration["SegmentCustomerCount"] = (
    product_penetration["Segment"]
    .map(segment_customer_count)
)

# 고객 침투율 계산
product_penetration["CustomerPenetration"] = (
    product_penetration["CustomerCount"]
    / product_penetration["SegmentCustomerCount"]
    * 100
)

print("\n==============================")
print("STEP 7-2. 세그먼트별 상품 고객 침투율")
print("==============================")

print("\n[분석 대상 거래 수]")
print(f"전체 거래: {len(normal_data):,}")
print(f"상품 거래: {len(product_data):,}")

print("\n[VIP 핵심고객 상품 침투율 상위 10개]")

print(
    product_penetration[
        product_penetration["Segment"] == "VIP_핵심고객"
    ]
    .sort_values(
        "CustomerPenetration",
        ascending=False
    )
    .head(10)
)

# ==========================================
# STEP 7-3. 세그먼트별 상품 선호도 지수
# ==========================================

# 전체 고객 기준 상품 구매 고객 수
overall_product = (
    product_data
    .groupby("Description")["CustomerID"]
    .nunique()
    .reset_index(name="OverallCustomerCount")
)

# 전체 고객 대비 상품 침투율
overall_product["OverallPenetration"] = (
    overall_product["OverallCustomerCount"]
    / total_customers
    * 100
)

# 세그먼트별 상품 데이터와 결합
product_penetration = product_penetration.merge(
    overall_product[
        ["Description", "OverallPenetration"]
    ],
    on="Description",
    how="left"
)

# 선호도 지수 계산
product_penetration["PreferenceIndex"] = (
    product_penetration["CustomerPenetration"]
    / product_penetration["OverallPenetration"]
)

print("\n==============================")
print("STEP 7-3. 세그먼트별 상품 선호도 지수")
print("==============================")

print("\n[VIP 핵심고객 선호도 지수 상위 10개]")

print(
    product_penetration[
        product_penetration["Segment"] == "VIP_핵심고객"
    ]
    .sort_values(
        "PreferenceIndex",
        ascending=False
    )
    .head(10)
)

# ==========================================
# STEP 7-4. 핵심 상품 필터링
# ==========================================

min_customer_count = 10

core_products = (
    product_penetration[
        product_penetration["CustomerCount"]
        >= min_customer_count
    ]
    .sort_values(
        ["Segment", "PreferenceIndex"],
        ascending=[True, False]
    )
)

print("\n==============================")
print("STEP 7-4. 핵심 상품 필터링")
print("==============================")

print("\n[최소 구매 고객 수 기준]")
print(f"최소 구매 고객 수: {min_customer_count}명")

print("\n[VIP 핵심고객 핵심 상품]")
print(
    core_products[
        core_products["Segment"] == "VIP_핵심고객"
    ]
    [
        [
            "Description",
            "CustomerCount",
            "CustomerPenetration",
            "OverallPenetration",
            "PreferenceIndex"
        ]
    ]
    .head(10)
)

# ==========================================
# STEP 7-5. 세그먼트별 핵심 상품
# ==========================================

for segment in segment_order:

    print("\n==============================")
    print(f"[{segment}] 핵심 상품 TOP 10")
    print("==============================")

    result = (
        core_products[
            core_products["Segment"] == segment
        ]
        [
            [
                "Description",
                "CustomerCount",
                "CustomerPenetration",
                "OverallPenetration",
                "PreferenceIndex"
            ]
        ]
        .head(10)
    )

    print(result)

# ==========================================
# STEP 8. 이탈위험고객 분석
# ==========================================

at_risk = (
    rfm[
        rfm["Segment"] == "이탈위험고객"
    ]
    .copy()
)

print("\n==============================")
print("STEP 8. 이탈위험고객 분석")
print("==============================")

print("\n[이탈위험고객 수]")
print(f"{len(at_risk):,}명")

print("\n[이탈위험고객 RFM 통계]")
print(
    at_risk[
        ["Recency", "Frequency", "Monetary"]
    ].describe()
)

print("\n[구매금액 상위 이탈위험고객]")
print(
    at_risk
    .sort_values(
        "Monetary",
        ascending=False
    )
    .head(10)
)

# ==========================================
# STEP 8-2. 고가치 이탈위험고객 추출
# ==========================================

monetary_q3 = (
    at_risk["Monetary"]
    .quantile(0.75)
)

high_value_at_risk = (
    at_risk[
        at_risk["Monetary"] > monetary_q3
    ]
    .copy()
)

print("\n==============================")
print("STEP 8-2. 고가치 이탈위험고객")
print("==============================")

print("\n[고가치 기준]")
print(f"Monetary Q3: {monetary_q3:,.2f}")

print("\n[고가치 이탈위험고객 수]")
print(f"{len(high_value_at_risk):,}명")

print("\n[고가치 이탈위험고객]")
print(
    high_value_at_risk
    .sort_values(
        "Monetary",
        ascending=False
    )
    .head(10)
)

# 이탈위험고객 전체 구매금액
at_risk_sales = at_risk["Monetary"].sum()

# 고가치 이탈위험고객 구매금액
high_value_sales = (
    high_value_at_risk["Monetary"].sum()
)

# 이탈위험고객 매출 중 고가치 고객 비중
high_value_sales_share = (
    high_value_sales
    / at_risk_sales
    * 100
)

print("\n[매출 기여도]")
print(f"이탈위험고객 전체 구매금액: {at_risk_sales:,.2f}")
print(f"고가치 이탈위험고객 구매금액: {high_value_sales:,.2f}")
print(
    f"고가치 이탈위험고객 매출 비중: "
    f"{high_value_sales_share:.2f}%"
)

# ==========================================
# STEP 8-3. 고가치 이탈위험고객 상품 분석
# ==========================================

# 고가치 이탈위험고객 ID
high_value_customer_ids = (
    high_value_at_risk.index
)

# 해당 고객들의 구매 데이터 추출
high_value_customer_data = (
    product_data[
        product_data["CustomerID"]
        .isin(high_value_customer_ids)
    ]
    .copy()
)

# 상품별 구매 고객 수 / 구매금액 / 구매수량
high_value_product = (
    high_value_customer_data
    .groupby("Description")
    .agg(
        CustomerCount=("CustomerID", "nunique"),
        TotalSales=("TotalPrice", "sum"),
        TotalQuantity=("Quantity", "sum")
    )
    .sort_values(
        "CustomerCount",
        ascending=False
    )
)

# 고가치 이탈위험고객 수 대비 침투율
high_value_product["CustomerPenetration"] = (
    high_value_product["CustomerCount"]
    / len(high_value_at_risk)
    * 100
)

# ==========================================
# STEP 8-4. 고가치 이탈위험 고객 수 시각화
# ==========================================

other_at_risk_count = len(at_risk) - len(high_value_at_risk)

labels = [
    "일반 이탈위험 고객",
    "고가치 이탈위험 고객"
]

values = [
    other_at_risk_count,
    len(high_value_at_risk)
]

plt.figure(figsize=(8, 6))

bars = plt.bar(labels, values)

plt.title("이탈위험 고객 내 고가치 고객 규모")
plt.xlabel("고객 유형")
plt.ylabel("고객 수")

for bar, value in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 3,
        f"{value}명",
        ha="center"
    )

plt.tight_layout()
plt.savefig("images/high_value_at_risk_customer.png", dpi=300)

# ==========================================
# STEP 8-5. 고가치 이탈위험 고객 매출 기여도
# ==========================================

other_at_risk_sales = at_risk_sales - high_value_sales

labels = [
    "고가치 이탈위험 고객",
    "기타 이탈위험 고객"
]

values = [
    high_value_sales,
    other_at_risk_sales
]

plt.figure(figsize=(8, 6))

plt.pie(
    values,
    labels=labels,
    autopct="%.2f%%",
    startangle=90
)

plt.title("이탈위험 고객의 구매금액 구성")
plt.tight_layout()

plt.savefig("images/high_value_at_risk_sales.png", dpi=300)

# ==========================================
# STEP 9. 최종 마케팅 전략 및 KPI
# ==========================================

print("\n==============================")
print("STEP 9. 최종 마케팅 전략")
print("==============================")

# ------------------------------------------
# 1. 세그먼트별 마케팅 전략
# ------------------------------------------

strategy = {
    "VIP_핵심고객":
        "고객 유지: VIP 혜택 제공 및 관련 상품 추천",

    "충성고객":
        "고객 가치 확대: 교차판매 및 추가 구매 유도",

    "잠재우수고객":
        "재구매 유도: 2차 구매 프로모션 및 관련 상품 추천",

    "이탈위험고객":
        "재활성화: 과거 구매상품 기반 리마케팅",

    "일반고객":
        "구매 활성화: 인기 상품 추천 및 저비용 CRM"
}

print("\n[세그먼트별 마케팅 전략]")

for segment in segment_order:

    print(
        f"{segment}: "
        f"{strategy[segment]}"
    )


# ------------------------------------------
# 2. 핵심 KPI
# ------------------------------------------

vip_customer_share = (
    segment_analysis.loc[
        "VIP_핵심고객",
        "CustomerShare"
    ]
)

vip_sales_share = (
    segment_analysis.loc[
        "VIP_핵심고객",
        "SalesShare"
    ]
)

high_value_at_risk_count = (
    len(high_value_at_risk)
)

high_value_at_risk_share = (
    high_value_sales_share
)

print("\n==============================")
print("핵심 KPI")
print("==============================")

print(f"전체 고객 수: {total_customers:,}명")
print(f"전체 주문 수: {total_orders:,}건")
print(f"총 구매금액: {total_sales:,.2f}")

print(
    f"VIP 핵심고객 비중: "
    f"{vip_customer_share:.2f}%"
)

print(
    f"VIP 핵심고객 매출 비중: "
    f"{vip_sales_share:.2f}%"
)

print(
    f"고가치 이탈위험고객 수: "
    f"{high_value_at_risk_count:,}명"
)

print(
    f"고가치 이탈위험고객 매출 비중: "
    f"{high_value_at_risk_share:.2f}%"
)


# ------------------------------------------
# 3. 핵심 인사이트
# ------------------------------------------

print("\n==============================")
print("핵심 인사이트")
print("==============================")

print(
    f"1. VIP 핵심고객은 전체 고객의 "
    f"{vip_customer_share:.2f}%이지만 "
    f"전체 매출의 "
    f"{vip_sales_share:.2f}%를 차지한다."
)

print(
    f"2. 잠재우수고객의 평균 Recency는 "
    f"{segment_analysis.loc['잠재우수고객', 'AvgRecency']:.2f}일이며, "
    f"평균 Frequency는 "
    f"{segment_analysis.loc['잠재우수고객', 'AvgFrequency']:.2f}회이다."
)

print(
    f"3. 이탈위험고객의 평균 Recency는 "
    f"{segment_analysis.loc['이탈위험고객', 'AvgRecency']:.2f}일이다."
)

print(
    f"4. 고가치 이탈위험고객 "
    f"{high_value_at_risk_count:,}명은 "
    f"이탈위험고객 매출의 "
    f"{high_value_at_risk_share:.2f}%를 차지한다."
)

# ==============================
# STEP 10-1. 최종 세그먼트 분석 요약
# ==============================

# 세그먼트별 고객 비중
segment_analysis["CustomerShare"] = (
    segment_analysis["CustomerCount"]
    / segment_analysis["CustomerCount"].sum()
    * 100
)

# 보기 좋은 순서로 정렬
segment_order = [
    "VIP_핵심고객",
    "충성고객",
    "잠재우수고객",
    "이탈위험고객",
    "일반고객"
]

final_segment_analysis = (
    segment_analysis
    .reindex(segment_order)
    .round(2)
)

print("\n==============================")
print("STEP 10-1. 최종 세그먼트 분석 요약")
print("==============================")

print(final_segment_analysis)

# ==============================
# STEP 10-2. 세그먼트별 마케팅 전략
# ==============================

strategy = pd.DataFrame({
    "Segment": [
        "VIP_핵심고객",
        "충성고객",
        "잠재우수고객",
        "이탈위험고객",
        "일반고객"
    ],
    
    "CustomerBehavior": [
        "최근 구매가 활발하고 구매빈도와 구매금액이 높음",
        "반복구매가 형성되어 있으며 구매가치가 높음",
        "최근 구매했지만 아직 구매빈도가 낮음",
        "장기간 구매가 없으며 과거 구매 경험이 있음",
        "구매빈도와 구매금액이 상대적으로 낮음"
    ],
    
    "MarketingGoal": [
        "고객 유지",
        "고객가치 확대",
        "재구매 유도",
        "고객 재활성화",
        "구매 활성화"
    ],
    
    "Strategy": [
        "VIP 혜택 및 신상품·연관상품 추천",
        "교차판매 및 추가 구매 유도",
        "2차 구매 프로모션 및 연관상품 추천",
        "과거 구매상품 기반 리마케팅",
        "인기상품 추천 및 저비용 CRM"
    ]
})

print("\n==============================")
print("STEP 10-2. 세그먼트별 마케팅 전략")
print("==============================")

print(strategy)

# ==========================================
# STEP 10-3. 고객 비중 vs 매출 비중
# ==========================================

comparison = segment_analysis[["CustomerShare", "SalesShare"]].copy()

# x축에 자동으로 표시되는 'Segment' 제거
comparison.index.name = None

comparison.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.title("세그먼트별 고객 비중과 매출 비중 비교")
plt.ylabel("비중 (%)")
plt.xticks(rotation=0)
plt.legend(["고객 비중", "매출 비중"])
plt.tight_layout()

plt.savefig("images/segment_customer_vs_sales.png", dpi=300)

# ==========================================
# STEP 10-4-1. RFM 기반 고객 구매행동 시각화
# ==========================================

# 고객별 구매빈도, 평균주문금액, 세그먼트 결합
rfm_plot_data = rfm[["Frequency", "Segment"]].join(
    customer_analysis[["AverageOrderValue"]]
)

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=rfm_plot_data,
    x="Frequency",
    y="AverageOrderValue",
    hue="Segment",
    alpha=0.65
)

# 값의 편차가 크므로 로그 스케일 적용
plt.xscale("log")
plt.yscale("log")

plt.title("RFM 기반 고객 구매행동 분포")
plt.xlabel("구매 빈도 (주문 수)")
plt.ylabel("평균 주문금액")
plt.legend(title="고객 세그먼트")
plt.tight_layout()

plt.savefig("images/rfm.png", dpi=300)
plt.show()
plt.close()

# ==============================
# STEP 11-1. 프로젝트 핵심 KPI
# ==============================

total_customers = normal_data["CustomerID"].nunique()
total_orders = normal_data["InvoiceNo"].nunique()
total_sales = normal_data["TotalPrice"].sum()

vip_sales_share = final_segment_analysis.loc[
    "VIP_핵심고객", "SalesShare"
]

vip_customer_share = final_segment_analysis.loc[
    "VIP_핵심고객", "CustomerShare"
]

high_value_at_risk_count = 101
high_value_at_risk_share = 64.99

print("\n==============================")
print("STEP 11-1. 프로젝트 핵심 KPI")
print("==============================")

print(f"전체 고객 수: {total_customers:,}명")
print(f"전체 주문 수: {total_orders:,}건")
print(f"총 구매금액: {total_sales:,.2f}")

print(f"\nVIP 핵심고객 비중: {vip_customer_share:.2f}%")
print(f"VIP 핵심고객 매출 비중: {vip_sales_share:.2f}%")

print(f"\n고가치 이탈위험 고객: {high_value_at_risk_count}명")
print(f"고가치 이탈위험 고객 매출 비중: {high_value_at_risk_share:.2f}%")

# ==============================
# STEP 11-2. 최종 핵심 인사이트
# ==============================

print("\n==============================")
print("STEP 11-2. 최종 핵심 인사이트")
print("==============================")

print("""
[인사이트 1]
VIP 핵심고객은 전체 고객의 22.06%이지만
전체 구매금액의 65.17%를 차지하였다.

[인사이트 2]
일반고객은 전체 고객의 38.08%로 가장 큰 고객군이지만
구매금액 비중은 9.70%로 나타났다.

[인사이트 3]
잠재우수고객은 평균 Recency가 16.43일로 최근 구매가 이루어졌지만
평균 Frequency는 1.79회로 상대적으로 낮게 나타났다.

[인사이트 4]
이탈위험고객은 평균 Recency가 163.49일로 장기간 구매가 없었다.

[인사이트 5]
이탈위험고객 403명 중 101명을 고가치 이탈위험 고객으로 분류했으며,
이들은 이탈위험 고객 전체 구매금액의 64.99%를 차지하였다.

[인사이트 6]
세그먼트별 상품 분석을 통해 고객군마다 상대적으로 높은
상품 선호도가 존재하는 것을 확인하였다.
""")
