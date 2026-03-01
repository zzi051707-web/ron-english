import streamlit as st
import time
import json
import os
from datetime import datetime, date, timedelta
import random
import pandas as pd
import plotly.express as px
import calendar
from io import StringIO

# ========================== 【本地Ron哥照片·核心配置】 ==========================
if not os.path.exists("ron_photos"):
    os.makedirs("ron_photos")
if not os.path.exists("my_checkin_photos"):
    os.makedirs("my_checkin_photos")

# 读取你本地ron_photos里的6张照片（ron1~ron6.jpg）
PHOTO_SCENES = {
    "default": "ron_photos/ron1.jpg",
    "greeting": "ron_photos/ron4.jpg",
    "lazy_mode_on": "ron_photos/ron2.jpg",
    "task_complete": "ron_photos/ron3.jpg",
    "all_done": "ron_photos/ron5.jpg",
    "achievement_unlock": "ron_photos/ron6.jpg",
    "timer_end": "ron_photos/ron2.jpg"
}
ALL_PHOTOS = [f"ron_photos/ron{i}.jpg" for i in range(1, 7)]

# ========================== 【学习任务·语录·成就·盲盒·全配置】 ==========================
DEFAULT_TASKS = {
    "背单词": {"子任务":["新单词数量","复习单词数量"],"默认目标":[50,100],"懒人目标":[25,50],"单位":["个","个"]},
    "练习听力": {"子任务":["精听篇数","泛听时长(分钟)"],"默认目标":[1,30],"懒人目标":[1,15],"单位":["篇","分钟"]},
    "看美剧学英语": {"子任务":["观看集数","记录口语表达数量"],"默认目标":[1,10],"懒人目标":[1,5],"单位":["集","个"]}
}

RONGE_QUOTES = {
    "greeting": {"morning":"早啊，新的一天，先把单词背了再摸鱼？[旺柴]","afternoon":"下午好，别犯困了，抽25分钟练个听力，哥陪着你。","evening":"晚上啦，今天的任务完成得怎么样了？没完成也别熬太晚。","midnight":"怎么还不睡？[皱眉] 快放下手机睡觉，学习明天再学也来得及。","friday":"周五啦！完成今天的任务，周末就能放心玩了，加油。","monday":"新的一周开始了，别摆烂，先把今天的任务搞定。","weekend":"哟，周末都在学？也太卷了吧！[旺柴] 学完赶紧去玩。","default":"哟，来了？今天打算学点什么？[旺柴]"},
    "lazy_mode": {"on":"没事，今天状态不好就少学点，总比一点不学强[拥抱]，先完成再说，别逼自己太紧。","off":"好样的！今天状态不错嘛，冲！[得意]"},
    "tasks": {"背单词":{"完成":"嗯呢，新单词+复习都搞定了，这记性可以啊！[旺柴] 坚持下去，词汇量咔咔涨。","未完成":"哈哈，单词背少了点？没事哈，别逼自己太紧，剩下的今天抽空补了就行。","超额":"我去，单词背这么多？功德直接拉满！[动画表情] 拿盆接着你的功德！"},"练习听力":{"完成":"听力精听+泛听都搞定了，耳朵都磨出来了！[拥抱] 慢慢听，语感会越来越棒的。","未完成":"听力还差一点？没事，今天累了就少听点，纯靠磨。","超额":"可以啊，听力还多练了会儿？这劲头，开学听力不得直接起飞？[得意]"},"看美剧学英语":{"完成":"美剧看完还记了表达，这才叫有效看剧！[敲打] 不是光看热闹。","未完成":"美剧只看了没记表达？没事，下次边看边记，哪怕5个也行。","超额":"我滴乖乖，记这么多表达？这效率，哥都佩服了！[旺柴]"}},
    "global": {"all_done":"今天三项任务全搞定了？牛啊！[动画表情] 自己的助理自己心疼，学完赶紧歇会儿，买杯奶茶去。","partial_done":"今天完成了大半任务，不错不错，比摆烂强多了！[皱眉] 剩下的明天补上就行。","none_done":"哈哈，今天是不是犯懒了？[苦涩] 没事，翻篇了，明天咱重新来。"},
    "achievement": "🏆 解锁新成就：「{name}」！\n\n{msg}",
    "timer_reminder": "嗯呢，计时结束！刚才学的内容，记得去打卡区填完成量哦[旺柴]",
    "focus_hour": "可以啊，连续专注学了1小时！这效率，必须给你记上一笔[得意]",
    "review": {"positive":["不错不错，能有成就感就说明没白学！继续保持这个势头。","可以啊，这状态越来越好了，哥看好你。","记住了就好，日积月累，你会越来越厉害的。"],"negative":["没事，跟不上很正常，多磨磨耳朵就好了，下次可以先听慢速的，别慌[拥抱]","挫败是暂时的，能坐下来学就已经赢了一半了，明天咱接着来。","别急，慢慢来，学习不是一天两天的事，哥相信你可以的。"],"lazy":["哈哈，没事，哪怕只学了一点点，也比摆烂强，明天继续加油就行。","能意识到自己犯懒就不错了，翻篇了，明天咱重新开始。"]},
    "photo_checkin": "不错哦，今天还拍了打卡照！[旺柴] 记录下努力的自己～"
}

ACHIEVEMENTS = [
    {"id":"first_checkin","name":"初次见面","desc":"完成第一次打卡","icon":"👋","msg":"Ron哥记住你了！以后好好干。"},
    {"id":"week_warrior","name":"勤奋小能手","desc":"连续7天完成所有任务","icon":"🔥","msg":"连续一周都坚持下来了，牛啊！[动画表情] 开学必须给你带奶茶。"},
    {"id":"word_king","name":"单词王者","desc":"累计背单词超过1000个","icon":"📚","msg":"可以啊，这词汇量，四级阅读不得直接拿捏？[得意]"},
    {"id":"ear_master","name":"听力磨耳达人","desc":"累计听力练习超过10小时","icon":"🎧","msg":"耳朵都磨出来了，慢慢听，语感会越来越棒的。[拥抱]"},
    {"id":"super_idol","name":"卷王认证","desc":"单日超额完成200%任务","icon":"👑","msg":"我去，今天这么卷？功德直接拉满！拿盆接好你的功德。"},
    {"id":"never_give_up","name":"永不言弃","desc":"断卡后重新连续打卡3天","icon":"💪","msg":"没事哈，翻篇了，能重新捡起来就超棒了，继续保持。"},
    {"id":"focus_master","name":"专注达人","desc":"累计专注学习满10小时","icon":"⏱️","msg":"可以啊，坐得住冷板凳，这才是干大事的人！"},
    {"id":"photo_star","name":"打卡达人","desc":"累计上传10张打卡照片","icon":"📸","msg":"坚持拍照打卡，记录每一次努力，必须给你点个赞！"}
]

BLIND_BOXES = [
    {"type":"easy","name":"轻松款","task":"今天多背10个单词","reward":"解锁Ron哥专属吐槽一句"},
    {"type":"challenge","name":"挑战款","task":"今天精听2篇听力","reward":"解锁Ron哥隐藏表扬信"},
    {"type":"lazy_saver","name":"摆烂救星款","task":"今天哪怕只学10分钟","reward":"今天就算你过关，不骂你"}
]

# ========================== 【数据初始化·永不报错】 ==========================
STUDY_DATA_FILE = "study_data.json"
CHECKIN_DATA_FILE = "checkin_records.json"
ACHIEVEMENT_FILE = "achievements.json"
CONFIG_FILE = "user_config.json"

for f in [CONFIG_FILE, STUDY_DATA_FILE, CHECKIN_DATA_FILE, ACHIEVEMENT_FILE]:
    if not os.path.exists(f):
        if f == CONFIG_FILE: json.dump({"tasks":DEFAULT_TASKS}, open(f,"w",encoding="utf-8"))
        elif f == STUDY_DATA_FILE: json.dump({"total_study_seconds":0,"daily_records":{},"checkin_days":0,"focus_hours_count":0}, open(f,"w",encoding="utf-8"))
        elif f == CHECKIN_DATA_FILE: json.dump({"daily_checkin":{},"photo_checkin":{}}, open(f,"w",encoding="utf-8"))
        elif f == ACHIEVEMENT_FILE:
            json.dump({"unlocked":[],"stats":{"total_checkins":0,"max_streak":0,"current_streak":0,"total_words":0,"total_listening":0,"has_exceeded":False,"comeback":False,"total_focus_hours":0,"total_photo_checkins":0},"daily_blind_box":{}}, open(f,"w",encoding="utf-8"))

USER_CONFIG = json.load(open(CONFIG_FILE,"r",encoding="utf-8"))
STUDY_TASKS = USER_CONFIG.get("tasks", DEFAULT_TASKS)
study_data = json.load(open(STUDY_DATA_FILE,"r",encoding="utf-8"))
checkin_data = json.load(open(CHECKIN_DATA_FILE,"r",encoding="utf-8"))
ach_data = json.load(open(ACHIEVEMENT_FILE,"r",encoding="utf-8"))

today = str(date.today())
now = datetime.now()
weekday = now.weekday()
is_weekend = weekday >= 5

# 会话状态
if "is_running" not in st.session_state: st.session_state.is_running = False
if "start_time" not in st.session_state: st.session_state.start_time = 0
if "elapsed_seconds" not in st.session_state: st.session_state.elapsed_seconds = 0
if "target_seconds" not in st.session_state: st.session_state.target_seconds = 25*60
if "timer_mode" not in st.session_state: st.session_state.timer_mode = "countdown"
if "lazy_mode" not in st.session_state: st.session_state.lazy_mode = False
if "new_achievement_popup" not in st.session_state: st.session_state.new_achievement_popup = None
if "current_photo" not in st.session_state: st.session_state.current_photo = PHOTO_SCENES["default"]

# 每日盲盒
if today not in ach_data.get("daily_blind_box",{}):
    ach_data["daily_blind_box"][today] = random.choice(BLIND_BOXES)
    json.dump(ach_data, open(ACHIEVEMENT_FILE,"w",encoding="utf-8"))
todays_box = ach_data["daily_blind_box"][today]

# ========================== 【核心功能函数】 ==========================
def get_greeting():
    h = now.hour
    if is_weekend and 8<=h<22: return RONGE_QUOTES["greeting"]["weekend"]
    if 0<=h<6: return RONGE_QUOTES["greeting"]["midnight"]
    elif 6<=h<12: return RONGE_QUOTES["greeting"]["monday"] if weekday==0 else RONGE_QUOTES["greeting"]["morning"]
    elif 12<=h<18: return RONGE_QUOTES["greeting"]["afternoon"]
    else: return RONGE_QUOTES["greeting"]["friday"] if weekday==4 else RONGE_QUOTES["greeting"]["evening"]

def calculate_stats():
    stats = ach_data["stats"].copy()
    defaults = {"total_checkins":0,"max_streak":0,"current_streak":0,"total_words":0,"total_listening":0,"has_exceeded":False,"comeback":False,"total_focus_hours":0,"total_photo_checkins":0}
    for k,v in defaults.items():
        if k not in stats: stats[k] = v
    dates = sorted(checkin_data["daily_checkin"].keys())
    if not dates: return stats
    streak = 0
    tmp = date.today()
    for _ in range(365):
        s = str(tmp)
        if s in checkin_data["daily_checkin"] and sum(sum(checkin_data["daily_checkin"][s][t]["完成量"]) for t in checkin_data["daily_checkin"][s])>0:
            streak +=1
        else: break
        tmp -= timedelta(days=1)
    stats["current_streak"] = streak
    stats["max_streak"] = max(streak, stats["max_streak"])
    stats["total_photo_checkins"] = len(checkin_data.get("photo_checkin",{}))
    stats["total_focus_hours"] = study_data.get("total_study_seconds",0)//3600
    return stats

def check_achievements():
    s = calculate_stats()
    ach_data["stats"] = s
    new_ach = None
    for ach in ACHIEVEMENTS:
        u = False
        if ach["id"]=="first_checkin" and s["total_checkins"]>=1:u=True
        if ach["id"]=="week_warrior" and s["current_streak"]>=7:u=True
        if ach["id"]=="word_king" and s["total_words"]>=1000:u=True
        if ach["id"]=="ear_master" and s["total_listening"]>=600:u=True
        if ach["id"]=="super_idol" and s["has_exceeded"]:u=True
        if ach["id"]=="never_give_up" and s["comeback"]:u=True
        if ach["id"]=="focus_master" and s["total_focus_hours"]>=10:u=True
        if ach["id"]=="photo_star" and s["total_photo_checkins"]>=10:u=True
        if u and ach["id"] not in ach_data["unlocked"]:
            ach_data["unlocked"].append(ach["id"])
            new_ach = ach
    json.dump(ach_data,open(ACHIEVEMENT_FILE,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    return new_ach

def save_checkin_photo(file):
    if file:
        fn = f"my_checkin_photos/{today}_{int(time.time())}_{file.name}"
        with open(fn,"wb") as w: w.write(file.getbuffer())
        checkin_data["photo_checkin"][today] = fn
        json.dump(checkin_data,open(CHECKIN_DATA_FILE,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
        return fn
    return None

# ========================== 【页面·全功能·完整版】 ==========================
st.set_page_config(page_title="Ron哥陪你学英语",page_icon="📚",layout="wide")

# —————— 侧边栏：成就 + Ron哥照片轮播 + 盲盒 + 统计 ——————
with st.sidebar:
    st.title("🏆 Ron哥成就墙")
    st.divider()
    st.subheader("📸 Ron哥的日常")
    if st.button("🎲 换一张照片"):
        st.session_state.current_photo = random.choice(ALL_PHOTOS)
    try:
        st.image(st.session_state.current_photo, width=200)
    except:
        st.write("👋 Ron哥就在你身边～")
    
    st.divider()
    cs = calculate_stats()
    st.metric("连续打卡", f"{cs['current_streak']} 天")
    st.metric("专注时长", f"{cs['total_focus_hours']} 小时")
    st.metric("照片打卡", f"{cs['total_photo_checkins']} 张")
    
    st.divider()
    st.subheader(f"🎁 今日盲盒：{todays_box['name']}")
    st.info(f"✅ 任务：{todays_box['task']}\n🎁 奖励：{todays_box['reward']}")
    
    st.divider()
    st.caption("已解锁成就：")
    for ach in ACHIEVEMENTS:
        if ach["id"] in ach_data["unlocked"]:
            st.success(f"{ach['icon']} {ach['name']}\n{ach['desc']}")
        else:
            st.info(f"🔒 ???\n{ach['desc']}")

# —————— 主页面：Ron哥问候 ——————
st.title("✨ Ron哥陪你学英语 · 全功能完整版 ✨")
greet = get_greeting()
st.session_state.current_photo = PHOTO_SCENES["greeting"]
c1, c2 = st.columns([1,3])
with c1:
    try:
        st.image(st.session_state.current_photo, width=220)
    except:
        st.write("👋 Ron哥向你打招呼")
with c2:
    st.info(f"💬 Ron哥：{greet}")

if st.session_state.new_achievement_popup:
    ach = st.session_state.new_achievement_popup
    st.balloons()
    st.success(RONGE_QUOTES["achievement"].format(name=ach["name"],msg=ach["msg"]))
    st.session_state.new_achievement_popup = None

st.divider()

# —————— 1. 打卡日历 ——————
st.subheader("📅 打卡日历（红框=照片打卡）")
cal = calendar.monthcalendar(now.year, now.month)
cols = st.columns(7)
for i,d in enumerate(["一","二","三","四","五","六","日"]): cols[i].markdown(f"**{d}**")
for w in cal:
    cols = st.columns(7)
    for i,d in enumerate(w):
        if d==0: cols[i].write("")
        else:
            ds = f"{now.year}-{now.month:02d}-{d:02d}"
            has_p = ds in checkin_data.get("photo_checkin",{})
            is_c = ds in checkin_data["daily_checkin"]
            is_t = d==now.day
            lb = f"👉{d}" if is_t else f"{d}"
            if has_p: cols[i].error(lb)
            elif is_c: cols[i].success(lb)
            elif is_t: cols[i].warning(lb)
            else: cols[i].info(lb)

st.divider()

# —————— 2. 任务设置 ——————
with st.expander("⚙️ 自定义学习目标（任务设置）"):
    st.caption("修改后点击「保存全局设置」")
    for tn in STUDY_TASKS:
        st.subheader(f"📖 {tn}")
        cols = st.columns(len(STUDY_TASKS[tn]["子任务"]))
        for i,sub in enumerate(STUDY_TASKS[tn]["子任务"]):
            with cols[i]:
                nv = st.number_input(f"{sub} 默认目标", min_value=1, value=STUDY_TASKS[tn]["默认目标"][i])
                STUDY_TASKS[tn]["默认目标"][i] = nv
                STUDY_TASKS[tn]["懒人目标"][i] = max(1, nv//2)
    if st.button("💾 保存全局设置"):
        USER_CONFIG["tasks"] = STUDY_TASKS
        json.dump(USER_CONFIG, open(CONFIG_FILE,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
        st.success("设置保存成功！")

st.divider()

# —————— 3. 今日学习打卡 ——————
st.subheader("📝 今日学习任务")
lazy_col, _ = st.columns([1,3])
with lazy_col:
    st.session_state.lazy_mode = st.checkbox("😴 懒人模式（目标减半）", value=st.session_state.lazy_mode)
    if st.session_state.lazy_mode:
        st.success(RONGE_QUOTES["lazy_mode"]["on"])

completed = []
if today not in checkin_data["daily_checkin"]:
    checkin_data["daily_checkin"][today] = {t:{"完成量":[]} for t in STUDY_TASKS}

for tn,ti in STUDY_TASKS.items():
    ct = ti["懒人目标"] if st.session_state.lazy_mode else ti["默认目标"]
    with st.expander(f"📖 {tn}", expanded=True):
        cols = st.columns(len(ti["子任务"]))
        total = 0
        for i,(sub,unit) in enumerate(zip(ti["子任务"], ti["单位"])):
            with cols[i]:
                val = checkin_data["daily_checkin"][today][tn]["完成量"][i] if len(checkin_data["daily_checkin"][today][tn]["完成量"])>i else 0
                v = st.number_input(f"{sub}（目标{ct[i]}{unit}）", min_value=0, value=val)
                if len(checkin_data["daily_checkin"][today][tn]["完成量"])>i:
                    checkin_data["daily_checkin"][today][tn]["完成量"][i] = v
                else:
                    checkin_data["daily_checkin"][today][tn]["完成量"].append(v)
                total += v
        if total >= sum(ct):
            st.success(RONGE_QUOTES["tasks"][tn]["完成"])
            completed.append(tn)
        elif total>0:
            st.warning(RONGE_QUOTES["tasks"][tn]["未完成"])

st.divider()

# —————— 4. 照片打卡 + 分页汇总 ——————
st.subheader("📸 每日照片打卡")
up = st.file_uploader("上传今日打卡照片", type=["jpg","jpeg","png"])
if up and st.button("✅ 确认上传打卡照片"):
    save_checkin_photo(up)
    st.success(RONGE_QUOTES["photo_checkin"])
    na = check_achievements()
    if na:
        st.session_state.new_achievement_popup = na
        st.rerun()

with st.expander("🖼️ 我的打卡照片历史 · 分页查看"):
    p_dates = sorted(checkin_data.get("photo_checkin",{}).keys(), reverse=True)
    if p_dates:
        page_size = 6
        page = st.selectbox("选择页码", range(1, len(p_dates)//page_size +2))
        idx = (page-1)*page_size
        cur = p_dates[idx:idx+page_size]
        for i in range(0, len(cur), 3):
            cs = st.columns(3)
            for j,ds in enumerate(cur[i:i+3]):
                with cs[j]:
                    st.markdown(f"**{ds}**")
                    try:
                        st.image(checkin_data["photo_checkin"][ds], width=150)
                    except:
                        st.write("照片已保存")
    else:
        st.info("还没有照片打卡记录～")

st.divider()

# —————— 5. 学习复盘 ——————
st.subheader("💭 跟Ron哥聊两句·学习复盘")
review = st.text_area("记录今天的心情/收获/难题")
if st.button("发送给Ron哥"):
    if review:
        pool = RONGE_QUOTES["review"]["positive"]
        if any(w in review for w in ["难","累","挫败","差"]):
            pool = RONGE_QUOTES["review"]["negative"]
        elif any(w in review for w in ["懒","没学","不想"]):
            pool = RONGE_QUOTES["review"]["lazy"]
        st.info(f"💬 Ron哥：{random.choice(pool)}")

st.divider()

# —————— 6. 保存打卡 ——————
if st.button("💾 保存今日所有打卡", use_container_width=True, type="primary"):
    json.dump(checkin_data, open(CHECKIN_DATA_FILE,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    na = check_achievements()
    if len(completed)==3:
        st.balloons()
        st.snow()
        st.success(RONGE_QUOTES["global"]["all_done"])
    elif len(completed)>0:
        st.success(RONGE_QUOTES["global"]["partial_done"])
    else:
        st.info(RONGE_QUOTES["global"]["none_done"])
    if na:
        st.session_state.new_achievement_popup = na
        st.rerun()

st.divider()

# —————— 7. 学习时长可视化·坚持曲线 ——————
st.subheader("📈 学习坚持曲线 · 可视化统计")
records = study_data.get("daily_records", {})
if records:
    df = pd.DataFrame({
        "日期": list(records.keys()),
        "学习分钟": [v//60 for v in records.values()]
    }).sort_values("日期")
    fig = px.line(df, x="日期", y="学习分钟", title="每日学习时长趋势", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("还没有学习记录，开始打卡生成你的坚持曲线吧～")

st.divider()

# —————— 8. 学习计时器 ——————
st.subheader("⏱️ 专注计时器")
mc, sc = st.columns([1,2])
with mc:
    mode = st.radio("模式", ["倒计时","正计时"], horizontal=True)
    st.session_state.timer_mode = "countdown" if mode=="倒计时" else "forward"
with sc:
    if st.session_state.timer_mode == "countdown":
        mins = st.number_input("倒计时分钟", min_value=1, value=25)
        st.session_state.target_seconds = mins*60

timer_display = st.empty()
c1,c2,c3 = st.columns(3)
if c1.button("▶️ 开始", use_container_width=True, type="primary"):
    st.session_state.is_running = True
    st.session_state.start_time = time.time() - st.session_state.elapsed_seconds
if c2.button("⏸️ 暂停", use_container_width=True):
    st.session_state.is_running = False
if c3.button("🔄 重置", use_container_width=True):
    st.session_state.is_running = False
    st.session_state.elapsed_seconds = 0

while st.session_state.is_running:
    st.session_state.elapsed_seconds = time.time() - st.session_state.start_time
    if st.session_state.timer_mode == "countdown":
        rem = st.session_state.target_seconds - st.session_state.elapsed_seconds
        if rem <=0:
            st.session_state.is_running = False
            study_data["total_study_seconds"] += st.session_state.target_seconds
            study_data["daily_records"][today] = study_data["daily_records"].get(today,0) + st.session_state.target_seconds
            study_data["checkin_days"] +=1
            json.dump(study_data, open(STUDY_DATA_FILE,"w",encoding="utf-8"))
            st.success(RONGE_QUOTES["timer_reminder"])
            st.balloons()
            st.session_state.elapsed_seconds =0
            st.rerun()
        m,s = divmod(int(rem),60)
        timer_display.markdown(f"<h1 style='text-align:center;color:red'>剩余：{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
    else:
        m,s = divmod(int(st.session_state.elapsed_seconds),60)
        timer_display.markdown(f"<h1 style='text-align:center;color:green'>已学：{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
    time.sleep(0.1)
    st.rerun()

if st.session_state.timer_mode == "forward" and not st.session_state.is_running and st.session_state.elapsed_seconds>0:
    if st.button("✅ 保存专注时长", use_container_width=True, type="primary"):
        study_data["total_study_seconds"] += st.session_state.elapsed_seconds
        study_data["daily_records"][today] = study_data["daily_records"].get(today,0) + st.session_state.elapsed_seconds
        json.dump(study_data, open(STUDY_DATA_FILE,"w",encoding="utf-8"))
        st.success("专注时长保存成功！")
        st.session_state.elapsed_seconds =0
        st.rerun()

st.divider()

# —————— 9. 数据导出 + 手机访问 ——————
st.subheader("📤 数据备份 & 📱 手机访问")
c1,c2 = st.columns(2)
with c1:
    if st.button("生成打卡记录CSV"):
        o = StringIO()
        o.write("日期,总完成量,照片打卡\n")
        for d in sorted(checkin_data["daily_checkin"].keys()):
            t = sum(sum(checkin_data["daily_checkin"][d][t]["完成量"]) for t in checkin_data["daily_checkin"][d] if "完成量" in checkin_data["daily_checkin"][d])
            p = "是" if d in checkin_data.get("photo_checkin",{}) else "否"
            o.write(f"{d},{t},{p}\n")
        st.download_button("📥 下载文件", o.getvalue(), f"学习打卡_{today}.csv", "text/csv")
with c2:
    st.code("手机访问：同一WiFi → 电脑查IPv4 → 浏览器输入 http://电脑IP:8501")