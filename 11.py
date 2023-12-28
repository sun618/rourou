import re
import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Line
from pyecharts.globals import SymbolType
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import io
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot as driver

# 获取页面内容并解析词语
def get_words(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding  # 设置编码防止乱码
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    return text

# 定义分词函数
def word_segmentation(text):
    # words = jieba.cut(text)
    # 使用jieba进行中文分词，排除标点符号和其他没有意义的中文字
    words = [word for word in jieba.lcut(text) if word.isalnum() and len(word) > 1]
    return list(words)

# 定义绘制词云函数
def draw_word_cloud(words_count):
    wc = (
        WordCloud()
        .add("", words_count, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
    )
    return wc

# 主应用
def main():
    # 页面标题
    st.title("文本分析应用")

    # 文章URL输入框
    url = st.text_input("请输入文章URL")

    # 选择图表类型
    chart_type = st.selectbox("选择图表类型", ["柱状图", "折线图","饼状图","雷达图","词云图","漏斗图"])
   
    def get_response(url):
        response = requests.get(url)
        response.encoding = response.apparent_encoding  # 设置编码防止乱码
        return response

    

    # 抓取文本内容
    words_count = Counter()  # 在此处定义空白的 words_count 变量
    if st.button("抓取文本内容"):
        response = requests.get(url)
        response.encoding = response.apparent_encoding  # 设置编码防止乱码
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        text_content = soup.get_text()
        encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
        st.text("文本内容：")
        st.text_area("内容展示", text_content, height=300)

        # 分词统计和词云绘制
        words = word_segmentation(text_content)
        words_count = Counter(words)
        word_list = [[word, count] for word, count in words_count.items()]
        wc = draw_word_cloud(word_list)
        st.text("词频排名前20：")
        
        if chart_type == "柱状图":
            st.text("词频柱状图：")
            sorted_words_count = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
            top_20_words = dict(sorted_words_count[:20])
            x_data = list(top_20_words.keys())
            y_data = list(top_20_words.values())
            plt.figure(figsize=(10, 6))
            plt.bar(x_data, y_data)
            plt.title("词频柱状图")
            plt.xlabel("词语")
            plt.ylabel("词频")
            plt.xticks(rotation=45)
            st.pyplot(plt.gcf())  # 传递当前的Matplotlib全局图形对象给st.pyplot()


        if chart_type == "折线图":
            st.text("词频折线图：")
            sorted_words_count = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
            top_20_words = dict(sorted_words_count[:20])
            x_data = list(top_20_words.keys())
            y_data = list(top_20_words.values())
            data = pd.DataFrame({"词频": y_data}, index=x_data)
            st.line_chart(data)

        if chart_type == "饼状图":
            st.text("词频饼状图：")
            sorted_words_count = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
            top_20_words = dict(sorted_words_count[:20])
            labels = list(top_20_words.keys())
            sizes = list(top_20_words.values())

            plt.figure(figsize=(10, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')  # 确保饼图是正圆形
            plt.title("词频饼状图")
            #plt.show()
            st.pyplot()


        if chart_type == "雷达图":
            st.text("词频雷达图：")
            sorted_words_count = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
            top_20_words = dict(sorted_words_count[:20])
            x_data = list(top_20_words.keys())
            y_data = list(top_20_words.values())

            labels = x_data
            values = y_data

            angles = [i / len(labels) * 2 * np.pi for i in range(len(labels))]  # 使用np.pi获取圆周率π
            values += values[:1]
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

            ax.plot(angles, values, linewidth=1, linestyle='solid')
            ax.fill(angles, values, 'b', alpha=0.1)

            ax.set_xticks(angles[:-1])

            # 设置中文标签
            font_prop = fm.FontProperties()
            ax.set_xticklabels(labels, fontproperties=font_prop)


            plt.show()
            
            # 显示雷达图
            st.pyplot(fig)


        if chart_type == "词云图":
            st.text("词云图：")
            sorted_words_count = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
            top_20_words = dict(sorted_words_count[:20])
            word_list = [[word, count] for word, count in top_20_words.items()]
            wc = draw_word_cloud(word_list)

            # 将词云图保存为图像文件
            wc.render("wordcloud.png")

            # 保存词云图文件
            plt.savefig("wordcloud.png")
            
            # 在 Streamlit 中显示词云图
            st.image("wordcloud.png")

        if chart_type == "漏斗图":
            st.text("词频漏斗图：")
            sorted_words_count = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
            top_20_words = dict(sorted_words_count[:20])
            x_data = list(top_20_words.keys())
            y_data = list(top_20_words.values())
            
            # 定义绘制漏斗图的函数
            def plot_funnel(data, figsize=(8, 6)):
                fig, ax = plt.subplots(figsize=figsize)

                ax.barh(range(len(data)), data, align='center')
                ax.set_yticks(range(len(data)))
                ax.set_yticklabels(x_data)
                ax.invert_yaxis()
                ax.set_xlabel('词频')
                ax.set_title('词频漏斗图')

            plot_funnel(y_data)
            st.pyplot()



    else:  # 默认为柱状图
            data = pd.DataFrame.from_dict(words_count.most_common(20))
            st.bar_chart(data)

if __name__ == "__main__":
    main()
