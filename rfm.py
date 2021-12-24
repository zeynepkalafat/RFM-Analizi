# RFM ANALİZİ İLE MÜŞTERİ SEGMENTASYONU

import pandas as pd
import datetime as dt

df = pd.read_excel("datasets\online_retail_II.xlsx", sheet_name="Year 2010-2011")

# Veri setinin betimsel istatistikleri

df.describe().T

''' 
                   count        mean        std          min         25%         50%         75%         max
Quantity    541910.00000     9.55223  218.08096 -80995.00000     1.00000     3.00000    10.00000 80995.00000
Price       541910.00000     4.61114   96.75977 -11062.06000     1.25000     2.08000     4.13000 38970.00000
Customer ID 406830.00000 15287.68416 1713.60307  12346.00000 13953.00000 15152.00000 16791.00000 18287.00000
'''

# Veri setindeki eksik değerleri gözlemlemek

df.isnull().values.any()
df.isnull().sum()

'''
Invoice             0
StockCode           0
Description      1454
Quantity            0
InvoiceDate         0
Price               0
Customer ID    135080
Country             0

'''

# Eksik gözlemlerin veri setinden çıkartılması

df.dropna(inplace=True)
df.isnull().sum()

'''
Invoice        0
StockCode      0
Description    0
Quantity       0
InvoiceDate    0
Price          0
Customer ID    0
Country        0
'''

# Eşsiz ürün sayısı kaçtır?
# Hangi üründen kaçar tane vardır?

df["Description"].nunique()
df["Description"].value_counts()


# En çok sipariş edilen 5 ürünün çoktan aza sıralanması

df[["Quantity","Description"]].groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity",ascending=False).head()

'''
                                    Quantity
Description                                 
WORLD WAR 2 GLIDERS ASSTD DESIGNS      53215
JUMBO BAG RED RETROSPOT                45066
ASSORTED COLOUR BIRD ORNAMENT          35314
WHITE HANGING HEART T-LIGHT HOLDER     34147
PACK OF 72 RETROSPOT CAKE CASES        33409
'''


# Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir.
# İptal edilen işlemleri veri setinden çıkartılması

df = df[~df["Invoice"].str.contains('C',na=False)]

# Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturulması

df["TotalPrice"] = df["Quantity"] * df["Price"]


# RFM metriklerinin hesaplanması

# Müşteri özelinde Recency, Frequency ve Monetary metriklerinin hesaplanması

df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})


rfm.columns = ['recency', 'frequency', 'monetary']

rfm = rfm[rfm['monetary']>0]

# RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi

# Recency
rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

# Frequency
rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# Monetary
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

# RFM skorlarının segment olarak tanımlanması

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

# Segmentleri gözlemlemek

rfm[["segment", "recency", "frequency", "monetary"]].groupby('segment').agg({"mean","count"})

'''
                        recency        frequency           monetary      
                           mean count       mean count         mean count
segment                                                                  
about_to_sleep        52.250000   360   1.300000   360   439.892778   360
at_Risk              155.695868   605   3.348760   605   969.751904   605
cant_loose           132.300000    70   9.771429    70  2383.257714    70
champions              6.088012   659  14.687405   659  6552.265372   659
hibernating          213.615236  1037   1.209257  1037   399.946703  1037
loyal_customers       32.701031   776   8.068299   776  2732.938455   776
need_attention        49.196629   178   2.674157   178   821.471966   178
new_customers          7.238095    42   1.000000    42   377.234286    42
potential_loyalists   16.484909   497   2.253521   497   717.330785   497
promising             23.187500    96   1.000000    96   306.213646    96

'''

# "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısının alınması

new_df = pd.DataFrame()
new_df["loyal_customers_id"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.to_csv("loyal_customers.csv")

