import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"

plt.rcParams["axes.unicode_minus"] = False

df = pd.read_excel("data/Online Retail.xlsx")

print(df.head())
print()
print(df.shape)
print()
print(df.columns)


print("\n[데이터 타입]")
print(df.dtypes)

print("\n[결측치]")
print(df.isnull().sum())

print("\n[중복 데이터]")
print(df.duplicated().sum())

print("\n[수치형 변수 통계]")
print(df[["Quantity", "UnitPrice"]].describe())

print("\n[취소 주문]")
print(df["InvoiceNo"].astype(str).str.startswith("C").sum())

print("\n[음수 수량]")
print((df["Quantity"] < 0).sum())

print("\n[0원 상품]")
print((df["UnitPrice"] == 0).sum())

print("\n[음수 수량 거래 예시]")
print(df[df["Quantity"] < 0].head(10))

print("\n[음수 단가 거래]")
print(df[df["UnitPrice"] < 0])

print("\n[0원 거래 예시]")
print(df[df["UnitPrice"] == 0].head(10))

print("\n[취소 주문 예시]")
print(df[df["InvoiceNo"].astype(str).str.startswith("C")].head(10))

print("\n[음수 수량 중 취소 주문 여부]")

negative_quantity = df["Quantity"] < 0
cancel_invoice = df["InvoiceNo"].astype(str).str.startswith("C")

print("음수 수량:", negative_quantity.sum())
print("취소 주문:", cancel_invoice.sum())
print("음수 수량 AND 취소 주문:", (negative_quantity & cancel_invoice).sum())
print("음수 수량 BUT 취소 주문 아님:", (negative_quantity & ~cancel_invoice).sum())

print("\n[음수 수량인데 취소 주문이 아닌 거래]")
print(
    df[negative_quantity & ~cancel_invoice][
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID", "Country"]
    ].head(20)
)

print("\n[전처리 대상 데이터 규모]")

print("전체 거래:", len(df))

print("CustomerID 결측 제외 후:",
      df["CustomerID"].notna().sum())

print("Quantity > 0:",
      (df["Quantity"] > 0).sum())

print("UnitPrice > 0:",
      (df["UnitPrice"] > 0).sum())

normal_data = df[
    (df["CustomerID"].notna()) &
    (df["Quantity"] > 0) &
    (df["UnitPrice"] > 0)
]

print("정상 구매 조건을 모두 만족하는 거래:",
      len(normal_data))

print("\n[정상 구매 데이터 통계]")
print(normal_data[["Quantity", "UnitPrice"]].describe())

print("\n[수량이 가장 큰 거래]")
print(
    normal_data.sort_values("Quantity", ascending=False)[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID", "Country"]
    ].head(10)
)

print("\n[단가가 가장 높은 거래]")
print(
    normal_data.sort_values("UnitPrice", ascending=False)[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "CustomerID", "Country"]
    ].head(10)
)

normal_data = normal_data.copy()

normal_data["TotalPrice"] = normal_data["Quantity"] * normal_data["UnitPrice"]

print("\n[거래금액이 가장 큰 거래]")
print(
    normal_data.sort_values("TotalPrice", ascending=False)[
        ["InvoiceNo", "StockCode", "Description",
         "Quantity", "UnitPrice", "TotalPrice", "CustomerID", "Country"]
    ].head(10)
)

print("\n[중복 제거]")

before = len(normal_data)

normal_data = normal_data.drop_duplicates()

after = len(normal_data)

print("중복 제거 전:", before)
print("중복 제거 후:", after)
print("제거된 중복:", before - after)

print("\n[최종 데이터 확인]")

print("행 개수:", len(normal_data))
print("열 개수:", len(normal_data.columns))

print("\n[결측치]")
print(normal_data.isnull().sum())

print("\n[데이터 타입]")
print(normal_data.dtypes)

print("\n==============================")
print("STEP 1. 전체 구매 규모")
print("==============================")

# 분석 기간
print("\n[분석 기간]")
print("시작일:", normal_data["InvoiceDate"].min())
print("종료일:", normal_data["InvoiceDate"].max())

# 고객 수
print("\n[고객 수]")
print("고객 수:", normal_data["CustomerID"].nunique())

# 주문 수
print("\n[주문 수]")
print("주문 수:", normal_data["InvoiceNo"].nunique())

# 총 매출
print("\n[총 매출]")
print("총 매출:", normal_data["TotalPrice"].sum())

# 평균 거래금액
print("\n[평균 거래금액]")
print("평균 거래금액:", normal_data["TotalPrice"].mean())

# 국가 수
print("\n[국가 수]")
print("국가 수:", normal_data["Country"].nunique())


print("\n==============================")
print("STEP 2. 월별 구매 추이")
print("==============================")

# 연-월 변수 생성
normal_data["YearMonth"] = normal_data["InvoiceDate"].dt.to_period("M")

# 월별 매출
monthly_sales = (
    normal_data
    .groupby("YearMonth")["TotalPrice"]
    .sum()
)

print("\n[월별 매출]")
print(monthly_sales)

# 월별 주문 수
monthly_orders = (
    normal_data
    .groupby("YearMonth")["InvoiceNo"]
    .nunique()
)

print("\n[월별 주문 수]")
print(monthly_orders)

# ==============================
# STEP 2-1. 월별 매출 추이
# ==============================

monthly_sales = (
    normal_data
    .groupby("YearMonth")["TotalPrice"]
    .sum()
)

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

print("\n==============================")
print("STEP 2-2. 주문당 평균 구매금액")
print("==============================")

# 주문별 구매금액 계산
order_sales = (
    normal_data
    .groupby("InvoiceNo")["TotalPrice"]
    .sum()
)

# 주문당 평균 구매금액
aov = order_sales.mean()

print("\n[주문당 평균 구매금액]")
print("AOV:", aov)

# 주문금액 기본 통계
print("\n[주문금액 통계]")
print(order_sales.describe())

print("\n==============================")
print("STEP 2-3. 고액 주문 영향")
print("==============================")

# 주문별 구매금액 기준으로 정렬
order_sales_sorted = order_sales.sort_values(ascending=False)

# 상위 10개 주문
print("\n[구매금액 상위 10개 주문]")
print(order_sales_sorted.head(10))

# 전체 매출
total_sales = order_sales.sum()

# 상위 10개 주문의 매출
top10_sales = order_sales_sorted.head(10).sum()

# 상위 10개 주문의 전체 매출 비중
top10_ratio = top10_sales / total_sales * 100

print("\n[상위 10개 주문의 매출 비중]")
print(top10_ratio, "%")

# 상위 1% 주문
top1_count = int(len(order_sales) * 0.01)

top1_sales = order_sales_sorted.head(top1_count).sum()
top1_ratio = top1_sales / total_sales * 100

print("\n[상위 1% 주문의 매출 비중]")
print(top1_ratio, "%")

print("\n==============================")
print("STEP 3. 국가별 구매 분석")
print("==============================")

# 국가별 고객 수
country_customers = (
    normal_data
    .groupby("Country")["CustomerID"]
    .nunique()
    .sort_values(ascending=False)
)

print("\n[국가별 고객 수 - 상위 10개]")
print(country_customers.head(10))

# 국가별 주문 수
country_orders = (
    normal_data
    .groupby("Country")["InvoiceNo"]
    .nunique()
    .sort_values(ascending=False)
)

print("\n[국가별 주문 수 - 상위 10개]")
print(country_orders.head(10))

# 국가별 매출
country_sales = (
    normal_data
    .groupby("Country")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
)

print("\n[국가별 매출 - 상위 10개]")
print(country_sales.head(10))

print("\n==============================")
print("STEP 3-2. 국가별 고객 1인당 매출")
print("==============================")

# 국가별 고객 수와 매출 결합
country_analysis = pd.DataFrame({
    "Customers": country_customers,
    "Sales": country_sales
})

# 고객 1명당 평균 매출
country_analysis["Sales_per_Customer"] = (
    country_analysis["Sales"] /
    country_analysis["Customers"]
)

# 매출 기준 상위 국가
print("\n[매출 상위 국가]")
print(
    country_analysis
    .sort_values("Sales", ascending=False)
    .head(10)
)

# 고객 1명당 매출 기준 상위 국가
print("\n[고객 1명당 매출 상위 국가]")
print(
    country_analysis
    .sort_values("Sales_per_Customer", ascending=False)
    .head(10)
)

print("\n==============================")
print("STEP 4. 고객별 구매행동 분석")
print("==============================")

customer_analysis = (
    normal_data
    .groupby("CustomerID")
    .agg(
        OrderCount=("InvoiceNo", "nunique"),
        TotalQuantity=("Quantity", "sum"),
        TotalSales=("TotalPrice", "sum"),
        AverageOrderValue=("TotalPrice", "sum")
    )
)

# 고객별 평균 주문금액을 다시 계산
customer_analysis["AverageOrderValue"] = (
    customer_analysis["TotalSales"] /
    customer_analysis["OrderCount"]
)

print("\n[고객별 분석 결과]")
print(customer_analysis.head())

print("\n[고객 수]")
print(len(customer_analysis))

print("\n[고객별 구매행동 통계]")
print(customer_analysis.describe())

print("\n==============================")
print("STEP 5. RFM 분석")
print("==============================")

# 분석 기준일
analysis_date = normal_data["InvoiceDate"].max()

print("\n[분석 기준일]")
print(analysis_date)

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

print("\n[RFM 데이터]")
print(rfm.head())

print("\n[RFM 통계]")
print(rfm.describe())

print("\n==============================")
print("STEP 5-2. RFM 점수화")
print("==============================")

# Recency
# 최근 구매일수록 높은 점수
rfm["R_Score"] = pd.qcut(
    rfm["Recency"],
    5,
    labels=[5, 4, 3, 2, 1]
)

# Frequency
# 구매 횟수가 많을수록 높은 점수
rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
)

# Monetary
# 구매금액이 많을수록 높은 점수
rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
)

# 숫자형으로 변환
rfm["R_Score"] = rfm["R_Score"].astype(int)
rfm["F_Score"] = rfm["F_Score"].astype(int)
rfm["M_Score"] = rfm["M_Score"].astype(int)

# RFM 총점
rfm["RFM_Score"] = (
    rfm["R_Score"] +
    rfm["F_Score"] +
    rfm["M_Score"]
)

print("\n[RFM 점수 결과]")
print(rfm.head(10))

print("\n[RFM 점수 통계]")
print(rfm[["R_Score", "F_Score", "M_Score", "RFM_Score"]].describe())

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


# ==============================
# STEP 6-3-1. 세그먼트별 고객 수
# ==============================

plt.figure(figsize=(10, 5))

plt.bar(
    plot_data.index,
    plot_data["CustomerCount"]
)

plt.title("세그먼트별 고객 수")
plt.xlabel("세그먼트")
plt.ylabel("고객 수")

plt.xticks(rotation=20)
plt.tight_layout()


# ==============================
# STEP 6-3-2. 세그먼트별 매출 비중
# ==============================

plt.figure(figsize=(10, 5))

plt.bar(
    plot_data.index,
    plot_data["SalesShare"]
)

plt.title("세그먼트별 매출 비중")
plt.xlabel("세그먼트")
plt.ylabel("매출 비중 (%)")

plt.xticks(rotation=20)
plt.tight_layout()



# ==============================
# STEP 6-4-1. 세그먼트별 Recency
# ==============================

plt.figure(figsize=(10, 5))

plt.bar(
    plot_data.index,
    plot_data["AvgRecency"]
)

plt.title("세그먼트별 평균 최근 구매일")
plt.xlabel("세그먼트")
plt.ylabel("평균 최근 구매일 (일)")

plt.xticks(rotation=20)
plt.tight_layout()

# ==============================
# STEP 6-4-2. 세그먼트별 Frequency
# ==============================

plt.figure(figsize=(10, 5))

plt.bar(
    plot_data.index,
    plot_data["AvgFrequency"]
)

plt.title("세그먼트별 평균 구매 빈도")
plt.xlabel("세그먼트")
plt.ylabel("평균 구매 횟수")

plt.xticks(rotation=20)
plt.tight_layout()

# ==============================
# STEP 6-4-3. 세그먼트별 Monetary
# ==============================

plt.figure(figsize=(10, 5))

plt.bar(
    plot_data.index,
    plot_data["AvgMonetary"]
)

plt.title("세그먼트별 평균 구매금액")
plt.xlabel("세그먼트")
plt.ylabel("평균 구매금액")

plt.xticks(rotation=20)
plt.tight_layout()


# ==============================
# STEP 6-5. 세그먼트별 평균 vs 중앙값
# ==============================

segment_median = (
    rfm
    .groupby("Segment")
    .agg(
        MedianRecency=("Recency", "median"),
        MedianFrequency=("Frequency", "median"),
        MedianMonetary=("Monetary", "median")
    )
)

segment_median = segment_median.reindex(segment_order)

print("\n==============================")
print("STEP 6-5. 세그먼트별 중앙값")
print("==============================")

print(segment_median)

# ==============================
# STEP 7-1-1. 거래 데이터에 세그먼트 정보 추가
# ==============================

normal_data["Segment"] = normal_data["CustomerID"].map(
    rfm["Segment"]
)

print("\n==============================")
print("STEP 7-1-1. 세그먼트 정보 확인")
print("==============================")

print(normal_data[[
    "CustomerID",
    "InvoiceNo",
    "Description",
    "Quantity",
    "TotalPrice",
    "Segment"
]].head(10))

print("\n[세그먼트 결측치]")
print(normal_data["Segment"].isnull().sum())

# ==============================
# STEP 7-1-2. 세그먼트별 인기 상품
# ==============================

segment_product_sales = (
    normal_data
    .groupby(["Segment", "Description"])
    .agg(
        Sales=("TotalPrice", "sum"),
        Quantity=("Quantity", "sum"),
        CustomerCount=("CustomerID", "nunique")
    )
    .reset_index()
)

print("\n==============================")
print("STEP 7-1-2. 세그먼트별 인기 상품")
print("==============================")

for segment in segment_order:

    print(f"\n[{segment}]")

    temp = (
        segment_product_sales[
            segment_product_sales["Segment"] == segment
        ]
        .sort_values("Sales", ascending=False)
        .head(10)
    )

    print(
        temp[
            ["Description", "Sales", "Quantity", "CustomerCount"]
        ]
    )

# ==============================
# STEP 7-2. 세그먼트별 상품 고객 침투율
# ==============================

segment_customer_count = (
    rfm["Segment"]
    .value_counts()
)

segment_product = (
    normal_data
    .groupby(["Segment", "Description"])
    .agg(
        CustomerCount=("CustomerID", "nunique"),
        Sales=("TotalPrice", "sum"),
        Quantity=("Quantity", "sum")
    )
    .reset_index()
)

# 세그먼트 전체 고객 수
segment_product["SegmentCustomerCount"] = (
    segment_product["Segment"]
    .map(segment_customer_count)
)

# 상품 고객 침투율
segment_product["CustomerPenetration"] = (
    segment_product["CustomerCount"]
    / segment_product["SegmentCustomerCount"]
    * 100
)

print("\n==============================")
print("STEP 7-2. 세그먼트별 상품 고객 침투율")
print("==============================")

for segment in segment_order:

    print(f"\n[{segment}]")

    temp = (
        segment_product[
            segment_product["Segment"] == segment
        ]
        .sort_values(
            "CustomerPenetration",
            ascending=False
        )
        .head(10)
    )

    print(
        temp[
            [
                "Description",
                "CustomerCount",
                "CustomerPenetration",
                "Sales",
                "Quantity"
            ]
        ]
    )

# ==============================
# STEP 7-3. 상품 분석용 데이터 정리
# ==============================

product_data = normal_data[
    ~normal_data["Description"].isin([
        "POSTAGE",
        "Manual"
    ])
].copy()

print("\n==============================")
print("STEP 7-3. 상품 분석용 데이터")
print("==============================")

print("전체 거래 건수:", len(normal_data))
print("상품 분석 거래 건수:", len(product_data))

print("\n[제외된 거래]")
print(len(normal_data) - len(product_data))


# ==============================
# STEP 7-3-2. 세그먼트별 상품 침투율
# ==============================

# 세그먼트별 전체 고객 수
segment_customer_count = rfm["Segment"].value_counts()

# 세그먼트 × 상품별 구매 고객 수
product_penetration = (
    product_data
    .groupby(["Segment", "Description"])["CustomerID"]
    .nunique()
    .reset_index(name="CustomerCount")
)

# 해당 세그먼트의 전체 고객 수
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
print("STEP 7-3-2. 세그먼트별 상품 침투율")
print("==============================")

for segment in segment_order:

    print(f"\n[{segment}]")

    temp = (
        product_penetration[
            product_penetration["Segment"] == segment
        ]
        .sort_values(
            "CustomerPenetration",
            ascending=False
        )
        .head(10)
    )

    print(
        temp[
            [
                "Description",
                "CustomerCount",
                "CustomerPenetration"
            ]
        ]
    )

# ==============================
# STEP 7-4. 세그먼트별 상품 선호도 지수
# ==============================

# 전체 고객 수
total_customer_count = rfm.index.nunique()

# 전체 상품별 구매 고객 수
overall_product = (
    product_data
    .groupby("Description")["CustomerID"]
    .nunique()
    .reset_index(name="OverallCustomerCount")
)

# 전체 고객 대비 상품 침투율
overall_product["OverallPenetration"] = (
    overall_product["OverallCustomerCount"]
    / total_customer_count
    * 100
)

# 세그먼트별 상품 침투율에 전체 상품 침투율 결합
product_preference = product_penetration.merge(
    overall_product,
    on="Description",
    how="left"
)

# 선호도 지수 계산
product_preference["PreferenceIndex"] = (
    product_preference["CustomerPenetration"]
    / product_preference["OverallPenetration"]
)

print("\n==============================")
print("STEP 7-4. 세그먼트별 상품 선호도 지수")
print("==============================")

for segment in segment_order:

    print(f"\n[{segment}]")

    temp = (
        product_preference[
            (product_preference["Segment"] == segment) &
            (product_preference["CustomerCount"] >= 10)
        ]
        .sort_values(
            "PreferenceIndex",
            ascending=False
        )
        .head(10)
    )

    print(
        temp[
            [
                "Description",
                "CustomerCount",
                "CustomerPenetration",
                "OverallPenetration",
                "PreferenceIndex"
            ]
        ]
    )

# ==============================
# STEP 7-5. 세그먼트별 핵심 상품
# ==============================

print("\n==============================")
print("STEP 7-5. 세그먼트별 핵심 상품")
print("==============================")

for segment in segment_order:

    print(f"\n[{segment}]")

    temp = (
        product_preference[
            (product_preference["Segment"] == segment) &
            (product_preference["CustomerCount"] >= 30) &
            (product_preference["PreferenceIndex"] >= 1.5)
        ]
        .sort_values(
            "PreferenceIndex",
            ascending=False
        )
        .head(10)
    )

    print(
        temp[
            [
                "Description",
                "CustomerCount",
                "CustomerPenetration",
                "OverallPenetration",
                "PreferenceIndex"
            ]
        ]
    )

# ==============================
# STEP 8-1. 고객 구매행동 시각화
# ==============================

import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 고객 분석 데이터에 세그먼트 추가
customer_plot = rfm.copy()

# 고객별 평균 주문금액 계산
customer_plot["AverageOrderValue"] = (
    customer_plot["Monetary"] /
    customer_plot["Frequency"]
)

print("\n==============================")
print("STEP 8-1. 고객 구매행동")
print("==============================")

print(customer_plot.head())

# ==============================
# STEP 8-2. 구매 빈도와 평균 주문금액
# ==============================

plt.figure(figsize=(10, 7))

for segment in segment_order:

    temp = customer_plot[
        customer_plot["Segment"] == segment
    ]

    plt.scatter(
        temp["Frequency"],
        temp["AverageOrderValue"],
        label=segment,
        alpha=0.6
    )

plt.xlabel("구매 횟수")
plt.ylabel("평균 주문금액")
plt.title("세그먼트별 구매 빈도와 평균 주문금액")
plt.legend()
plt.grid(alpha=0.3)

# ==============================
# STEP 8-2-1. 로그 스케일 고객 구매행동
# ==============================

plt.figure(figsize=(10, 7))

for segment in segment_order:

    temp = customer_plot[
        customer_plot["Segment"] == segment
    ]

    plt.scatter(
        temp["Frequency"],
        temp["AverageOrderValue"],
        label=segment,
        alpha=0.6
    )

# 로그 스케일 적용
plt.xscale("log")
plt.yscale("log")

plt.xlabel("구매 횟수 (로그 스케일)")
plt.ylabel("평균 주문금액 (로그 스케일)")
plt.title("세그먼트별 구매 빈도와 평균 주문금액")
plt.legend()
plt.grid(alpha=0.3)

plt.savefig(
    "images/rfm.png",
    dpi=300
)


# ==============================
# STEP 8-3. 이탈위험고객 가치 분석
# ==============================

at_risk_customers = (
    rfm[
        rfm["Segment"] == "이탈위험고객"
    ]
    .sort_values(
        "Monetary",
        ascending=False
    )
)

print("\n==============================")
print("STEP 8-3. 이탈위험고객 가치 분석")
print("==============================")

print(
    at_risk_customers[
        [
            "Recency",
            "Frequency",
            "Monetary",
            "RFM_Score"
        ]
    ].head(20)
)

# ==============================
# STEP 8-4. 고가치 이탈위험 고객
# ==============================

# 이탈위험고객의 Monetary 75% 분위수
at_risk_q3 = at_risk_customers["Monetary"].quantile(0.75)

# 고가치 이탈위험 고객
high_value_at_risk = at_risk_customers[
    at_risk_customers["Monetary"] >= at_risk_q3
]

print("\n==============================")
print("STEP 8-4. 고가치 이탈위험 고객")
print("==============================")

print("이탈위험고객 수:", len(at_risk_customers))
print("Monetary Q3:", round(at_risk_q3, 2))
print("고가치 이탈위험 고객 수:", len(high_value_at_risk))

print("\n[고가치 이탈위험 고객]")
print(
    high_value_at_risk[
        [
            "Recency",
            "Frequency",
            "Monetary",
            "RFM_Score"
        ]
    ].head(20)
)

# 고가치 이탈위험 고객의 매출 기여도
high_value_sales = high_value_at_risk["Monetary"].sum()
at_risk_sales = at_risk_customers["Monetary"].sum()

high_value_sales_share = (
    high_value_sales
    / at_risk_sales
    * 100
)

print("\n[매출 기여도]")
print("이탈위험고객 전체 구매금액:", round(at_risk_sales, 2))
print("고가치 이탈위험 고객 구매금액:", round(high_value_sales, 2))
print(
    "고가치 이탈위험 고객의 매출 비중:",
    round(high_value_sales_share, 2),
    "%"
)


# ==============================
# STEP 8-5. 고가치 이탈위험 고객 상품 분석
# ==============================

# 고가치 이탈위험 고객 ID
high_value_customer_ids = high_value_at_risk.index

# 해당 고객들의 구매 데이터
high_value_product_data = product_data[
    product_data["CustomerID"].isin(high_value_customer_ids)
].copy()

# 상품별 구매 고객 수
high_value_product = (
    high_value_product_data
    .groupby("Description")
    .agg(
        CustomerCount=("CustomerID", "nunique"),
        Sales=("TotalPrice", "sum"),
        Quantity=("Quantity", "sum")
    )
    .reset_index()
)

# 고가치 이탈위험 고객 수
high_value_customer_count = len(high_value_customer_ids)

# 상품 침투율
high_value_product["CustomerPenetration"] = (
    high_value_product["CustomerCount"]
    / high_value_customer_count
    * 100
)

print("\n==============================")
print("STEP 8-5. 고가치 이탈위험 고객 상품 분석")
print("==============================")

print(
    high_value_product
    .sort_values(
        "CustomerPenetration",
        ascending=False
    )
    .head(20)
)


# ==============================
# STEP 9-1. 고가치 이탈위험 고객 분석 시각화
# ==============================

plt.figure(figsize=(8, 6))

labels = [
    "일반 이탈위험 고객",
    "고가치 이탈위험 고객"
]

values = [
    len(at_risk_customers) - len(high_value_at_risk),
    len(high_value_at_risk)
]

bars = plt.bar(labels, values)

plt.ylabel("고객 수")
plt.title("이탈위험 고객 내 고가치 고객 규모")

for bar, value in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 5,
        f"{value}명",
        ha="center"
    )

plt.savefig(
    "images/high_value_at_risk_customer",
    dpi=300
)


# ==============================
# STEP 9-1-2. 고가치 이탈위험 고객 매출 기여도
# ==============================

plt.figure(figsize=(7, 7))

labels = [
    "고가치 이탈위험 고객",
    "기타 이탈위험 고객"
]

values = [
    high_value_sales,
    at_risk_sales - high_value_sales
]

plt.pie(
    values,
    labels=labels,
    autopct="%.1f%%",
    startangle=90
)

plt.title("이탈위험 고객의 구매금액 구성")

plt.savefig(
    "images/high_value_at_risk_sales.png",
    dpi=300
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
# STEP 10-1-1. 고객 비중 vs 매출 비중
# ==============================

plt.figure(figsize=(10, 6))

x = range(len(final_segment_analysis))

plt.bar(
    [i - 0.2 for i in x],
    final_segment_analysis["CustomerShare"],
    width=0.4,
    label="고객 비중"
)

plt.bar(
    [i + 0.2 for i in x],
    final_segment_analysis["SalesShare"],
    width=0.4,
    label="매출 비중"
)

plt.xticks(
    x,
    final_segment_analysis.index
)

plt.ylabel("비중 (%)")
plt.title("세그먼트별 고객 비중과 매출 비중")
plt.legend()

plt.savefig(
    "images/segment_share.png",
    dpi=300
)

plt.show()


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

# ==============================
# STEP 10-3. 고가치 이탈위험 고객 전략
# ==============================

high_value_strategy = pd.DataFrame({
    "Target": [
        "고가치 이탈위험 고객"
    ],
    
    "CustomerCount": [
        len(high_value_at_risk)
    ],
    
    "SalesShare": [
        high_value_sales_share
    ],
    
    "MarketingGoal": [
        "고객 재활성화"
    ],
    
    "Strategy": [
        "과거 구매상품을 활용한 개인화 재활성화 캠페인"
    ]
})

print("\n==============================")
print("STEP 10-3. 고가치 이탈위험 고객 전략")
print("==============================")

print(high_value_strategy.round(2))


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
