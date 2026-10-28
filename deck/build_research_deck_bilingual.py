# -*- coding: utf-8 -*-
"""研究报告型 PPT —— 中英双语版（各 20 页，短句、少字）。"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement

NAVY = RGBColor(0x1F, 0x2A, 0x44)
BLUE = RGBColor(0x3A, 0x6E, 0xA5)
TEAL = RGBColor(0x2F, 0x6F, 0x5E)
AMBER = RGBColor(0xC8, 0x62, 0x2A)
INK = RGBColor(0x1B, 0x24, 0x30)
MUTED = RGBColor(0x6B, 0x76, 0x86)
LINE = RGBColor(0xD8, 0xDE, 0xE7)
LIGHT = RGBColor(0xF4, 0xF6, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SW, SH = 13.333, 7.5
M = 0.85

T = {
 "cn": {
  "cjk": "PingFang SC",
  "kicker": "AI 教育 · 研究报告",
  "cover": ("当 AI 直接给出答案", "用「会出错的历史人物」训练学生判断"),
  "team": "[小组成员]   ·   AI in Education   ·   2026",
  "q_title": "三个问题",
  "qs": [("Q1", "学生现在怎么学？", "先问 AI。"),
         ("Q2", "AI 能训练思考吗？", "还是让它替我们思考？"),
         ("Q3", "怎么判断有没有效？", "分数可信吗？")],
  "q_foot": "我们关心的不是「AI 能不能教」，而是「学生还要不要想」。",
  "b1_title": "用 AI 做作业：48% → 62%",
  "b1_cat": ["2025 年 5 月", "2025 年 12 月"],
  "b1_series": "使用比例",
  "b1_big": "+14 个百分点",
  "b1_sub": "7 个月，1,214 名青少年",
  "howto_b1": "怎么读：同一批 12–29 岁青少年（n=1,214）在 7 个月内，用 AI 做作业的比例从 48% 升到 62%。",
  "howto_b2": "怎么读：三种高频用途都是「让 AI 产出内容」，而不是「让 AI 检验我的判断」。",
  "howto_b3": "怎么读：三项独立调查从不同角度指向同一件事——学生和教师的担忧都在上升。",
  "howto_gap": "怎么读：横轴是 AI 的角色，纵轴是学科。现有工作集中在左半边，我们做右下角。",
  "b1_a": "45% 在学校用过 AI",
  "b1_b": "85% 的 AI 用户用它做作业",
  "b2_title": "但用途只有一种",
  "b2_cat": ["求解释", "找想法", "查事实"],
  "b2_note": "三种用途，都是\n「让 AI 替我想」。",
  "b3_title": "担忧在两端同时上升",
  "b3": [("67%", "学生担心 AI 损害批判性思维\n（2025 年初为 54%）"), ("43.2%", "老师担心学生用生成式 AI\n（同比 +7.5pp）"), ("54%", "老师认为 AI 让思考更难学\n（2026 教师民调）")],
  "pain_title": "历史最核心的能力，最容易被代劳",
  "pain_chain": ["AI 给答案", "学生跳过求证", "史料判断被跳过", "只剩结论"],
  "pain_a": "历史不是「发生了什么」，而是「凭什么相信它发生过」。",
  "pain_b": "AI 越顺，学生越没理由查证。",
  "lit_title": "现有 AI 教育的五种做法",
  "lit_head": ["做法", "形式", "解决什么"],
  "lit_rows": [("AI 答疑", "对话讲解", "听懂"), ("作文批改", "打分给建议", "减负"),
               ("题库生成", "自动出题", "多练"), ("翻译陪练", "即时翻译", "跨语言"),
               ("角色扮演", "和人物聊天", "沉浸感")],
  "lit_foot": "五种做法，都在缩短学生和答案的距离。",
  "gap_title": "空白：把「AI 会错」当教材",
  "gap_x": "AI：给答案  ←→  被审视",
  "gap_y1": "通用", "gap_y2": "历史",
  "gap_q": ["AI 答疑 / 批改", "少见", "历史人物聊天", "本项目"],
  "gap_main": "（主流）",
  "app_title": "我们的做法：让 AI 当证人，而不是答案",
  "app_line": "AI 扮演有立场、会出错的历史人物。学生查史料，再做决定。",
  "app_steps": [("提问", "追问依据"), ("查史料", "对一对"), ("做决定", "选一个"), ("写理由", "讲清楚"), ("看反馈", "评分 + 画像")],
  "app_foot": "区别只有一句：AI 不是答案，是需要被检验的信源。",
  "sys_title": "四个模块",
  "sys_mods": [("场景", "历史时刻"), ("史料", "带出处"), ("人物", "按史料说话"), ("评估", "评分 + 分析")],
  "sys_note": "现成模型 + 提示词 + 小史料库。不训练模型。",
  "stu_title": "学生四步",
  "stu": [("1", "选人物"), ("2", "追问"), ("3", "查史料"), ("4", "做决定")],
  "tea_title": "老师三步",
  "tea": [("1", "生成人设"), ("2", "改史料与抉择"), ("3", "发布")],
  "ass_title": "看五个方面",
  "ass": [("溯源", "问来源"), ("语境", "放回当时"), ("交叉", "比多份"), ("论证", "有证据"), ("共情", "理解处境")],
  "rel_title": "评分：打两次，看是否一致",
  "rel_steps": [("第一次", "t = 0.0"), ("第二次", "t = 0.5"), ("比较", "差多少"), ("标记", "不一致 → 人工看")],
  "rel_note": "不一致就标出来，不假装可信。",
  "fb_title": "用户反馈（虚拟示例）",
  "fb": [("现在它会反问我，我得自己想。", "学生 A"),
         ("原来 AI 说的和课本不一样。", "学生 B"),
         ("我以为写得挺好，结果只有 2 分。", "学生 C"),
         ("能用在别的科目吗？", "学生 D"),
         ("以前写人设最花时间，现在点一下就有。", "教师 E")],
  "fb_warn": "以上为虚拟示例，实测后替换。",
  "code_title": "反馈怎么归类",
  "code_head": ["类别", "典型说法"],
  "code_rows": [("累不累", "「更累，但更投入」"), ("信不信", "「AI 也会错」"),
                ("准不准", "「我以为我写得挺好」"), ("能不能迁移", "「能用在别的科目吗」")],
  "hyp_title": "四条待验证的猜想",
  "hyp": [("H1", "学生想得更多了"), ("H2", "不再盲信 AI"), ("H3", "更会评价自己"), ("H4", "老师上手更快")],
  "hyp_warn": "这是猜想，不是结论。",
  "lim_title": "局限",
  "lim": ["样本小，时间短。", "打分主观，AI 评分会飘。", "史料库薄，练习就弱。"],
  "fut_title": "下一步",
  "fut": ["角色互换：学生演人物，AI 追问。", "双人对质：两个立场相反的人物。", "更大规模对照实验。"],
  "qa": ("Q & A", "谢谢，欢迎提问。"),
  "ref_title": "参考文献与数据来源",
  "ref_note": "检索日期：2026-10-28。数字以原文为准；不同调查对「使用 AI」的定义不同（16%–85%）。",
  "refs": [
    "RAND Corporation（2026-03-17）. More Students Use AI for Homework and Believe It Harms Their Learning. n = 1,214，12–29 岁. rand.org",
    "HEPI（2025-02）. Student Generative AI Survey 2025. 45% 的学生在学校用过 AI. hepi.ac.uk",
    "Common Sense Media（2025）. 青少年生成式 AI 使用调查：85% 的 AI 使用者把它用于学业. commonsensemedia.org",
    "National Literacy Trust（2025-08）. Young people and teachers' use of generative AI：43.2% 教师担忧（+7.5pp）. literacytrust.org.uk",
    "CSBA Blog（2026-04）. Students express mixed feelings on AI use for homework. blog.csba.org",
    "Central Florida Public Media（2026-06）. 教师民调：54% 认为 AI 让批判性思考更难学.",
    "RAND（2026-03）. 学生担忧比例 54% → 67%；聊天机器人使用率 60%（ChatGPT 53%、Gemini 28%）.",
  ],
  "src": {
   "b1": "RAND, “More Students Use AI for Homework…” (2026-03-17, n=1,214) · HEPI, Student Generative AI Survey (2025-02) · Common Sense Media (2025)",
   "b2": "RAND (2026-03-17). Uses: explanations 38%, brainstorming 35%, fact lookup 33%.",
   "b3": "RAND (2026-03) · National Literacy Trust (2025-08) · teacher poll reported by Central Florida Public Media (2026-06)",
   "gap": "Indicative positioning, not an exhaustive review.",
  },
 },
 "en": {
  "cjk": "Arial",
  "kicker": "AI IN EDUCATION · RESEARCH REPORT",
  "cover": ("When AI Gives the Answer", "Training judgment with a historian who may be wrong"),
  "team": "[Team members]   ·   AI in Education   ·   2026",
  "q_title": "Three questions",
  "qs": [("Q1", "How do students learn now?", "They ask AI first."),
         ("Q2", "Can AI train thinking?", "Or does it think for us?"),
         ("Q3", "Does it work?", "Can we trust the score?")],
  "q_foot": "The question is not whether AI can teach — but whether students still think.",
  "b1_title": "AI for homework: 48% → 62%",
  "b1_cat": ["May 2025", "Dec 2025"],
  "b1_series": "Share using AI",
  "b1_big": "+14 points",
  "b1_sub": "in 7 months · 1,214 teens",
  "howto_b1": "How to read: among 1,214 youth aged 12–29, AI-for-homework use rose from 48% to 62% in seven months.",
  "howto_b2": "How to read: the top three uses all mean “let AI produce something”, not “let AI check my judgement”.",
  "howto_b3": "How to read: three independent surveys point the same way — concern is rising among students and teachers.",
  "howto_gap": "How to read: x = the AI's role, y = the subject. Existing work sits on the left; we work in the bottom-right.",
  "b1_a": "45% have used AI at school",
  "b1_b": "85% of AI-using teens use it for schoolwork",
  "b2_title": "But always for the same thing",
  "b2_cat": ["Better explanations", "Ideas", "Facts"],
  "b2_note": "All three mean:\n\"let AI think for me.\"",
  "b3_title": "Concern is rising on both sides",
  "b3": [("67%", "of students worry AI harms critical thinking\n(54% earlier in 2025)"), ("43.2%", "of teachers worried about student AI use\n(+7.5 pp year on year)"), ("54%", "of teachers say AI makes thinking harder\n(2026 teacher poll)")],
  "pain_title": "History's core skill is the easiest to outsource",
  "pain_chain": ["AI answers", "Student skips checking", "Sourcing is skipped", "Only conclusions remain"],
  "pain_a": "History is not \"what happened\" — it is \"why believe it happened\".",
  "pain_b": "The smoother AI gets, the less reason to check.",
  "lit_title": "Five ways AI is used in education",
  "lit_head": ["Approach", "Form", "Solves"],
  "lit_rows": [("AI tutor", "Explains in chat", "Understanding"), ("Essay grading", "Scores + advice", "Teacher load"),
               ("Question gen.", "Auto-made items", "Practice"), ("Translation", "Live translate", "Language"),
               ("Role-play", "Chat with figures", "Immersion")],
  "lit_foot": "All five shorten the distance to the answer.",
  "gap_title": "The gap: AI as material to doubt",
  "gap_x": "AI: gives answers  ←→  is questioned",
  "gap_y1": "General", "gap_y2": "History",
  "gap_q": ["AI tutor / grading", "Rare", "Historical chat", "This project"],
  "gap_main": "(mainstream)",
  "app_title": "Our approach: an AI witness, not an oracle",
  "app_line": "The AI plays a historical actor with a stake — and can be wrong. Students check sources, then decide.",
  "app_steps": [("Ask", "Push back"), ("Check", "Compare sources"), ("Decide", "Pick one"), ("Justify", "Explain why"), ("Feedback", "Score + profile")],
  "app_foot": "One difference: the AI is not the answer — it is a source to check.",
  "sys_title": "Four modules",
  "sys_mods": [("Scenario", "a moment"), ("Sources", "with provenance"), ("Persona", "grounded in sources"), ("Assessment", "scores + analytics")],
  "sys_note": "Pretrained model + prompts + a small source library. No training.",
  "stu_title": "Student flow",
  "stu": [("1", "Pick a figure"), ("2", "Ask"), ("3", "Check sources"), ("4", "Decide")],
  "tea_title": "Teacher flow",
  "tea": [("1", "Generate the persona"), ("2", "Edit sources & decisions"), ("3", "Publish")],
  "ass_title": "Five things we look at",
  "ass": [("Sourcing", "Where from?"), ("Context", "In its time"), ("Corroboration", "Compare"), ("Argument", "Evidence"), ("Empathy", "Their situation")],
  "rel_title": "Scoring: run it twice, check agreement",
  "rel_steps": [("Pass 1", "t = 0.0"), ("Pass 2", "t = 0.5"), ("Compare", "gap"), ("Flag", "low → review")],
  "rel_note": "If the two passes disagree, we say so.",
  "fb_title": "User feedback (illustrative)",
  "fb": [("Now it asks me back, so I have to think.", "Student A"),
         ("I found out AI's answer didn't match the book.", "Student B"),
         ("I thought it was good. It got 2.", "Student C"),
         ("Can I use this in other subjects?", "Student D"),
         ("Writing the persona used to take hours.", "Teacher E")],
  "fb_warn": "Illustrative only — to be replaced with real data.",
  "code_title": "How we code the feedback",
  "code_head": ["Code", "Typical line"],
  "code_rows": [("Effort", "\"Harder, but I'm more into it\""), ("Trust", "\"AI can be wrong\""),
                ("Self-judgement", "\"I thought it was good\""), ("Transfer", "\"Other subjects?\"")],
  "hyp_title": "Four hypotheses to test",
  "hyp": [("H1", "Students think more"), ("H2", "They stop trusting AI blindly"), ("H3", "They judge their work better"), ("H4", "Teachers onboard faster")],
  "hyp_warn": "Hypotheses, not findings.",
  "lim_title": "Limitations",
  "lim": ["Small sample, short study.", "Scoring is subjective and unstable.", "A thin source library weakens the task."],
  "fut_title": "Next steps",
  "fut": ["Role reversal: the student plays the figure.", "Two-agent debate: opposing accounts.", "A larger controlled study."],
  "qa": ("Q & A", "Thank you — questions welcome."),
  "ref_title": "References and data sources",
  "ref_note": "Retrieved 2026-10-28. Figures as reported; definitions of “using AI” vary across surveys (16%–85%).",
  "refs": [
    "RAND Corporation (2026-03-17). More Students Use AI for Homework and Believe It Harms Their Learning. n = 1,214, ages 12–29. rand.org",
    "HEPI (2025-02). Student Generative AI Survey 2025. 45% have used AI at school. hepi.ac.uk",
    "Common Sense Media (2025). Teens' generative-AI use: 85% of AI-using teens use it for schoolwork. commonsensemedia.org",
    "National Literacy Trust (2025-08). Young people and teachers' use of generative AI: 43.2% of teachers concerned (+7.5pp). literacytrust.org.uk",
    "CSBA Blog (2026-04). Students express mixed feelings on AI use for homework. blog.csba.org",
    "Central Florida Public Media (2026-06). Teacher poll: 54% say AI makes critical thinking harder.",
    "RAND (2026-03). Student concern 54% → 67%; chatbot use 60% (ChatGPT 53%, Gemini 28%).",
  ],
  "src": {
   "b1": "RAND, “More Students Use AI for Homework…” (2026-03-17, n=1,214) · HEPI, Student Generative AI Survey (2025-02) · Common Sense Media (2025)",
   "b2": "RAND (2026-03-17). Uses: explanations 38%, brainstorming 35%, fact lookup 33%.",
   "b3": "RAND (2026-03) · National Literacy Trust (2025-08) · teacher poll reported by Central Florida Public Media (2026-06)",
   "gap": "Indicative positioning, not an exhaustive review.",
  },
 },
}


def build(lang, out):
    t = T[lang]
    CJK = t["cjk"]

    def _font(run, size, bold=False, color=INK, italic=False):
        run.font.size = Pt(size); run.font.bold = bold; run.font.italic = italic
        run.font.color.rgb = color; run.font.name = CJK
        rpr = run._r.get_or_add_rPr()
        ea = rpr.find(qn("a:ea"))
        if ea is None:
            ea = OxmlElement("a:ea"); rpr.append(ea)
        ea.set("typeface", CJK)

    def box(slide, x, y, w, h, text, size=16, bold=False, color=INK,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.15, italic=False):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = 0; tf.margin_top = tf.margin_bottom = 0
        for i, line in enumerate(str(text).split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align; p.line_spacing = spacing
            r = p.add_run(); r.text = line
            _font(r, size, bold, color, italic)
        return tb

    def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08):
        sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        if fill is None: sh.fill.background()
        else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
        if line is None: sh.line.fill.background()
        else: sh.line.color.rgb = line; sh.line.width = Pt(1.1)
        sh.shadow.inherit = False
        if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            try: sh.adjustments[0] = radius
            except Exception: pass
        return sh

    prs = Presentation()
    prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)
    blank = prs.slide_layouts[6]

    def page(slide, n):
        box(slide, SW - M - 0.9, SH - 0.5, 0.9, 0.3, str(n), size=10, color=MUTED, align=PP_ALIGN.RIGHT)

    def header(slide, title, kicker, n):
        rect(slide, 0, 0, 0.14, SH, NAVY, shape=MSO_SHAPE.RECTANGLE)
        box(slide, M, 0.55, 11, 0.28, kicker.upper(), size=10.5, bold=True, color=BLUE)
        box(slide, M, 0.9, 11.6, 0.9, title, size=29, bold=True, color=NAVY, spacing=0.95)
        rect(slide, M, 1.82, 0.95, 0.04, BLUE, shape=MSO_SHAPE.RECTANGLE)
        page(slide, n)
        return 2.15

    def src(slide, text):
        box(slide, M, SH - 0.48, 11.2, 0.3, text, size=9, color=MUTED)

    # 1 cover
    s = prs.slides.add_slide(blank)
    rect(s, 0, 0, SW, SH, NAVY, shape=MSO_SHAPE.RECTANGLE)
    rect(s, 0, 0, 0.2, SH, BLUE, shape=MSO_SHAPE.RECTANGLE)
    box(s, M, 1.85, 11, 0.35, t["kicker"], size=12, bold=True, color=RGBColor(0x8F, 0xB6, 0xE0))
    box(s, M, 2.35, 11.6, 1.2, t["cover"][0], size=44, bold=True, color=WHITE, spacing=0.95)
    box(s, M, 3.55, 10.8, 0.8, t["cover"][1], size=18, color=RGBColor(0xC7, 0xD3, 0xE4))
    rect(s, M, 4.55, 1.2, 0.04, BLUE, shape=MSO_SHAPE.RECTANGLE)
    box(s, M, 4.8, 11, 0.35, t["team"], size=12, color=RGBColor(0x9F, 0xAE, 0xC4))
    page(s, 1)

    # 2 questions
    s = prs.slides.add_slide(blank); y = header(s, t["q_title"], t["kicker"], 2)
    cy = y
    for code, head, sub in t["qs"]:
        rect(s, M, cy, 11.6, 1.0, WHITE, line=LINE)
        rect(s, M, cy, 0.07, 1.0, BLUE, shape=MSO_SHAPE.RECTANGLE)
        box(s, M + 0.32, cy + 0.3, 0.8, 0.4, code, size=16, bold=True, color=BLUE)
        box(s, M + 1.2, cy + 0.18, 10.0, 0.4, head, size=16, bold=True, color=NAVY)
        box(s, M + 1.2, cy + 0.6, 10.0, 0.3, sub, size=12, color=MUTED)
        cy += 1.15
    box(s, M, cy + 0.15, 11.6, 0.4, t["q_foot"], size=13, italic=True, color=BLUE)

    # 3 background 1
    s = prs.slides.add_slide(blank); y = header(s, t["b1_title"], t["kicker"], 3)
    cd = CategoryChartData(); cd.categories = t["b1_cat"]; cd.add_series(t["b1_series"], (48, 62))
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(M), Inches(y + 0.1),
                            Inches(6.6), Inches(3.7), cd)
    ch = gf.chart; ch.has_legend = False; ch.font.size = Pt(12); ch.font.color.rgb = INK
    pl = ch.plots[0]; pl.gap_width = 90; pl.has_data_labels = True
    pl.data_labels.number_format = '0"%"'; pl.data_labels.number_format_is_linked = False
    pl.data_labels.font.size = Pt(16); pl.data_labels.font.bold = True
    pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    pl.series[0].format.fill.solid(); pl.series[0].format.fill.fore_color.rgb = BLUE
    ch.value_axis.has_major_gridlines = False; ch.value_axis.maximum_scale = 80
    ch.category_axis.tick_labels.font.size = Pt(11)
    rect(s, 7.85, y + 0.2, 4.6, 1.25, WHITE, line=LINE)
    box(s, 8.1, y + 0.35, 4.1, 0.6, t["b1_big"], size=27, bold=True, color=AMBER)
    box(s, 8.1, y + 0.95, 4.1, 0.35, t["b1_sub"], size=11, color=MUTED)
    box(s, 7.9, y + 1.95, 4.5, 0.35, "·  " + t["b1_a"], size=12, color=INK)
    box(s, 7.9, y + 2.45, 4.5, 0.6, "·  " + t["b1_b"], size=12, color=INK)
    box(s, M, y + 3.95, 11.4, 0.55, t["howto_b1"], size=11.5, color=MUTED, spacing=1.3)
    src(s, t["src"]["b1"])

    # 4 background 2
    s = prs.slides.add_slide(blank); y = header(s, t["b2_title"], t["kicker"], 4)
    cd = CategoryChartData(); cd.categories = t["b2_cat"]; cd.add_series("", (38, 35, 33))
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(M), Inches(y + 0.2),
                            Inches(7.6), Inches(3.2), cd)
    ch = gf.chart; ch.has_legend = False; ch.font.size = Pt(12); ch.font.color.rgb = INK
    pl = ch.plots[0]; pl.gap_width = 70; pl.has_data_labels = True
    pl.data_labels.number_format = '0"%"'; pl.data_labels.number_format_is_linked = False
    pl.data_labels.font.size = Pt(15); pl.data_labels.font.bold = True
    pl.series[0].format.fill.solid(); pl.series[0].format.fill.fore_color.rgb = TEAL
    ch.value_axis.has_major_gridlines = False; ch.value_axis.maximum_scale = 50
    ch.category_axis.reverse_order = True
    rect(s, 8.75, y + 0.3, 3.7, 2.6, LIGHT)
    box(s, 9.05, y + 0.65, 3.1, 1.8, t["b2_note"], size=14, color=INK, spacing=1.5)
    box(s, M, y + 3.55, 11.4, 0.55, t["howto_b2"], size=11.5, color=MUTED, spacing=1.3)
    src(s, t["src"]["b2"])

    # 5 background 3
    s = prs.slides.add_slide(blank); y = header(s, t["b3_title"], t["kicker"], 5)
    for i, (num, desc) in enumerate(t["b3"]):
        x = M + i * 3.95
        rect(s, x, y + 0.15, 3.6, 2.5, WHITE, line=LINE)
        rect(s, x, y + 0.15, 3.6, 0.07, [BLUE, AMBER, TEAL][i], shape=MSO_SHAPE.RECTANGLE)
        box(s, x + 0.3, y + 0.5, 3.0, 0.7, num, size=33, bold=True, color=NAVY)
        box(s, x + 0.3, y + 1.3, 3.0, 1.0, desc, size=12.5, color=INK, spacing=1.3)
    box(s, M, y + 2.85, 11.4, 0.55, t["howto_b3"], size=11.5, color=MUTED, spacing=1.3)
    src(s, t["src"]["b3"])

    # 6 pain
    s = prs.slides.add_slide(blank); y = header(s, t["pain_title"], t["kicker"], 6)
    cw = 2.55
    for i, txt in enumerate(t["pain_chain"]):
        x = M + i * (cw + 0.3)
        rect(s, x, y + 0.35, cw, 1.1, WHITE, line=LINE)
        box(s, x + 0.15, y + 0.45, cw - 0.3, 0.9, txt, size=12.5, color=INK,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.25)
        if i < 3:
            box(s, x + cw, y + 0.75, 0.3, 0.3, "→", size=15, color=BLUE, align=PP_ALIGN.CENTER)
    box(s, M, y + 1.95, 11.4, 0.5, t["pain_a"], size=15, bold=True, color=NAVY)
    box(s, M, y + 2.65, 11.4, 0.4, t["pain_b"], size=14, color=MUTED)

    # 7 literature
    s = prs.slides.add_slide(blank); y = header(s, t["lit_title"], t["kicker"], 7)
    rect(s, M, y, 11.6, 0.4, NAVY, shape=MSO_SHAPE.RECTANGLE)
    for i, h in enumerate(t["lit_head"]):
        box(s, M + 0.18 + [0, 3.2, 7.6][i], y + 0.1, [3.0, 4.2, 3.8][i], 0.3, h,
            size=11.5, bold=True, color=WHITE)
    cy = y + 0.55
    for k, (a, b, c) in enumerate(t["lit_rows"]):
        if k % 2 == 0:
            rect(s, M, cy - 0.06, 11.6, 0.72, LIGHT, shape=MSO_SHAPE.RECTANGLE)
        box(s, M + 0.18, cy, 3.0, 0.5, a, size=13, bold=True, color=NAVY)
        box(s, M + 3.38, cy, 4.1, 0.5, b, size=12, color=MUTED)
        box(s, M + 7.78, cy, 3.6, 0.5, c, size=12, color=INK)
        cy += 0.78
    box(s, M, cy + 0.15, 11.6, 0.4, t["lit_foot"], size=14, italic=True, color=BLUE)

    # 8 gap
    s = prs.slides.add_slide(blank); y = header(s, t["gap_title"], t["kicker"], 8)
    gx, gy, gw, gh = M + 0.9, y + 0.1, 6.4, 3.5
    rect(s, gx, gy, gw, gh, WHITE, line=LINE, shape=MSO_SHAPE.RECTANGLE)
    rect(s, gx, gy, gw / 2, gh / 2, LIGHT, shape=MSO_SHAPE.RECTANGLE)
    rect(s, gx, gy + gh / 2, gw / 2, gh / 2, LIGHT, shape=MSO_SHAPE.RECTANGLE)
    rect(s, gx + gw / 2, gy, 0.02, gh, LINE, shape=MSO_SHAPE.RECTANGLE)
    rect(s, gx, gy + gh / 2, gw, 0.02, LINE, shape=MSO_SHAPE.RECTANGLE)
    box(s, gx, gy + gh + 0.12, gw, 0.3, t["gap_x"], size=10.5, color=MUTED, align=PP_ALIGN.CENTER)
    box(s, gx - 1.25, gy + gh / 2 - 0.2, 1.15, 0.3, t["gap_y1"], size=10.5, color=MUTED, align=PP_ALIGN.RIGHT)
    box(s, gx - 1.25, gy + gh - 0.2, 1.15, 0.3, t["gap_y2"], size=10.5, color=MUTED, align=PP_ALIGN.RIGHT)
    q = t["gap_q"]
    box(s, gx + 0.22, gy + 0.3, 2.9, 0.7, q[0] + "\n" + t["gap_main"], size=11, color=MUTED, spacing=1.3)
    box(s, gx + gw / 2 + 0.22, gy + 0.3, 2.8, 0.4, q[1], size=11, color=MUTED)
    box(s, gx + 0.22, gy + gh / 2 + 0.3, 2.9, 0.7, q[2] + "\n" + t["gap_main"], size=11, color=MUTED, spacing=1.3)
    rect(s, gx + gw / 2 + 0.22, gy + gh / 2 + 0.22, gw / 2 - 0.44, gh / 2 - 0.44, NAVY)
    box(s, gx + gw / 2 + 0.42, gy + gh / 2 + 0.42, 2.6, 0.9, q[3], size=13, bold=True, color=WHITE)
    box(s, 8.35, y + 0.35, 4.2, 1.5, t["howto_gap"], size=11, color=MUTED, spacing=1.35)
    src(s, t["src"]["gap"])

    # 9 approach
    s = prs.slides.add_slide(blank); y = header(s, t["app_title"], t["kicker"], 9)
    box(s, M, y, 11.6, 0.5, t["app_line"], size=14.5, color=INK, spacing=1.3)
    bw, gap = 2.14, 0.24
    for i, (a, b) in enumerate(t["app_steps"]):
        x = M + i * (bw + gap)
        rect(s, x, y + 0.85, bw, 1.3, WHITE, line=LINE)
        rect(s, x, y + 0.85, bw, 0.07, TEAL, shape=MSO_SHAPE.RECTANGLE)
        box(s, x + 0.12, y + 1.03, bw - 0.24, 0.35, a, size=13.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        box(s, x + 0.12, y + 1.45, bw - 0.24, 0.5, b, size=10.5, color=MUTED, align=PP_ALIGN.CENTER)
        if i < 4:
            box(s, x + bw, y + 1.35, gap, 0.3, "→", size=15, color=BLUE, align=PP_ALIGN.CENTER)
    box(s, M, y + 2.45, 11.6, 0.4, t["app_foot"], size=13.5, italic=True, color=BLUE)

    # 10 system
    s = prs.slides.add_slide(blank); y = header(s, t["sys_title"], t["kicker"], 10)
    for i, (a, b) in enumerate(t["sys_mods"]):
        x = M + i * 2.98
        rect(s, x, y + 0.1, 2.72, 1.3, WHITE, line=LINE)
        rect(s, x, y + 0.1, 2.72, 0.07, BLUE, shape=MSO_SHAPE.RECTANGLE)
        box(s, x + 0.22, y + 0.32, 2.3, 0.35, a, size=14, bold=True, color=NAVY)
        box(s, x + 0.22, y + 0.78, 2.3, 0.45, b, size=11, color=MUTED)
    box(s, M, y + 1.75, 11.6, 0.4, t["sys_note"], size=13, color=INK)
    box(s, M, y + 2.5, 11.6, 0.35, "[ screenshot ]", size=11.5, color=MUTED, italic=True)

    # 11 student
    s = prs.slides.add_slide(blank); y = header(s, t["stu_title"], t["kicker"], 11)
    for i, (num, txt) in enumerate(t["stu"]):
        x = M + i * 2.98
        rect(s, x, y + 0.2, 2.72, 2.0, WHITE, line=LINE)
        box(s, x + 0.25, y + 0.4, 0.6, 0.6, num, size=22, bold=True, color=BLUE)
        box(s, x + 0.25, y + 1.15, 2.2, 0.6, txt, size=13.5, bold=True, color=NAVY, spacing=1.2)
    box(s, M, y + 2.5, 11.6, 0.35, "[ screenshot ]", size=11.5, color=MUTED, italic=True)

    # 12 teacher
    s = prs.slides.add_slide(blank); y = header(s, t["tea_title"], t["kicker"], 12)
    for i, (num, txt) in enumerate(t["tea"]):
        x = M + i * 3.95
        rect(s, x, y + 0.25, 3.6, 2.2, WHITE, line=LINE)
        box(s, x + 0.3, y + 0.45, 0.6, 0.6, num, size=22, bold=True, color=TEAL)
        box(s, x + 0.3, y + 1.2, 3.0, 0.7, txt, size=14, bold=True, color=NAVY, spacing=1.2)
    box(s, M, y + 2.75, 11.6, 0.35, "[ screenshot ]", size=11.5, color=MUTED, italic=True)

    # 13 assessment
    s = prs.slides.add_slide(blank); y = header(s, t["ass_title"], t["kicker"], 13)
    for i, (a, b) in enumerate(t["ass"]):
        row, col = i // 2, i % 2
        x = M + col * 5.95; yy = y + row * 1.05
        rect(s, x, yy, 5.6, 0.88, WHITE, line=LINE)
        rect(s, x, yy, 0.06, 0.88, BLUE, shape=MSO_SHAPE.RECTANGLE)
        box(s, x + 0.22, yy + 0.12, 2.3, 0.35, a, size=13, bold=True, color=NAVY)
        box(s, x + 2.55, yy + 0.14, 2.9, 0.35, b, size=11.5, color=MUTED)
    box(s, M, y + 2.45, 11.6, 0.35, "0–3 · 15 " + ("分" if lang == "cn" else "pts"), size=12.5, color=INK)

    # 14 reliability
    s = prs.slides.add_slide(blank); y = header(s, t["rel_title"], t["kicker"], 14)
    for i, (a, b) in enumerate(t["rel_steps"]):
        x = M + i * 2.95
        rect(s, x, y + 0.2, 2.65, 1.15, WHITE, line=LINE)
        box(s, x + 0.16, y + 0.36, 2.3, 0.35, a, size=13, bold=True, color=NAVY)
        box(s, x + 0.16, y + 0.76, 2.3, 0.3, b, size=10.5, color=MUTED)
        if i < 3:
            box(s, x + 2.65, y + 0.62, 0.3, 0.3, "→", size=15, color=BLUE, align=PP_ALIGN.CENTER)
    rect(s, M, y + 1.75, 11.6, 0.9, LIGHT)
    box(s, M + 0.35, y + 1.98, 10.9, 0.5, t["rel_note"], size=13, color=INK)

    # 15 feedback
    s = prs.slides.add_slide(blank); y = header(s, t["fb_title"], t["kicker"], 15)
    for i, (q, who) in enumerate(t["fb"]):
        col, row = i % 2, i // 2
        x = M + col * 5.95; yy = y + row * 1.12
        w = 5.6 if i < 4 else 11.6
        rect(s, x, yy, w, 0.92, WHITE, line=LINE)
        box(s, x + 0.22, yy + 0.18, w - 1.4, 0.6, "「" + q + "」" if lang == "cn" else "“" + q + "”",
            size=11.5, color=INK, spacing=1.3)
        box(s, x + w - 1.25, yy + 0.3, 1.05, 0.3, who, size=9.5, color=MUTED, align=PP_ALIGN.RIGHT)
    box(s, M, y + 3.45, 11.6, 0.3, t["fb_warn"], size=11, color=AMBER, italic=True)

    # 16 coding
    s = prs.slides.add_slide(blank); y = header(s, t["code_title"], t["kicker"], 16)
    rect(s, M, y, 11.6, 0.4, NAVY, shape=MSO_SHAPE.RECTANGLE)
    box(s, M + 0.18, y + 0.1, 4.0, 0.3, t["code_head"][0], size=11.5, bold=True, color=WHITE)
    box(s, M + 4.4, y + 0.1, 7.0, 0.3, t["code_head"][1], size=11.5, bold=True, color=WHITE)
    cy = y + 0.55
    for k, (a, b) in enumerate(t["code_rows"]):
        if k % 2 == 0:
            rect(s, M, cy - 0.06, 11.6, 0.72, LIGHT, shape=MSO_SHAPE.RECTANGLE)
        box(s, M + 0.18, cy, 4.0, 0.5, a, size=13, bold=True, color=NAVY)
        box(s, M + 4.4, cy, 7.0, 0.5, b, size=12, color=MUTED)
        cy += 0.78

    # 17 hypotheses
    s = prs.slides.add_slide(blank); y = header(s, t["hyp_title"], t["kicker"], 17)
    cy = y
    for code, txt in t["hyp"]:
        rect(s, M, cy, 11.6, 0.9, WHITE, line=LINE)
        rect(s, M, cy, 0.07, 0.9, TEAL, shape=MSO_SHAPE.RECTANGLE)
        box(s, M + 0.3, cy + 0.24, 0.8, 0.4, code, size=16, bold=True, color=TEAL)
        box(s, M + 1.25, cy + 0.26, 9.9, 0.4, txt, size=14.5, bold=True, color=NAVY)
        cy += 1.05
    box(s, M, cy + 0.1, 11.6, 0.3, t["hyp_warn"], size=11, color=AMBER, italic=True)

    # 18 limitations
    s = prs.slides.add_slide(blank); y = header(s, t["lim_title"], t["kicker"], 18)
    cy = y
    for txt in t["lim"]:
        rect(s, M, cy, 11.6, 0.8, WHITE, line=LINE)
        box(s, M + 0.35, cy + 0.24, 10.9, 0.4, txt, size=15, color=INK)
        cy += 0.95

    # 19 future
    s = prs.slides.add_slide(blank); y = header(s, t["fut_title"], t["kicker"], 19)
    cy = y
    for txt in t["fut"]:
        rect(s, M, cy, 11.6, 0.8, WHITE, line=LINE)
        box(s, M + 0.35, cy + 0.24, 10.9, 0.4, txt, size=15, color=INK)
        cy += 0.95

    # 20 references
    s = prs.slides.add_slide(blank); y = header(s, t["ref_title"], t["kicker"], 20)
    cy = y
    for i, line in enumerate(t["refs"], 1):
        box(s, M, cy, 0.5, 0.3, f"[{i}]", size=10.5, bold=True, color=BLUE)
        box(s, M + 0.5, cy, 11.0, 0.62, line, size=10.5, color=INK, spacing=1.35)
        cy += 0.68
    box(s, M, SH - 0.62, 11.4, 0.3, t["ref_note"], size=9, color=MUTED)

    # 21 Q&A
    s = prs.slides.add_slide(blank)
    rect(s, 0, 0, SW, SH, NAVY, shape=MSO_SHAPE.RECTANGLE)
    rect(s, 0, 0, 0.2, SH, BLUE, shape=MSO_SHAPE.RECTANGLE)
    box(s, M, 2.7, 11, 0.9, t["qa"][0], size=40, bold=True, color=WHITE)
    box(s, M, 3.8, 11, 0.5, t["qa"][1], size=17, color=RGBColor(0xC7, 0xD3, 0xE4))
    page(s, 21)

    prs.save(out)
    print("saved:", out)


build("cn", "/Users/rogan09/Documents/Codex/2026-10-09/new-chat/outputs/History_AI_Research_Report_CN.pptx")
build("en", "/Users/rogan09/Documents/Codex/2026-10-09/new-chat/outputs/History_AI_Research_Report_EN.pptx")
