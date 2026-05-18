import pandas as pd

df = pd.read_excel("tum_istasyonlar_temiz.xlsx")
print(
    df.groupby("Kaynak Dosya")["İstasyon No"]
    .count()
    .sort_values(ascending=False)
    .to_string()
)
