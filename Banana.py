import streamlit as st
import google.generativeai as genai
import os
from streamlit_mic_recorder import speech_to_text
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse

# --- 1. 全局多语言字典 (新增收购商和成熟期相关翻译) ---
TRANSLATIONS = {
    "English": {
        "page_title": "🍌 Banana AI Farmer Pro",
        "sidebar_lang": "Language",
        "sidebar_api": "Google API Key",

        "champ_title": "🏆 Top Profit Hall of Fame (Hover to see details)",
        "rank_1": "🥇 2022 Champion",
        "rank_2": "🥇 2023 Champion",
        "rank_3": "🥇 2024 Champion",
        "hover_yield": "Yield:",
        "hover_price": "Avg Price:",
        "hover_reason": "Key Factor:",

        "quiz_title": "📝 Step 1: Your Environment",
        "soil_label": "Soil Type:",
        "soil_opts": {"Sandy": "Sandy (Loose)", "Loam": "Loam (Fertile)", "Clay": "Clay/Peat (Heavy)"},
        "water_label": "Water Access:",
        "water_opts": {"Low": "Low (Dry)", "Medium": "Medium", "High": "High (Rainy)"},

        "btn_calc": "🚀 Analyze & Connect Buyers",
        "rec_card_title": "Top Recommendation:",
        "rec_profit": "Est. Profit:",
        "rec_match": "Match:",
        "rec_diff": "Difficulty:",
        "rec_time": "⏳ Harvest Time:",  # New
        "buyer_title": "🤝 Verified Buyers / Wholesalers",  # New
        "buyer_call": "Call",  # New

        "chart_title": "💰 Profit Prediction (RM/Unit)",
        "globe_title": "🌍 Global Agriculture Map (Realistic Terrain)",

        "wa_btn": "📄 Send Full Report (with Buyers)",
        "report_header": "🍌 *BANANA AI FARMING REPORT*",
        "report_env": "📍 *Land Status*:",
        "report_rec": "🏆 *Recommendation*:",
        "report_time": "⏳ *Maturity*:",  # New
        "report_finance": "💰 *Financial Prediction (Per Acre)*:",
        "report_rev": "• Revenue:",
        "report_cost": "• Cost:",
        "report_prof": "• Net Profit:",
        "report_buyer": "🤝 *Recommended Buyer*:",  # New

        "voice_title": "🎙️ Voice Command / 语音控制",
        "voice_desc": "Tap the BIG button below to speak.",
        "voice_success": "Voice received: ",

        "chat_placeholder": "Type here...",
        "ai_instruction": "You are a Malaysian agricultural expert. Answer in English.",
        "warning_api": "Please enter API Key."
    },
    "中文": {
        "page_title": "🍌 Banana AI 农事通 Pro",
        "sidebar_lang": "语言 / Language",
        "sidebar_api": "Google API Key",

        "champ_title": "🏆 历年“赚钱王”风云榜 (鼠标悬停看详情)",
        "rank_1": "🥇 2022 利润冠军",
        "rank_2": "🥇 2023 利润冠军",
        "rank_3": "🥇 2024 利润冠军",
        "hover_yield": "当年产量:",
        "hover_price": "平均收购价:",
        "hover_reason": "致胜关键:",

        "quiz_title": "📝 第一步：土地环境",
        "soil_label": "土壤类型:",
        "soil_opts": {"Sandy": "沙土 (松散/透水)", "Loam": "壤土 (肥沃/一般)", "Clay": "黏土/泥炭土 (保水)"},
        "water_label": "水源情况:",
        "water_opts": {"Low": "少雨 (缺水区)", "Medium": "普通", "High": "多雨 (水源足)"},

        "btn_calc": "🚀 分析并对接收购商",
        "rec_card_title": "为您推荐首选:",
        "rec_profit": "预计净赚:",
        "rec_match": "匹配度:",
        "rec_diff": "难度:",
        "rec_time": "⏳ 成熟周期:",  # New
        "buyer_title": "🤝 认证收购商 / 批发商黄页",  # New
        "buyer_call": "拨打",  # New

        "chart_title": "💰 收益预测 (RM/亩)",
        "globe_title": "🌍 全球农业分布图 (写实地形)",

        "wa_btn": "📄 发送完整报告 (含收购商)",
        "report_header": "🍌 *Banana AI 农业评估报告*",
        "report_env": "📍 *土地状况*:",
        "report_rec": "🏆 *最佳推荐*:",
        "report_time": "⏳ *成熟期*:",  # New
        "report_finance": "💰 *财务预估 (每亩)*:",
        "report_rev": "• 预计产值:",
        "report_cost": "• 种植成本:",
        "report_prof": "• 预计净赚:",
        "report_buyer": "🤝 *推荐收购商*:",  # New

        "voice_title": "🎙️ 语音控制台",
        "voice_desc": "点击下方大按钮提问 (例如：'猫山王怎么种？')",
        "voice_success": "收到语音: ",

        "chat_placeholder": "在此打字...",
        "ai_instruction": "你是一位马来西亚农业专家。请用中文回答，结合当地气候。",
        "warning_api": "请在侧边栏输入 API Key"
    },
    "Bahasa Melayu": {
        "page_title": "🍌 Banana AI Peladang Pro",
        "sidebar_lang": "Bahasa",
        "sidebar_api": "Google API Key",

        "champ_title": "🏆 Juara Keuntungan Tahunan (Hover info)",
        "rank_1": "🥇 Juara 2022",
        "rank_2": "🥇 Juara 2023",
        "rank_3": "🥇 Juara 2024",
        "hover_yield": "Hasil:",
        "hover_price": "Harga Purata:",
        "hover_reason": "Faktor Utama:",

        "quiz_title": "📝 Langkah 1: Persekitaran",
        "soil_label": "Jenis Tanah:",
        "soil_opts": {"Sandy": "Berpasir", "Loam": "Loam", "Clay": "Liat/Gambut"},
        "water_label": "Sumber Air:",
        "water_opts": {"Low": "Kering", "Medium": "Sederhana", "High": "Hujan"},

        "btn_calc": "🚀 Analisa & Cari Pembeli",
        "rec_card_title": "Pilihan Terbaik:",
        "rec_profit": "Untung:",
        "rec_match": "Padanan:",
        "rec_diff": "Kesukaran:",
        "rec_time": "⏳ Tempoh Matang:",  # New
        "buyer_title": "🤝 Senarai Pembeli / Pemborong",  # New
        "buyer_call": "Telefon",  # New

        "chart_title": "💰 Ramalan Keuntungan (RM)",
        "globe_title": "🌍 Peta Pertanian Global (Rupa Bumi Realistik)",

        "wa_btn": "📄 Hantar Laporan (dengan Pembeli)",
        "report_header": "🍌 *Laporan Pertanian Banana AI*",
        "report_env": "📍 *Status Tanah*:",
        "report_rec": "🏆 *Cadangan Utama*:",
        "report_time": "⏳ *Tempoh Matang*:",  # New
        "report_finance": "💰 *Ramalan Kewangan (Seekar)*:",
        "report_rev": "• Hasil Kasar:",
        "report_cost": "• Kos:",
        "report_prof": "• Untung Bersih:",
        "report_buyer": "🤝 *Pembeli Disyorkan*:",  # New

        "voice_title": "🎙️ Pusat Arahan Suara",
        "voice_desc": "Tekan butang BESAR di bawah.",
        "voice_success": "Suara diterima: ",

        "chat_placeholder": "Taip sini...",
        "ai_instruction": "Anda pakar pertanian Malaysia. Jawab dalam Bahasa Melayu.",
        "warning_api": "Sila masukkan API Key."
    }
}

# --- 2. 页面配置 & CSS ---
st.set_page_config(page_title="Banana AI Farmer", page_icon="🍌", layout="wide")

st.markdown("""
    <style>
    h1 { color: #FFAE00 !important; }
    .stChatMessage { border-radius: 15px; }

    /* 冠军卡片 */
    .champion-card {
        position: relative; background: linear-gradient(to bottom right, #fffde7, #ffffff);
        border: 2px solid #FFD54F; border-radius: 15px; padding: 15px;
        text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;
        transition: transform 0.3s; height: 220px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
    }
    .champion-card:hover { transform: translateY(-5px); border-color: #FF6F00; }
    .champ-badge { background-color: #FFD700; color: #5D4037; font-weight: bold; padding: 5px 10px; border-radius: 20px; font-size: 14px; margin-bottom: 10px; }
    .champ-icon { font-size: 50px; display: block; margin: 5px 0; }
    .champ-name { font-size: 18px; font-weight: bold; color: #333; }
    .champ-data { color: #2E7D32; font-size: 22px; font-weight: 800; margin-top: 5px; background-color: rgba(232, 245, 233, 0.5); border-radius: 5px; padding: 2px 10px; }
    .champ-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.9); color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s ease; border-radius: 13px; padding: 10px; }
    .champion-card:hover .champ-overlay { opacity: 1; }
    .overlay-text { font-size: 14px; line-height: 1.6; text-align: center; width: 100%; }
    .overlay-val { color: #FFD54F; font-weight: bold; font-size: 16px; }

    /* 推荐卡片 */
    .rec-card { border: 2px solid #4CAF50; background-color: #E8F5E9; padding: 15px; border-radius: 10px; text-align: center; }

    /* 收购商卡片 (New) */
    .buyer-card {
        background-color: #fff; border: 1px solid #ddd; border-radius: 8px;
        padding: 15px; margin-bottom: 10px; display: flex; align-items: center;
        justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .buyer-info { text-align: left; }
    .buyer-name { font-weight: bold; font-size: 16px; color: #333; }
    .buyer-loc { font-size: 13px; color: #666; }
    .buyer-btn {
        background-color: #0288D1; color: white; text-decoration: none;
        padding: 8px 15px; border-radius: 20px; font-size: 13px; font-weight: bold;
    }

    /* WhatsApp & Voice */
    .wa-button { background-color: #25D366; color: white; border: none; padding: 15px 24px; border-radius: 30px; font-weight: bold; font-size: 18px; text-decoration: none; display: inline-block; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); width: 100%; text-align: center; transition: background-color 0.3s; }
    .wa-button:hover { background-color: #128C7E; }
    .voice-box-container { background-color: #f0f8ff; border: 2px dashed #4b9ce2; border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 10px; }
    div.stButton > button[kind="primary"] { height: auto !important; min-height: 60px !important; font-size: 22px !important; font-weight: bold !important; white-space: normal !important; padding: 10px 20px !important; line-height: 1.5 !important; }
    div.stButton > button:not([kind="primary"]) { width: 120px !important; height: 120px !important; border-radius: 50% !important; font-size: 60px !important; border: 5px solid #4b9ce2 !important; background-color: white !important; color: #4b9ce2 !important; margin: 0 auto !important; display: block !important; box-shadow: 0 10px 20px rgba(0,0,0,0.15) !important; transition: transform 0.1s; }
    div.stButton > button:not([kind="primary"]):active { transform: scale(0.95); background-color: #e3f2fd !important; }
    </style>
""", unsafe_allow_html=True)


# --- 3. 数据逻辑 (新增：成熟期 & 收购商数据) ---
def get_crop_database(lang):
    n = {
        "Durian": {"English": "Durian (Musang King)", "中文": "榴莲 (猫山王)", "Bahasa Melayu": "Durian (Musang King)"},
        "Palm": {"English": "Oil Palm", "中文": "油棕", "Bahasa Melayu": "Kelapa Sawit"},
        "Banana": {"English": "Banana", "中文": "香蕉", "Bahasa Melayu": "Pisang"},
        "Pineapple": {"English": "Pineapple", "中文": "菠萝/黄梨", "Bahasa Melayu": "Nanas"},
        "Corn": {"English": "Corn", "中文": "玉米", "Bahasa Melayu": "Jagung"},
        "Chili": {"English": "Chili", "中文": "辣椒", "Bahasa Melayu": "Cili"},
        "Rice": {"English": "Rice", "中文": "水稻", "Bahasa Melayu": "Padi"},
    }
    d = {
        "High": {"English": "⭐⭐⭐", "中文": "⭐⭐⭐", "Bahasa Melayu": "⭐⭐⭐"},
        "Med": {"English": "⭐⭐", "中文": "⭐⭐", "Bahasa Melayu": "⭐⭐"},
        "Low": {"English": "⭐", "中文": "⭐", "Bahasa Melayu": "⭐"}
    }
    # 定义不同作物的成熟期 (Maturity)
    m = {
        "Durian": "4-5 Years (First Harvest)",
        "Palm": "3 Years (First Harvest)",
        "Banana": "9-10 Months",
        "Pineapple": "12-14 Months",
        "Corn": "90-100 Days",
        "Chili": "60-70 Days",
        "Rice": "110 Days"
    }
    # 定义模拟收购商 (Buyers)
    b = {
        "Durian": [{"name": "Musang King Empire", "loc": "Pahang", "tel": "012-3334444"},
                   {"name": "Top Fruits Export", "loc": "Johor", "tel": "019-8887777"}],
        "Palm": [{"name": "Sime Darby Collection", "loc": "Selangor", "tel": "03-55556666"},
                 {"name": "IOI Buying Centre", "loc": "Sabah", "tel": "088-222333"}],
        "Banana": [{"name": "Pisang Borong KL", "loc": "Kuala Lumpur", "tel": "016-2221111"},
                   {"name": "Tesco Fresh Hub", "loc": "National", "tel": "1-800-888"}],
        "Pineapple": [{"name": "Nanas Johor Hub", "loc": "Pontian", "tel": "07-6868686"},
                      {"name": "Lee Pineapple Cannery", "loc": "Skudai", "tel": "07-5554444"}],
        "Corn": [{"name": "Pasar Borong Selayang", "loc": "Selangor", "tel": "013-9998888"},
                 {"name": "Cameron Vege Distributor", "loc": "Cameron", "tel": "05-4911111"}],
        "Chili": [{"name": "Baba Chili Sauce Factory", "loc": "Penang", "tel": "04-2223333"},
                  {"name": "Nestle Collection", "loc": "Shah Alam", "tel": "03-77778888"}],
        "Rice": [{"name": "Bernas Local Center", "loc": "Kedah", "tel": "04-7777777"},
                 {"name": "Jasmine Rice Mill", "loc": "Selangor", "tel": "03-33334444"}]
    }

    return {
        "Durian": {"name": n["Durian"][lang], "icon": "👑", "diff": d["High"][lang], "maturity": m["Durian"],
                   "buyers": b["Durian"], "soil_pref": ["Loam", "Clay"], "water_needs": "High", "base_yield": 100,
                   "price": 60.0, "cost": 3000},
        "Palm": {"name": n["Palm"][lang], "icon": "🌴", "diff": d["Low"][lang], "maturity": m["Palm"],
                 "buyers": b["Palm"], "soil_pref": ["Loam", "Clay"], "water_needs": "High", "base_yield": 1500,
                 "price": 1.5, "cost": 1000},
        "Chili": {"name": n["Chili"][lang], "icon": "🌶️", "diff": d["High"][lang], "maturity": m["Chili"],
                  "buyers": b["Chili"], "soil_pref": ["Loam", "Sandy"], "water_needs": "Med", "base_yield": 200,
                  "price": 18.0, "cost": 2200},
        "Pineapple": {"name": n["Pineapple"][lang], "icon": "🍍", "diff": d["Low"][lang], "maturity": m["Pineapple"],
                      "buyers": b["Pineapple"], "soil_pref": ["Sandy", "Clay"], "water_needs": "Low", "base_yield": 800,
                      "price": 3.0, "cost": 1200},
        "Banana": {"name": n["Banana"][lang], "icon": "🍌", "diff": d["Med"][lang], "maturity": m["Banana"],
                   "buyers": b["Banana"], "soil_pref": ["Loam", "Sandy"], "water_needs": "Med", "base_yield": 1000,
                   "price": 2.0, "cost": 1400},
        "Corn": {"name": n["Corn"][lang], "icon": "🌽", "diff": d["Low"][lang], "maturity": m["Corn"],
                 "buyers": b["Corn"], "soil_pref": ["Sandy", "Loam"], "water_needs": "Low", "base_yield": 800,
                 "price": 2.5, "cost": 1200},
        "Rice": {"name": n["Rice"][lang], "icon": "🌾", "diff": d["Med"][lang], "maturity": m["Rice"],
                 "buyers": b["Rice"], "soil_pref": ["Clay"], "water_needs": "High", "base_yield": 600, "price": 3.5,
                 "cost": 1500}
    }


def calculate_best_crop(user_soil_key, user_water_key, lang):
    db = get_crop_database(lang)
    results = []
    for key, data in db.items():
        score = 100
        yield_mod = 1.0
        if user_soil_key not in data["soil_pref"]: score -= 30; yield_mod *= 0.7
        if user_water_key == "Low" and data["water_needs"] == "High":
            score -= 60; yield_mod *= 0.3
        elif user_water_key == "High" and data["water_needs"] == "Low":
            score -= 20; yield_mod *= 0.8
        revenue = data["base_yield"] * yield_mod * data["price"]
        profit = revenue - data["cost"]
        results.append({
            "key": key,
            "display_name": f"{data['icon']} {data['name']}",
            "revenue": revenue, "cost": data["cost"], "profit": profit,
            "match_score": score, "difficulty": data["diff"],
            "maturity": data["maturity"],  # 传递成熟期
            "buyers": data["buyers"]  # 传递收购商列表
        })
    return pd.DataFrame(results).sort_values(by=["match_score", "profit"], ascending=False)


# --- 3D 地形图 ---
def plot_realistic_globe():
    global_crops = [
        {"name": "Corn Belt (USA)", "icon": "🌽", "lat": 41.8, "lon": -93.6},
        {"name": "Soybean (Brazil)", "icon": "🫘", "lat": -16.3, "lon": -55.0},
        {"name": "Oil Palm (Malaysia)", "icon": "🌴", "lat": 3.5, "lon": 102.0},
        {"name": "Rubber (Thailand)", "icon": "🌳", "lat": 15.0, "lon": 101.0},
        {"name": "Rice (Vietnam)", "icon": "🌾", "lat": 10.8, "lon": 106.6},
        {"name": "Coffee (Colombia)", "icon": "☕", "lat": 4.7, "lon": -75.6},
        {"name": "Bananas (Ecuador)", "icon": "🍌", "lat": -1.2, "lon": -78.5},
        {"name": "Wheat (Ukraine)", "icon": "🍞", "lat": 49.0, "lon": 32.0},
        {"name": "Cocoa (Ivory Coast)", "icon": "🍫", "lat": 7.5, "lon": -5.5},
        {"name": "Sugarcane (Australia)", "icon": "🎋", "lat": -20.3, "lon": 148.7},
    ]
    lats = [c["lat"] for c in global_crops]
    lons = [c["lon"] for c in global_crops]
    map_icons = [c["icon"] for c in global_crops]
    fig = go.Figure(data=go.Scattergeo(lon=lons, lat=lats, text=map_icons, mode='text', textfont=dict(size=20)))
    fig.update_layout(geo=dict(projection_type='orthographic', showland=True, landcolor="#C4B093", showocean=True,
                               oceancolor="#5B92E5", showcountries=True, countrycolor="#888888", countrywidth=0.5,
                               showlakes=True, lakecolor="#5B92E5", showrivers=True, rivercolor="#5B92E5",
                               resolution=50, bgcolor='rgba(0,0,0,0)',
                               projection_rotation=dict(lon=20, lat=20, roll=0)),
                      margin={"r": 0, "t": 30, "l": 0, "b": 0}, height=450, paper_bgcolor='rgba(0,0,0,0)',
                      title=dict(text="Drag to explore! / 拖动探索!", y=0.98, x=0.5, xanchor='center', yanchor='top',
                                 font=dict(size=16, color="#555")))
    return fig


# --- 4. 侧边栏 ---
with st.sidebar:
    st.image("https://em-content.zobj.net/source/microsoft-teams/337/banana_1f34c.png", width=50)
    selected_lang = st.selectbox("Language", ["English", "中文", "Bahasa Melayu"])
    t = TRANSLATIONS[selected_lang]
    st.divider()
    api_key = st.text_input(t["sidebar_api"], type="password")
    try:
        if not api_key and "GOOGLE_API_KEY" in st.secrets: api_key = st.secrets["GOOGLE_API_KEY"]
    except:
        pass

# --- 5. 主界面 ---
st.title(t["page_title"])

# 冠军榜 (悬停交互版)
st.subheader(t["champ_title"])
c1, c2, c3 = st.columns(3)
db = get_crop_database(selected_lang)

with c1:
    st.markdown(
        f"""<div class="champion-card"><div class="champ-badge">{t['rank_1']}</div><div class="champ-icon">🍍</div><div class="champ-name">{db['Pineapple']['name']}</div><div class="champ-data">RM 9,500</div><div class="champ-overlay"><div class="overlay-text">{t['hover_yield']} <span class="overlay-val">40 Ton/Ha</span></div><div class="overlay-text">{t['hover_price']} <span class="overlay-val">RM 3.8/kg</span></div><div style="margin-top:5px; border-top:1px solid #fff; width:80%; padding-top:5px;"></div><div class="overlay-text">{t['hover_reason']}<br><i>"Resilient to La Niña"</i></div></div></div>""",
        unsafe_allow_html=True)
with c2:
    st.markdown(
        f"""<div class="champion-card"><div class="champ-badge">{t['rank_2']}</div><div class="champ-icon">👑</div><div class="champ-name">{db['Durian']['name']}</div><div class="champ-data">RM 45,000</div><div class="champ-overlay"><div class="overlay-text">{t['hover_yield']} <span class="overlay-val">12 Ton/Ha</span></div><div class="overlay-text">{t['hover_price']} <span class="overlay-val">RM 55/kg</span></div><div style="margin-top:5px; border-top:1px solid #fff; width:80%; padding-top:5px;"></div><div class="overlay-text">{t['hover_reason']}<br><i>"Export Boom"</i></div></div></div>""",
        unsafe_allow_html=True)
with c3:
    st.markdown(
        f"""<div class="champion-card"><div class="champ-badge">{t['rank_3']}</div><div class="champ-icon">🌴</div><div class="champ-name">{db['Palm']['name']}</div><div class="champ-data">RM 12,000</div><div class="champ-overlay"><div class="overlay-text">{t['hover_yield']} <span class="overlay-val">22 Ton/Ha</span></div><div class="overlay-text">{t['hover_price']} <span class="overlay-val">RM 780/Ton</span></div><div style="margin-top:5px; border-top:1px solid #fff; width:80%; padding-top:5px;"></div><div class="overlay-text">{t['hover_reason']}<br><i>"Global Stability"</i></div></div></div>""",
        unsafe_allow_html=True)

st.divider()

# 问卷
st.subheader(t["quiz_title"])
col_q1, col_q2 = st.columns(2)
with col_q1: soil_disp = st.radio(t["soil_label"], ["Sandy", "Loam", "Clay"], horizontal=True)
with col_q2: water_disp = st.radio(t["water_label"], ["Low", "Medium", "High"], horizontal=True)

# 🚀 计算与结果
st.write("")
if st.button(t["btn_calc"], type="primary", use_container_width=True):
    res = calculate_best_crop(soil_disp, water_disp, selected_lang)
    top = res.iloc[0]

    # 1. 推荐概览
    st.markdown(f"""
    <div class='rec-card'>
        <h3>{t['rec_card_title']}</h3>
        <div style='font-size:30px'>{top['display_name']}</div>
        <div>{t['rec_profit']} <b>RM {top['profit']:,.0f}</b></div>
        <hr style="border-top: 1px dashed #bbb;">
        <div>{t['rec_time']} <b>{top['maturity']}</b></div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 🤝 收购商列表 (新增)
    st.write("")
    st.markdown(f"#### {t['buyer_title']}")

    for buyer in top['buyers']:
        st.markdown(f"""
        <div class="buyer-card">
            <div class="buyer-info">
                <div class="buyer-name">{buyer['name']}</div>
                <div class="buyer-loc">📍 {buyer['loc']}</div>
            </div>
            <a href="tel:{buyer['tel']}" class="buyer-btn">📞 {t['buyer_call']}</a>
        </div>
        """, unsafe_allow_html=True)

    # 3. WhatsApp 报告 (升级版：含成熟期和第一收购商)
    first_buyer = top['buyers'][0]['name']
    report_text = f"{t['report_header']}\n--------------------------\n{t['report_env']} {soil_disp} | {water_disp}\n{t['report_rec']} {top['display_name']}\n{t['report_time']} {top['maturity']}\n--------------------------\n{t['report_finance']}\n{t['report_rev']} RM {top['revenue']:,.0f}\n{t['report_cost']} RM {top['cost']:,.0f}\n{t['report_prof']} RM {top['profit']:,.0f}\n--------------------------\n{t['report_buyer']} {first_buyer}\n"
    encoded_msg = urllib.parse.quote(report_text)
    st.markdown(
        f"""<a href="https://wa.me/?text={encoded_msg}" target="_blank" style="text-decoration:none;"><div class="wa-button">{t['wa_btn']}</div></a>""",
        unsafe_allow_html=True)

    # 图表与地球
    st.write("")
    fig_bar = px.bar(res, y="display_name", x="profit", orientation='h', text="profit", color="match_score",
                     color_continuous_scale="RdYlGn")
    fig_bar.update_layout(xaxis_visible=False, yaxis_title=None, title=t["chart_title"])
    st.plotly_chart(fig_bar, use_container_width=True)
    st.divider()
    st.subheader(t["globe_title"])
    st.plotly_chart(plot_realistic_globe(), use_container_width=True)

    st.session_state.analysis_context = f"Analysis: Best crop is {top['display_name']} for {soil_disp} soil. Maturity: {top['maturity']}."

st.divider()

# --- 🎙️ 语音 ---
with st.container():
    st.markdown(
        f"""<div class="voice-box-container"><div class="voice-title">{t['voice_title']}</div><div class="voice-desc">{t['voice_desc']}</div></div>""",
        unsafe_allow_html=True)
    col_spacer1, col_btn, col_spacer2 = st.columns([1, 1, 1])
    with col_btn:
        voice_text = speech_to_text(
            language='zh-CN' if selected_lang == "中文" else ('ms-MY' if selected_lang == "Bahasa Melayu" else 'en-US'),
            start_prompt="🎤", stop_prompt="✅", just_once=True, key=f'STT_{selected_lang}')

if "messages" not in st.session_state: st.session_state.messages = []
if "analysis_context" not in st.session_state: st.session_state.analysis_context = ""
prompt = None
chat_input = st.chat_input(t["chat_placeholder"])
if voice_text:
    prompt = voice_text; st.toast(f"✅ {t['voice_success']} {voice_text}", icon="🍌")
elif chat_input:
    prompt = chat_input
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])
if api_key and prompt:
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        system_prompt = f"{t['ai_instruction']}\nContext: {st.session_state.analysis_context}\nUser: {prompt}"
        container = st.empty()
        full_resp = ""
        try:
            with st.spinner("AI thinking..."):
                resp = model.generate_content(system_prompt, stream=True)
                for chunk in resp:
                    if chunk.text: full_resp += chunk.text; container.markdown(full_resp + "▌")
            container.markdown(full_resp)
            st.session_state.messages.append({"role": "assistant", "content": full_resp})
        except Exception as e:
            st.error(f"Error: {e}")
elif prompt and not api_key:
    st.warning(t["warning_api"])