import requests
import pandas as pd
import json
import datetime

import baostock as bs
import pandas as pd

def fetch_and_save_stock_data(
    stock_code: str,
    start_date: str,
    end_date: str,
    frequency: str = "d",
    adjustflag: str = "3",
    save_path: str = None
):
    """
    使用 Baostock 拉取指定股票历史行情并保存为 CSV 文件。

    参数:
    - stock_code: 股票代码（如 "sh.600519"）
    - start_date: 起始日期（"YYYY-MM-DD"）
    - end_date: 截止日期（"YYYY-MM-DD"）
    - frequency: k线周期，"d"=日，"w"=周，"m"=月（默认日线）
    - adjustflag: 复权方式，"3"=不复权，"2"=前复权，"1"=后复权
    - save_path: 保存路径（默认当前目录下以代码命名）

    返回:
    - pd.DataFrame 格式的行情数据
    """

    # 登录
    lg = bs.login()
    if lg.error_code != '0':
        print(f"登录失败: {lg.error_msg}")
        return None

    # 拉取数据
    fields = (
        "date,code,open,high,low,close,volume,amount,adjustflag,"
        "turn,peTTM,pbMRQ,psTTM,pctChg"
    )
    rs = bs.query_history_k_data_plus(
        stock_code,
        fields,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        adjustflag=adjustflag
    )

    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)

    # 保存
    if save_path is None:
        code_short = stock_code.replace(".", "")
        save_path = f"{code_short}_{start_date}_to_{end_date}.csv"
    df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"数据已保存到：{save_path}")

    bs.logout()
    return df


#年度报告
#我们需要agent 具备查询股票代码，以及搜集年报的功能
# 1. 通过agent的代码，获取股票代码
# 2. 通过股票代码，获取年报
# 3. 通过年报，获取年报的pdf链接
# 4. 通过pdf链接，获取年报的pdf文件
# 5. 通过年报的pdf文件，保存到本地

def fetch_cninfo(code: str, keyword: str = "年报", page: int = 1):
    url = "https://www.cninfo.com.cn/new/fulltextSearch/full"
    params = {
        "searchkey": f"{code} {keyword}",
        "pageNum": page,
        "pageSize": 40
    }
    headers = {
        "Referer": "https://www.cninfo.com.cn",
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, params=params, headers=headers, timeout=10).json()
    return pd.DataFrame(res["announcements"])

df = fetch_cninfo("600519")
# pdf_url = "https://static.cninfo.com.cn/" + df.iloc[0]["adjunctUrl"]
# 拼接完整 URL 列
df["pdf_url"] = "https://static.cninfo.com.cn/" + df["adjunctUrl"]

# 选取需要保存的字段
save_df = df[["announcementTitle", "announcementTime", "pdf_url"]]

# 保存为 CSV
save_df.to_csv("announcements.csv", index=False, encoding="utf-8-sig")
df = fetch_and_save_stock_data(
    stock_code="sh.600519",
    start_date="2020-01-01",
    end_date="2024-12-31",
    frequency="d",
    adjustflag="2",  # 前复权
    save_path="moutai_daily_qfq.csv"
)

