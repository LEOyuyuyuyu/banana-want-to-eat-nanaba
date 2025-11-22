import streamlit as st
import google.generativeai as genai
import os
from streamlit_mic_recorder import speech_to_text
import pandas as pd
import plotly.express as px
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim
import time
import random
from datetime import datetime, timedelta

# --- 1. 配置与页面设置 ---
st.set_page_config(page_title="Banana AI Sabah", page_icon="🍌", layout="wide")

# --- 多语言字典 (含离线模式文案) ---
TRANSLATIONS = {
    "English": {
        "title": "🍌 Banana AI (Sabah Edition)",
        "tab_1": "🏆 Market & Weather",
        "tab_2": "📍 Smart Analysis",
        "tab_3": "🛠️ Tools",
        "top_5_title": "🏆 Top 5 Champions (Sabah)",
        "tools_title": "🛠️ Farm Utilities",
        "t1": "🧮 Profit Calc", "t2": "🦠 Disease Scan", "t3": "🚛 Find Lorry",
        "weather_title": "🌦️ Sabah Weather",
        "tips_scroll_title": "📢 Daily Planting Tips (Scrolling)",
        "step_loc": "Step 1: Find Your Farm",
        "btn_voice": "🎙️ Voice", "btn_cam": "📸 Soil Photo", "btn_gps": "📍 GPS Locate",
        "addr_found": "📍 Your Farm:",
        "map_title": "🗺️ Your Location",
        "res_title": "🌱 Best Recommendation",
        "res_tips_title": "💡 Expert Planting Tips",
        "res_profit": "Net Profit / Acre / Year",
        "buyers": "🤝 Buyer Contact",
        "chat_header": "🤖 AI Assistant (Voice & Chat)",
        "chat_hint_market": "Ask about Durian prices...",
        "chat_hint_soil": "How to fertilize sandy soil...",
        "chat_hint_tools": "How to calculate cost...",
        "mic_start": "🎤 Speak", "mic_stop": "🛑 Stop",
        "offline_mode": "🔌 Offline Mode",
        "offline_warn": "⚠️ Offline Mode Active: AI & Maps Disabled. Using local data.",
        "ai_offline_msg": "🔌 I am offline. I cannot use Gemini AI, but I can record your notes.",
        "loc_offline": "Offline Coords:",
        "map_offline": "🚫 Map unavailable offline."
    },
    "中文": {
        "title": "🍌 Banana AI 农事通 (沙巴卡通版)",
        "tab_1": "🏆 冠军榜 & 天气",
        "tab_2": "📍 智能选种",
        "tab_3": "🛠️ 工具箱",
        "top_5_title": "🏆 去年利润前五名 (沙巴)",
        "tools_title": "🛠️ 实用工具箱",
        "t1": "🧮 利润计算器", "t2": "🦠 拍叶子看病", "t3": "🚛 找罗里/运输",
        "weather_title": "🌦️ 沙巴未来7天天气",
        "tips_scroll_title": "📢 每日种植小贴士 (滚动播放)",
        "step_loc": "第一步：确认农地位置",
        "btn_voice": "🎙️ 语音输入", "btn_cam": "📸 拍泥土", "btn_gps": "📍 自动定位 (GPS)",
        "addr_found": "📍 您的农地位置:",
        "map_title": "🗺️ 您的坐标 (沙巴地图)",
        "res_title": "🌱 最佳推荐",
        "res_tips_title": "💡 专家种植建议",
        "res_profit": "预计年净赚 (每英亩)",
        "buyers": "🤝 沙巴收购商 (点击拨打)",
        "chat_header": "🤖 智能助手 (支持语音)",
        "chat_hint_market": "问问现在榴莲多少钱...",
        "chat_hint_soil": "沙地要放什么肥...",
        "chat_hint_tools": "怎么算利润...",
        "mic_start": "🎤 点击说话", "mic_stop": "🛑 停止",
        "offline_mode": "🔌 离线模式 (无网专用)",
        "offline_warn": "⚠️ 离线模式已开启：AI和地图已禁用，使用本地数据。",
        "ai_offline_msg": "🔌 我现在离线，无法连接大脑。但我可以记录您的笔记。",
        "loc_offline": "离线坐标:",
        "map_offline": "🚫 离线无法加载地图。"
    },
    "Bahasa Melayu": {
        "title": "🍌 Banana AI (Sabah Kartun)",
        "tab_1": "🏆 Juara & Cuaca",
        "tab_2": "📍 Analisa Pintar",
        "tab_3": "🛠️ Alatan",
        "top_5_title": "🏆 5 Juara Untung (Sabah)",
        "tools_title": "🛠️ Alatan Kebun",
        "t1": "🧮 Kira Untung", "t2": "🦠 Scan Penyakit", "t3": "🚛 Cari Lori",
        "weather_title": "🌦️ Cuaca Sabah",
        "tips_scroll_title": "📢 Tips Tanaman Harian",
        "step_loc": "Langkah 1: Cari Kebun",
        "btn_voice": "🎙️ Suara", "btn_cam": "📸 Foto", "btn_gps": "📍 GPS Auto",
        "addr_found": "📍 Lokasi Kebun:",
        "map_title": "🗺️ Lokasi Anda",
        "res_title": "🌱 Pilihan Terbaik",
        "res_tips_title": "💡 Tips Pakar",
        "res_profit": "Untung Bersih / Ekar / Tahun",
        "buyers": "🤝 Pembeli Sabah",
        "chat_header": "🤖 Pembantu AI (Suara)",
        "chat_hint_market": "Tanya harga Durian...",
        "chat_hint_soil": "Baja apa untuk tanah pasir...",
        "chat_hint_tools": "Macam mana kira untung...",
        "mic_start": "🎤 Cakap", "mic_stop": "🛑 Berhenti",
        "offline_mode": "🔌 Mod Offline",
        "offline_warn": "⚠️ Mod Offline Aktif: AI & Peta dipadamkan.",
        "ai_offline_msg": "🔌 Saya offline. Tak dapat guna AI, tapi saya boleh catat nota.",
        "loc_offline": "Koordinat Offline:",
        "map_offline": "🚫 Peta tak dapat buka offline."
    }
}

# --- 2. CSS (样式优化) ---
st.markdown("""
    <style>
    html, body, p, label { font-size: 18px !important; font-family: sans-serif; }

    .champ-card {
        background: #FFFDE7; border: 3px solid #FBC02D; border-radius: 20px;
        padding: 10px; text-align: center; height: 340px;
        display: flex; flex-direction: column; justify-content: flex-start; align-items: center;
        box-shadow: 0 5px 10px rgba(0,0,0,0.1);
    }
    .champ-rank { background: #FF6F00; color: white; padding: 5px 15px; border-radius: 20px; font-weight:bold; margin-bottom:5px;}

    /* 图片与Emoji样式 */
    .cartoon-img { width: 90px; height: 90px; object-fit: contain; margin: 5px 0; transition: transform 0.2s;}
    .champ-card:hover .cartoon-img { transform: scale(1.1); }
    .offline-emoji { font-size: 70px; margin: 10px 0; }

    .champ-profit { color: #D32F2F; font-weight: 900; font-size: 22px; margin-top: 5px; }

    .chat-section {
        background-color: #f0f2f6; border-radius: 15px; padding: 15px; margin-top: 20px; border: 2px dashed #888; text-align: center;
    }
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #E8F5E9; padding: 10px; border-radius: 10px; margin-top: 10px; border: 2px solid #4CAF50;
    }
    .ticker-text { font-size: 20px; color: #1B5E20; font-weight: bold; }
    div.stButton > button { width: 100%; border-radius: 15px; height: 70px; font-size: 20px; font-weight:bold; }
    </style>
""", unsafe_allow_html=True)


# --- 3. 数据逻辑 (含离线处理) ---

def get_top_5(lang, is_offline):
    # 多语言 Tips
    if lang == "中文":
        tips_durian = ["一定要做好排水，怕积水", "前三年要多施氮肥", "注意防蛀虫"]
        tips_chili = ["不要种在低洼地", "每两周喷一次叶面肥", "主要防炭疽病"]
        tips_banana = ["每棵保留一母一子", "由于巴拿马病，尽量轮作", "老叶要及时修剪"]
        tips_palm = ["主要是施肥要有规律", "一定要清理老叶", "注意老鼠吃果"]
        tips_pine = ["非常适合沙质土壤", "催花需要乙烯利", "不需要太多水"]
    elif lang == "Bahasa Melayu":
        tips_durian = ["Pastikan saliran baik", "Banyakkan Nitrogen (N)", "Jaga-jaga ulat"]
        tips_chili = ["Elakkan tanah rendah", "Sembur baja daun", "Cegah Antraknos"]
        tips_banana = ["Simpan 1 pokok ibu 1 anak", "Giliran tanaman", "Cantantas daun tua"]
        tips_palm = ["Baja kena teratur", "Cantantas pelepah", "Kawal tikus"]
        tips_pine = ["Sesuai tanah pasir", "Guna Ethephon", "Tahan kering"]
    else:
        tips_durian = ["Good drainage needed", "More Nitrogen (N)", "Watch out for borers"]
        tips_chili = ["Avoid low land", "Foliar fertilizer", "Prevent Anthracnose"]
        tips_banana = ["Keep 1 mother 1 sucker", "Crop rotation", "Prune old leaves"]
        tips_palm = ["Regular fertilization", "Pruning is key", "Control rats"]
        tips_pine = ["Best for sandy soil", "Use Ethephon", "Drought tolerant"]

    # 离线切换：图片 -> Emoji
    return [
        {"rank": "1", "n": "Durian", "cn": "榴莲",
         "img": "🍈" if is_offline else "https://img.icons8.com/color/96/durian.png", "p": 45000,
         "desc_cn": "中国人都爱吃！", "desc_en": "High Demand China", "trend": [1, 2, 4, 5, 7], "tips": tips_durian},
        {"rank": "2", "n": "Chili", "cn": "辣椒",
         "img": "🌶️" if is_offline else "https://img.icons8.com/color/96/chili-pepper.png", "p": 25000,
         "desc_cn": "60天就回本！", "desc_en": "Fast Cash", "trend": [3, 4, 3, 5, 6], "tips": tips_chili},
        {"rank": "3", "n": "Banana", "cn": "香蕉",
         "img": "🍌" if is_offline else "https://img.icons8.com/color/96/banana.png", "p": 18000,
         "desc_cn": "价格很稳，好种。", "desc_en": "Stable Price", "trend": [2, 2, 3, 3, 3], "tips": tips_banana},
        {"rank": "4", "n": "Palm Oil", "cn": "油棕",
         "img": "🌴" if is_offline else "https://img.icons8.com/color/96/palm-tree.png", "p": 12000,
         "desc_cn": "不用天天照顾。", "desc_en": "Easy Care", "trend": [3, 3, 3, 3, 3], "tips": tips_palm},
        {"rank": "5", "n": "Pineapple", "cn": "黄梨",
         "img": "🍍" if is_offline else "https://img.icons8.com/color/96/pineapple.png", "p": 9500,
         "desc_cn": "沙地也能种。", "desc_en": "Sandy Soil OK", "trend": [2, 3, 4, 4, 5], "tips": tips_pine}
    ]


def get_scrolling_tips(lang):
    if lang == "中文":
        return ["🌧️ 雨季记得挖深沟渠排水！", "🍌 香蕉要大条，记得给够钾肥 (K)", "🚜 定期检查土壤酸碱度 (pH 5.5-6.5)",
                "🐛 早上抓害虫", "🌞 烈日下勿喷农药"]
    elif lang == "Bahasa Melayu":
        return ["🌧️ Musim hujan: Dalamkan parit!", "🍌 Pisang perlu Kalium (K)", "🚜 Cek pH tanah (5.5-6.5)",
                "🐛 Pagi masa cari serangga", "🌞 Jangan sembur racun masa panas!"]
    else:
        return ["🌧️ Dig drains deeper!", "🍌 Banana needs Potassium (K)", "🚜 Check pH (5.5-6.5)",
                "🐛 Check insects in morning", "🌞 Don't spray in hot sun!"]


def generate_fixed_sabah_weather():
    random.seed(datetime.now().date().toordinal())
    days = []
    today = datetime.now()
    weather_types = ["☀️", "⛅", "☁️", "🌧️", "⛈️"]
    for i in range(7):
        d = today + timedelta(days=i)
        cond = random.choice(weather_types)
        days.append({"day": d.strftime("%a"), "icon": cond, "temp": f"{random.randint(28, 33)}°C"})
    return days


def get_address(lat, lon, is_offline, t):
    if is_offline:
        return f"{t['loc_offline']} {lat:.3f}, {lon:.3f}"
    try:
        geo = Nominatim(user_agent="sabah_app_v6")
        loc = geo.reverse(f"{lat}, {lon}", language='en')
        return loc.address if loc else "Sabah, Malaysia"
    except:
        return f"Lat: {lat:.3f}, Lon: {lon:.3f}"


def plot_mini_chart(data):
    fig = px.line(x=range(len(data)), y=data)
    fig.update_traces(line_color='#4CAF50', line_width=4)
    fig.update_layout(showlegend=False, xaxis_visible=False, yaxis_visible=False, margin=dict(l=0, r=0, t=0, b=0),
                      height=50, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


# 🟢 智能 Chatbox (处理离线逻辑)
def render_chat_box(context_name, language, api_key, hint_text, tab_key, is_offline):
    t = TRANSLATIONS[language]
    st.markdown(f"<div class='chat-section'><h4>{t['chat_header']} - {context_name}</h4></div>", unsafe_allow_html=True)

    voice_val = None
    if not is_offline:
        st.write("👇")
        voice_lang = 'zh-CN' if language == "中文" else 'ms-MY' if language == "Bahasa Melayu" else 'en-US'
        voice_val = speech_to_text(language=voice_lang, start_prompt=t['mic_start'], stop_prompt=t['mic_stop'],
                                   just_once=True, key=f"chat_mic_{tab_key}")
    else:
        st.caption("🚫 Voice disabled in Offline Mode")

    text_val = st.chat_input(hint_text, key=f"chat_text_{tab_key}")
    user_q = voice_val if voice_val else text_val

    if user_q:
        st.chat_message("user").write(user_q)

        if is_offline:
            st.warning(t['ai_offline_msg'])
            time.sleep(1)
            # 离线简单匹配
            lower_q = user_q.lower()
            if "durian" in lower_q or "榴莲" in lower_q:
                st.chat_message("assistant").write("offline_db: Durian Price ~RM45,000/acre. (Stored Data)")
            else:
                st.chat_message("assistant").write("📝 Note saved to local storage.")
        else:
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    with st.spinner("🤖..."):
                        prompt = f"Role: Sabah Agricultural Expert. Context: {context_name}. Language: {language}. Question: {user_q}. Action: Answer simply."
                        res = model.generate_content(prompt)
                        st.chat_message("assistant").write(res.text)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("⚠️ Please set API Key")


# --- 4. 侧边栏 ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/farmer-male.png", width=80)
    sel_lang = st.selectbox("Language / 语言", ["English", "中文", "Bahasa Melayu"], index=0)
    t = TRANSLATIONS[sel_lang]
    st.divider()

    # 🟢 离线开关
    offline_mode = st.checkbox(t["offline_mode"], value=False)
    if offline_mode:
        st.warning(t["offline_warn"])

    st.divider()
    api_key = ""
    if not offline_mode:
        api_key = st.text_input("Google API Key", type="password")
        try:
            if not api_key and "GOOGLE_API_KEY" in st.secrets: api_key = st.secrets["GOOGLE_API_KEY"]
        except:
            pass

# --- 5. 主页面 ---
st.title(t["title"])
if offline_mode: st.error(t["offline_warn"])

tab1, tab2, tab3 = st.tabs([t["tab_1"], t["tab_2"], t["tab_3"]])

# === Tab 1: 冠军榜 & 天气 ===
with tab1:
    st.subheader(t["top_5_title"])
    cols = st.columns(5)
    top5 = get_top_5(sel_lang, offline_mode)

    for i, col in enumerate(cols):
        crop = top5[i]
        name = crop["cn"] if sel_lang == "中文" else crop["n"]
        desc = crop["desc_cn"] if sel_lang == "中文" else crop["desc_en"]
        with col:
            # 离线 Emoji vs 在线图片
            if offline_mode:
                img_html = f"<div class='offline-emoji'>{crop['img']}</div>"
            else:
                img_html = f"<img src='{crop['img']}' class='cartoon-img'>"

            st.markdown(f"""
            <div class='champ-card'>
                <div class='champ-rank'>#{crop['rank']}</div>
                {img_html}
                <div style='font-weight:bold; font-size:20px;'>{name}</div>
                <div class='champ-profit'>RM {crop['p']:,}</div>
                <div class='champ-desc'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(plot_mini_chart(crop["trend"]), use_container_width=True, config={'staticPlot': True})

    st.write("---")
    st.subheader(t["weather_title"])
    w_cols = st.columns(7)
    weather_data = generate_fixed_sabah_weather()
    for i, w in enumerate(weather_data):
        with w_cols[i]:
            st.markdown(f"""
            <div style='background:#E1F5FE; border:2px solid #29B6F6; border-radius:10px; text-align:center; padding:5px;'>
                <div>{w['day']}</div>
                <div style='font-size:30px;'>{w['icon']}</div>
                <div style='color:#0277BD; font-weight:bold;'>{w['temp']}</div>
            </div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown(f"**{t['tips_scroll_title']}**")
    tips_list = get_scrolling_tips(sel_lang)
    tips_string = "  &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;  ".join(tips_list)
    st.markdown(
        f"""<div class="ticker-wrap"><marquee direction="left" scrollamount="6" class="ticker-text">{tips_string}</marquee></div>""",
        unsafe_allow_html=True)

    render_chat_box("Market & Weather", sel_lang, api_key, t["chat_hint_market"], "tab1", offline_mode)

# === Tab 2: 智能定位 ===
with tab2:
    if "lat" not in st.session_state: st.session_state.lat = 5.9750
    if "lon" not in st.session_state: st.session_state.lon = 116.0724
    if "loc" not in st.session_state: st.session_state.loc = ""
    if "soil" not in st.session_state: st.session_state.soil = "Loam"

    st.subheader(t["step_loc"])
    c_v, c_c, c_g = st.columns(3)

    with c_v:
        if offline_mode:
            st.warning("🚫 Offline")
        else:
            st.info(t["btn_voice"])
            voice_lang = 'zh-CN' if sel_lang == "中文" else 'ms-MY' if sel_lang == "Bahasa Melayu" else 'en-US'
            voice = speech_to_text(language=voice_lang, start_prompt="🎤 GO", stop_prompt="🛑", key="v_btn")
            if voice:
                st.success(f"🗣️: {voice}")
                time.sleep(3)
                st.session_state.loc = voice
                st.rerun()

    with c_c:
        st.info(t["btn_cam"])
        img = st.camera_input("Cam", label_visibility="collapsed")
        if img: st.success("✅ Saved")

    with c_g:
        st.info(t["btn_gps"])
        gps = get_geolocation(component_key='gps_btn')
        if gps:
            lat = gps['coords']['latitude']
            lon = gps['coords']['longitude']
            if abs(lat - st.session_state.lat) > 0.0001:
                st.session_state.lat = lat
                st.session_state.lon = lon
                with st.spinner("📍 Locating... (Wait 3s)"):
                    addr = get_address(lat, lon, offline_mode, t)
                    st.session_state.loc = addr
                    time.sleep(3)
                st.rerun()

    st.write("---")
    display_addr = st.session_state.loc if st.session_state.loc else "Sabah, Malaysia (Default)"
    st.markdown(f"<div class='address-box'>{t['addr_found']} {display_addr}</div>", unsafe_allow_html=True)
    st.write(f"**{t['map_title']}**")

    if offline_mode:
        st.warning(t['map_offline'])
    else:
        map_df = pd.DataFrame({'lat': [st.session_state.lat], 'lon': [st.session_state.lon]})
        st.map(map_df, zoom=11, size=400, color='#FF0000')

    st.write("---")
    if st.button("🚀 START / 开始分析", type="primary"):
        with st.spinner("🤖 Analyzing..."):
            time.sleep(3)
            if img:
                st.session_state.soil = "Sandy"
            elif "Ranau" in display_addr:
                st.session_state.soil = "Highland"
            else:
                st.session_state.soil = "Clay"
            st.rerun()

    if st.session_state.get("soil"):
        if "Sandy" in st.session_state.soil:
            best = top5[4]
        elif "Highland" in st.session_state.soil:
            best = top5[1]
        else:
            best = top5[0]

        n_show = best["cn"] if sel_lang == "中文" else best["n"]

        # 离线 Emoji 处理
        if offline_mode:
            res_img_html = f"<div style='font-size:100px;'>{best['img']}</div>"
        else:
            res_img_html = f"<img src='{best['img']}' style='width:120px;'>"

        st.markdown(f"""
        <div style='background:#E8F5E9; border:3px solid #4CAF50; border-radius:20px; padding:20px; text-align:center;'>
            <h2 style='color:#2E7D32;'>{t['res_title']}</h2>
            {res_img_html}
            <h1>{n_show}</h1>
            <div style='font-size:22px; color:#D32F2F; font-weight:bold;'>RM {best['p']:,}</div>
        </div>""", unsafe_allow_html=True)

        st.subheader(t["res_tips_title"])
        for tip in best["tips"]:
            st.info(f"✅ {tip}")

        st.subheader(t["buyers"])
        st.markdown(f"""
        <div style='background:white; padding:15px; border-radius:10px; border:1px solid #ddd; display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
            <div style='font-weight:bold;'>👤 Ah Huat (Sabah)</div>
            <a href='tel:0123456' style='background:#03A9F4; color:white; padding:10px 20px; border-radius:20px; text-decoration:none;'>📞 Call</a>
        </div>
        """, unsafe_allow_html=True)

    render_chat_box("Planting & Soil Analysis", sel_lang, api_key, t["chat_hint_soil"], "tab2", offline_mode)

# === Tab 3: 工具箱 ===
with tab3:
    st.subheader(t["tools_title"])
    tc1, tc2, tc3 = st.columns(3)

    # 图标逻辑
    icon_calc = "🧮" if offline_mode else "<img src='https://img.icons8.com/color/96/calculator.png' style='width:60px;'>"
    icon_cam = "📷" if offline_mode else "<img src='https://img.icons8.com/color/96/search.png' style='width:60px;'>"
    icon_truck = "🚛" if offline_mode else "<img src='https://img.icons8.com/color/96/truck.png' style='width:60px;'>"

    with tc1:
        st.markdown(f"<div class='tool-card'>{icon_calc}<h3>{t['t1']}</h3></div>", unsafe_allow_html=True)
        if st.button("Open Calc", key="btn_t1"): st.info("💰 Cost: RM 5k -> Sales: RM 15k")
    with tc2:
        st.markdown(f"<div class='tool-card'>{icon_cam}<h3>{t['t2']}</h3></div>", unsafe_allow_html=True)
        if st.button("Open Cam", key="btn_t2"): st.warning("📸 Please upload leaf photo.")
    with tc3:
        st.markdown(f"<div class='tool-card'>{icon_truck}<h3>{t['t3']}</h3></div>", unsafe_allow_html=True)
        if st.button("Find Lorry", key="btn_t3"): st.success("🚛 Found 3 Lorries nearby!")

    render_chat_box("Farm Tools & Logistics", sel_lang, api_key, t["chat_hint_tools"], "tab3", offline_mode)
