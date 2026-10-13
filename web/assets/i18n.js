/* 界面多语言：简体中文 / 繁體中文 / English
 *
 * 做法：以"简体原文"为键的字典 + DOM 翻译。
 * - 只翻译字典里精确命中的文本节点，因此 AI 回复、学生答案、教师填写的人物内容不会被误翻。
 * - 切回中文时用 WeakMap 里保存的原文还原。
 */
const DICT = {
  // ---- 通用 / 导航 ----
  "学生端": ["學生端", "Student"],
  "教师端": ["教師端", "Teacher"],
  "学情分析": ["學情分析", "Analytics"],
  "AI 历史人物模拟器": ["AI 歷史人物模擬器", "AI Historical Figure Simulator"],
  "学生端 · AI 历史人物模拟器": ["學生端 · AI 歷史人物模擬器", "Student · AI Historical Figure Simulator"],
  "教师端 · AI 历史人物模拟器": ["教師端 · AI 歷史人物模擬器", "Teacher · AI Historical Figure Simulator"],
  "学情分析 · AI 历史人物模拟器": ["學情分析 · AI 歷史人物模擬器", "Analytics · AI Historical Figure Simulator"],
  "对话 · AI 历史人物模拟器": ["對話 · AI 歷史人物模擬器", "Chat · AI Historical Figure Simulator"],
  "AI 历史人物模拟器 · 学生端": ["AI 歷史人物模擬器 · 學生端", "AI Historical Figure Simulator · Student"],
  "AI 历史人物模拟器 · 教师端": ["AI 歷史人物模擬器 · 教師端", "AI Historical Figure Simulator · Teacher"],
  "加载中…": ["載入中…", "Loading…"],
  "关闭": ["關閉", "Close"],
  "发送": ["傳送", "Send"],
  "删除": ["刪除", "Delete"],
  "提示": ["提示", "Hint"],
  "资料与任务": ["資料與任務", "Resources & tasks"],
  "卡通形象": ["卡通形象", "Avatar"],
  "拖拽图片到此处，或点击选择": ["拖曳圖片到此處，或點擊選擇", "Drag an image here, or click to choose"],
  "assets/avatars/xxx.svg（也可手动填路径）": ["assets/avatars/xxx.svg（也可手動填路徑）", "assets/avatars/xxx.svg (or type a path)"],
  "只支持 PNG / JPG / WEBP / GIF 图片": ["只支援 PNG / JPG / WEBP / GIF 圖片", "Only PNG / JPG / WEBP / GIF are supported"],
  "图片太大，请压缩到 2MB 以内": ["圖片太大，請壓縮到 2MB 以內", "Image too large — please keep it under 2 MB"],
  "图片数据读取失败": ["圖片資料讀取失敗", "Could not read the image data"],
  "形象上传失败": ["形象上傳失敗", "Avatar upload failed"],
  "上传中…": ["上傳中…", "Uploading…"],
  "上传成功": ["上傳成功", "Uploaded"],
  "API：": ["API：", "API: "],
  "离线演示（无需 API）": ["離線演示（無需 API）", "Offline demo (no API needed)"],
  "OpenAI 兼容（OpenAI / DeepSeek / 通义 / 智谱 …）": ["OpenAI 相容（OpenAI / DeepSeek / 通義 / 智譜 …）", "OpenAI-compatible (OpenAI / DeepSeek / Qwen / Zhipu …)"],
  "本地 Ollama": ["本地 Ollama", "Local Ollama"],
  "Anthropic Claude": ["Anthropic Claude", "Anthropic Claude"],
  "开始": ["開始", "Start"],
  "级提示（不扣分，仅供教师参考）。": ["級提示（不扣分，僅供教師參考）。", " hint(s) — no penalty, shown to the teacher only."],
  "低估": ["低估", "under-rated"],
  "高估": ["高估", "over-rated"],

  // ---- 学生端首页 ----
  "选择一位历史人物，开始一场对话": ["選擇一位歷史人物，開始一場對話", "Pick a historical figure and start a conversation"],
  "这里的 AI 扮演的不是「全知百科」，而是": ["這裡的 AI 扮演的不是「全知百科」，而是", "The AI here is not an all-knowing encyclopedia — it plays"],
  "有立场、可能带偏见的历史当事人": ["有立場、可能帶偏見的歷史當事人", "a historical actor with a stake and a possible bias"],
  "。向他提问、追问、质疑——再想一想：你凭什么相信他说的？": ["。向他提問、追問、質疑——再想一想：你憑什麼相信他說的？", ". Ask, push back, question — then ask yourself: why do you believe him?"],
  "与他对话 →": ["與他對話 →", "Talk to him →"],
  "暂无已发布的历史人物。请到教师端发布。": ["暫無已發布的歷史人物。請到教師端發布。", "No published figures yet. Publish one from the teacher console."],

  // ---- 对话页 ----
  "＋ 新对话": ["＋ 新對話", "＋ New chat"],
  "← 返回": ["← 返回", "← Back"],
  "向这位历史人物提问…（Enter 发送 / Shift+Enter 换行）": ["向這位歷史人物提問…（Enter 傳送 / Shift+Enter 換行）", "Ask this historical figure… (Enter to send / Shift+Enter for a new line)"],
  "API 接口": ["API 介面", "API"],
  "模型名": ["模型名稱", "Model"],
  "API Key（仅本机浏览器保存）": ["API Key（僅本機瀏覽器儲存）", "API Key (stored only in this browser)"],
  "我的历史思维画像": ["我的歷史思維畫像", "My historical-thinking profile"],
  "抉择任务": ["抉擇任務", "Decision tasks"],
  "可查证的史料": ["可查證的史料", "Sources you can check"],
  "可以这样问": ["可以這樣問", "Try asking"],
  "有立场、可能带偏见": ["有立場、可能帶偏見", "has a stake, may be biased"],
  "。别急着相信——先追问他「你怎么知道的」，再对照史料。": ["。別急著相信——先追問他「你怎麼知道的」，再對照史料。", ". Don't believe it yet — ask how he knows, then check the sources."],
  "这位人物": ["這位人物", "this figure"],
  "该人物尚未关联史料。": ["該人物尚未關聯史料。", "No sources linked to this figure yet."],
  "暂无建议问题。": ["暫無建議問題。", "No suggested questions yet."],
  "该人物暂无抉择任务。": ["該人物暫無抉擇任務。", "This figure has no decision tasks yet."],
  "完成一次「抉择任务」后，这里会出现你的能力画像。": ["完成一次「抉擇任務」後，這裡會出現你的能力畫像。", "Complete one decision task and your profile will appear here."],
  "最需要加强：": ["最需要加強：", "Focus on: "],
  "📖 指标说明与水平划分": ["📖 指標說明與水平劃分", "📖 What the indicators mean"],
  "指标说明与水平划分": ["指標說明與水平劃分", "What the indicators mean"],
  "五个指标各 0–3 分。下面是它们的意思，以及不同分数段代表的水平。": ["五個指標各 0–3 分。下面是它們的意思，以及不同分數段代表的水平。", "Each indicator is scored 0–3. Below: what it means, and what each score band represents."],
  "低": ["低", "Low"],
  "高": ["高", "High"],
  "史料溯源": ["史料溯源", "Sourcing"],
  "语境化": ["語境化", "Contextualization"],
  "交叉验证": ["交叉驗證", "Corroboration"],
  "论证": ["論證", "Argumentation"],
  "历史共情": ["歷史共情", "Historical empathy"],
  "起步": ["起步", "Starting"],
  "初步": ["初步", "Emerging"],
  "较好": ["較好", "Good"],
  "成熟": ["成熟", "Mature"],
  "分": ["分", "pts"],

  // ---- 抉择弹窗 ----
  "抉择：": ["抉擇：", "Decision: "],
  "你的论证——为什么这样选？最好引用史料作为依据。": ["你的論證——為什麼這樣選？最好引用史料作為依據。", "Your argument — why this choice? Cite the sources if you can."],
  "例如：我选择……，因为……（依据：《……》）": ["例如：我選擇……，因為……（依據：《……》）", "e.g. I choose … because … (based on …)"],
  "先自评：你觉得你的论证在这五方面各能得几分？（0–3，必填）": ["先自評：你覺得你的論證在這五方面各能得幾分？（0–3，必填）", "Self-assess first: how would you score your own argument on each of the five? (0–3, required)"],
  "💡 需要一点提示？": ["💡 需要一點提示？", "💡 Need a hint?"],
  "已给出全部提示": ["已給出全部提示", "All hints shown"],
  "启用双评分（两次独立评分 + 一致性，更可靠，约 2 倍耗时）": ["啟用雙評分（兩次獨立評分 + 一致性，更可靠，約 2 倍耗時）", "Double scoring (two independent passes + agreement; more reliable, about 2× the cost)"],
  "提交论证": ["提交論證", "Submit argument"],
  "请先选择一个选项": ["請先選擇一個選項", "Choose an option first"],
  "请写下你的论证": ["請寫下你的論證", "Write your argument first"],
  "请先完成自评（还差": ["請先完成自評（還差", "Finish your self-assessment ("],
  " 项）": [" 項）", " left)"],
  "评估中…": ["評估中…", "Scoring…"],
  "总分": ["總分", "Total"],
  "自评 vs AI": ["自評 vs AI", "Self vs AI"],
  "自评": ["自評", "Self"],
  "元认知提示：": ["元認知提示：", "Metacognition: "],
  "自评与 AI 评分基本一致。": ["自評與 AI 評分基本一致。", "Your self-rating matches the AI score."],
  "👍 做得好": ["👍 做得好", "👍 What worked"],
  "🔧 可以改进": ["🔧 可以改進", "🔧 What to improve"],
  "点评": ["點評", "Comments"],
  "一致性": ["一致性", "agreement"],
  "⚠️ 评分一致性偏低": ["⚠️ 評分一致性偏低", "⚠️ Low scoring agreement"],
  "该次评分的部分维度两次结果差异较大，建议教师复核或让学生补充论证后再评。": ["該次評分的部分維度兩次結果差異較大，建議教師複核或讓學生補充論證後再評。", "Two scoring passes disagreed on some dimensions — a teacher should review, or the student should expand the argument."],
  "本次使用了": ["本次使用了", "This attempt used"],
  " 级提示（不扣分，仅供教师参考）。": [" 級提示（不扣分，僅供教師參考）。", " hint level(s) — no penalty, shown to the teacher only."],
  "评估失败": ["評估失敗", "Scoring failed"],

  // ---- 史料核对 ----
  "🔍 核对史料": ["🔍 核對史料", "🔍 Check the sources"],
  "核对史料": ["核對史料", "Check the sources"],
  "要核对的 AI 说法：": ["要核對的 AI 說法：", "Claim to check:"],
  "可对照的史料：": ["可對照的史料：", "Sources to compare:"],
  "这条说法与史料相符吗？": ["這條說法與史料相符嗎？", "Does this claim match the sources?"],
  "相符": ["相符", "Matches"],
  "有出入": ["有出入", "Differs"],
  "有出入（夸大、偏差，或与史料矛盾）": ["有出入（誇大、偏差，或與史料矛盾）", "Differs (exaggerated, skewed, or contradicts the sources)"],
  "史料未涉及": ["史料未涉及", "Not covered"],
  "你的依据——依据哪一份史料？为什么？": ["你的依據——依據哪一份史料？為什麼？", "Your basis — which source, and why?"],
  "例如：依据《……》，其中说……，与该说法不同，因为……": ["例如：依據《……》，其中說……，與該說法不同，因為……", "e.g. According to …, which says …, this claim differs because …"],
  "提交核对": ["提交核對", "Submit check"],
  "请先选择你的判断": ["請先選擇你的判斷", "Choose your judgement first"],
  "请写下你的依据": ["請寫下你的依據", "Write your basis first"],
  "核对中…": ["核對中…", "Checking…"],
  "你的判断：": ["你的判斷：", "Your judgement: "],
  "参照判断": ["參照判斷", "Reference view"],
  "可以改进": ["可以改進", "What to improve"],
  "核对失败": ["核對失敗", "Check failed"],

  // ---- 教师端 ----
  "历史人物（全部）": ["歷史人物（全部）", "Figures (all)"],
  "＋ 新建人物": ["＋ 新增人物", "＋ New figure"],
  "编辑历史人物": ["編輯歷史人物", "Edit figure"],
  "新建历史人物": ["新增歷史人物", "New figure"],
  "基本信息": ["基本資訊", "Basics"],
  "人物设定": ["人物設定", "Persona"],
  "史料": ["史料", "Sources"],
  "建议问题": ["建議問題", "Suggested questions"],
  "抉择节点": ["抉擇節點", "Decision tasks"],
  "发布": ["發布", "Publish"],
  "ID（英文，唯一）": ["ID（英文，唯一）", "ID (English, unique)"],
  "姓名": ["姓名", "Name"],
  "英文名": ["英文名", "English name"],
  "时代": ["時代", "Era"],
  "难度": ["難度", "Difficulty"],
  "入门": ["入門", "Intro"],
  "进阶": ["進階", "Intermediate"],
  "挑战": ["挑戰", "Challenge"],
  "主题色": ["主題色", "Accent colour"],
  "一句话简介": ["一句話簡介", "One-line summary"],
  "卡通形象路径": ["卡通形象路徑", "Avatar path"],
  "开场白（学生进入对话时看到的第一句）": ["開場白（學生進入對話時看到的第一句）", "Opening line (first thing the student sees)"],
  "限制词 / system prompt（AI 扮演该人物的行为约束）": ["限制詞 / system prompt（AI 扮演該人物的行為約束）", "Persona prompt / system prompt (how the AI must behave)"],
  "每份史料独立一张卡片。类型下拉可直接选择，没有合适的就选「自定义」自行填写。": ["每份史料獨立一張卡片。類型下拉可直接選擇，沒有合適的就選「自訂」自行填寫。", "One card per source. Pick the type from the dropdown, or choose “Custom” and type your own."],
  "＋ 添加一份史料": ["＋ 新增一份史料", "＋ Add a source"],
  "这些会显示在学生端右侧「可以这样问」。": ["這些會顯示在學生端右側「可以這樣問」。", "These appear under “Try asking” on the student side."],
  "＋ 添加一个问题": ["＋ 新增一個問題", "＋ Add a question"],
  "每个抉择节点 = 情境 + 若干选项 + 提示。学生将从中选择并提交论证。": ["每個抉擇節點 = 情境 + 若干選項 + 提示。學生將從中選擇並提交論證。", "Each decision task = a scenario + options + hints. The student chooses and submits an argument."],
  "＋ 添加一个抉择节点": ["＋ 新增一個抉擇節點", "＋ Add a decision task"],
  "每个板块独立编辑。列表类内容（史料 / 问题 / 抉择 / 选项）都可以": ["每個板塊獨立編輯。列表類內容（史料 / 問題 / 抉擇 / 選項）都可以", "Each section is edited on its own. Lists (sources / questions / decisions / options) can all be"],
  "单独增删改": ["單獨增刪改", "added, edited or removed individually"],
  "。改完点底部「保存并发布」同步到学生端。": ["。改完點底部「儲存並發布」同步到學生端。", ". Click “Save & publish” at the bottom to push it to students."],
  "已发布（学生端可见）": ["已發布（學生端可見）", "Published (visible to students)"],
  "「保存并发布」后，学生端立即生效。": ["「儲存並發布」後，學生端立即生效。", "After “Save & publish”, students see it immediately."],
  "💾 保存并发布": ["💾 儲存並發布", "💾 Save & publish"],
  "以学生身份测试": ["以學生身分測試", "Test as a student"],
  "删除此人物": ["刪除此人物", "Delete this figure"],
  "还没有人物。": ["還沒有人物。", "No figures yet."],
  "已发布": ["已發布", "Published"],
  "未发布": ["未發布", "Draft"],
  "还没有史料，点下面按钮添加。": ["還沒有史料，點下面按鈕新增。", "No sources yet — add one below."],
  "还没有问题，点下面按钮添加。": ["還沒有問題，點下面按鈕新增。", "No questions yet — add one below."],
  "还没有抉择节点，点下面按钮添加。": ["還沒有抉擇節點，點下面按鈕新增。", "No decision tasks yet — add one below."],
  "拖拽排序": ["拖曳排序", "Drag to reorder"],
  "删除这份史料": ["刪除這份史料", "Delete this source"],
  "删除这个抉择": ["刪除這個抉擇", "Delete this decision task"],
  "删除选项": ["刪除選項", "Delete option"],
  "史料标题，如《出师表》": ["史料標題，如《出師表》", "Source title, e.g. a text or document"],
  "类型": ["類型", "Type"],
  "备注": ["備註", "Note"],
  "摘要 / 可对照原文（学生核对时看到）": ["摘要 / 可對照原文（學生核對時看到）", "Summary / quoted text (shown when students check)"],
  "填原文节选或要点": ["填原文節選或要點", "Paste a short quotation or the key point"],
  "如：核心一手史料": ["如：核心一手史料", "e.g. the key primary source"],
  "自定义…": ["自訂…", "Custom…"],
  "输入自定义类型": ["輸入自訂類型", "Type your own"],
  "一手": ["一手", "Primary"],
  "二手": ["二手", "Secondary"],
  "正史": ["正史", "Official history"],
  "文献": ["文獻", "Document"],
  "图像": ["圖像", "Image"],
  "考古": ["考古", "Archaeology"],
  "情境": ["情境", "Scenario"],
  "选项（可拖拽排序）": ["選項（可拖曳排序）", "Options (drag to reorder)"],
  "＋ 添加选项": ["＋ 新增選項", "＋ Add option"],
  "选项内容": ["選項內容", "Option text"],
  "提示（分级支架，最多 3 级，每行一级；越往下越具体，但始终不给答案）": ["提示（分級支架，最多 3 級，每行一級；越往下越具體，但始終不給答案）", "Hints (up to 3 levels, one per line; each is more specific, but never gives the answer)"],
  "抉择标题，如：街亭用人": ["抉擇標題，如：街亭用人", "Decision title"],
  "给学生描述这个历史抉择场景": ["給學生描述這個歷史抉擇場景", "Describe the scenario for the student"],
  "提示（可选）": ["提示（可選）", "Hint (optional)"],
  "给学生一点思考方向": ["給學生一點思考方向", "Give the student a direction to think about"],
  "如：丞相，您为何执意北伐？": ["如：丞相，您為何執意北伐？", "e.g. Why did you insist on the northern campaign?"],
  "给学生描述这个历史抉择场景": ["給學生描述這個歷史抉擇場景", "Describe the scenario"],
  "保存失败：": ["儲存失敗：", "Save failed: "],
  "删除失败：": ["刪除失敗：", "Delete failed: "],
  "⚠️ 请填写唯一 ID（英文）": ["⚠️ 請填寫唯一 ID（英文）", "⚠️ Enter a unique ID (English)"],
  "✅ 已保存并发布": ["✅ 已儲存並發布", "✅ Saved and published"],
  "有未保存的修改": ["有未儲存的修改", "Unsaved changes"],
  "· ● 未保存": ["· ● 未儲存", " · ● unsaved"],
  "确认删除该历史人物？此操作不可撤销。": ["確認刪除該歷史人物？此操作無法復原。", "Delete this figure? This cannot be undone."],
  "当前有未保存的修改，": ["當前有未儲存的修改，", "There are unsaved changes; "],
  "后将丢失。确定继续吗？": ["後將遺失。確定繼續嗎？", " will be lost. Continue?"],
  "切换人物": ["切換人物", "Switching figures"],
  "新建人物": ["新增人物", "Creating a new figure"],

  // ---- 学情分析 ----
  "汇总学生在「抉择任务」中的论证评分，观察历史思维各维度的整体表现与个体差异。": ["彙整學生在「抉擇任務」中的論證評分，觀察歷史思維各維度的整體表現與個體差異。", "Aggregated argument scores from decision tasks, across the five historical-thinking dimensions."],
  "历史思维画像（全体平均）": ["歷史思維畫像（全體平均）", "Historical-thinking profile (class average)"],
  "最近提交": ["最近提交", "Recent submissions"],
  "抉择提交": ["抉擇提交", "Decisions"],
  "史料核对": ["史料核對", "Source checks"],
  "历史人物": ["歷史人物", "Figures"],
  "最弱维度": ["最弱維度", "Weakest dimension"],
  "平均提示级数（": ["平均提示級數（", "Avg. hints used ("],
  "% 用过提示": ["% 用過提示", "% used hints"],
  "无数据": ["無資料", "no data"],
  "自评偏差（正=高估）": ["自評偏差（正=高估）", "Self-rating gap (+ = overconfident)"],
  "还没有学生提交。": ["還沒有學生提交。", "No submissions yet."],
  "全体最需要加强：": ["全體最需要加強：", "Class-wide focus: "],
  "暂无记录。": ["暫無記錄。", "No records yet."],
  "选择：": ["選擇：", "Choice: "],
  "编辑：": ["編輯：", "Editing: "],
  "用了 ": ["用了 ", "used "],
  " 级提示": [" 級提示", " hint(s)"],
  "指标说明与水平划分": ["指標說明與水平劃分", "What the indicators mean"],


  // ---- 指标说明正文（来自 /api/rubric） ----
  "你是否追问或说明一条说法的来源、作者是谁、有什么立场。": ["你是否追問或說明一條說法的來源、作者是誰、有什麼立場。", "Do you ask where a claim comes from — who said it, and what they stood to gain?"],
  "直接接受结论，不问出处。": ["直接接受結論，不問出處。", "Takes the conclusion as given, without asking where it came from."],
  "主动指出来源，并考虑作者的立场与时代。": ["主動指出來源，並考慮作者的立場與時代。", "Names the source, and weighs the author's position and period."],
  "你是否把决定放回当时的时间与条件下考虑，而不是用今天的标准去衡量。": ["你是否把決定放回當時的時間與條件下考慮，而不是用今天的標準去衡量。", "Do you judge the decision inside its own time and constraints, rather than by today's standards?"],
  "以今度古，忽略当时的处境。": ["以今度古，忽略當時的處境。", "Judges the past by present standards."],
  "结合当时的国力、地理、制度等约束来解释选择。": ["結合當時的國力、地理、制度等約束來解釋選擇。", "Explains the choice using the constraints of the day — power, geography, institutions."],
  "你是否用多于一份的来源互相比对，而不是只听一家之言。": ["你是否用多於一份的來源互相比對，而不是只聽一家之言。", "Do you compare more than one source, instead of trusting a single account?"],
  "只凭单一来源或单一印象下判断。": ["只憑單一來源或單一印象下判斷。", "Relies on one source, or on an impression."],
  "主动对照两份以上史料，并指出它们的异同。": ["主動對照兩份以上史料，並指出它們的異同。", "Sets two or more sources side by side, and notes where they agree or differ."],
  "你的结论是否有「论点—证据—推理」的完整链条。": ["你的結論是否有「論點—證據—推理」的完整鏈條。", "Does your conclusion have a complete chain: claim — evidence — reasoning?"],
  "只给结论，或只有一句简单理由。": ["只給結論，或只有一句簡單理由。", "States a conclusion, or gives one bare reason."],
  "论点明确，引用具体证据，并说明证据如何支持结论。": ["論點明確，引用具體證據，並說明證據如何支持結論。", "States the claim, cites specific evidence, and explains how it supports the claim."],
  "你是否能理解当时人为什么会那样选择（理解不等于认同）。": ["你是否能理解當時人為什麼會那樣選擇（理解不等於認同）。", "Can you explain why people then acted as they did? (Understanding is not agreement.)"],
  "用现在的是非直接评判古人。": ["用現在的是非直接評判古人。", "Judges people of the past directly by today's right and wrong."],
  "能说出当时人的处境与限制，并据此解释其动机。": ["能說出當時人的處境與限制，並據此解釋其動機。", "Describes the constraints people faced, and explains their motives from there."],

  // ---- 快捷追问 ----
  "你的依据是什么？": ["你的依據是什麼？", "What's your evidence?"],
  "还有别的说法吗？": ["還有別的說法嗎？", "Are there other accounts?"],
  "当时的人会怎么看？": ["當時的人會怎麼看？", "How would people then have seen it?"],
  "你确定吗？": ["你確定嗎？", "Are you sure?"],

  // ---- 动态句式（用「模式」处理，见下） ----
  "调用失败：": ["呼叫失敗：", "Request failed: "],
  "核对失败：": ["核對失敗：", "Check failed: "],
  "提交失败：": ["提交失敗：", "Submit failed: "],
  "加载失败：": ["載入失敗：", "Load failed: "],
  "找不到该人物：": ["找不到該人物：", "Figure not found: "],
  "抉择": ["抉擇", "Decision"],
};

const PREFIX_KEYS = [
  "全体最需要加强：", "最需要加强：", "找不到该人物：", "元认知提示：",
  "你的判断：", "总分", "API：",
  "保存失败：", "删除失败：", "提交失败：", "调用失败：", "加载失败：",
  "核对失败：", "选择：", "编辑：", "抉择：",
];

const PATTERNS = [
  [/^抉择\s*(\d+)\s*次\s*·\s*核对\s*(\d+)\s*次$/, (m, L) =>
    L === "en" ? `${m[1]} decision(s) · ${m[2]} check(s)`
      : L === "tw" ? `抉擇 ${m[1]} 次 · 核對 ${m[2]} 次` : m[0]],
  [/^已完成\s*(\d+)\s*次抉择论证$/, (m, L) =>
    L === "en" ? `${m[1]} decision argument(s) completed`
      : L === "tw" ? `已完成 ${m[1]} 次抉擇論證` : m[0]],
  [/^用了\s*(\d+)\s*级提示$/, (m, L) =>
    L === "en" ? `used ${m[1]} hint(s)` : L === "tw" ? `用了 ${m[1]} 級提示` : m[0]],
  [/^整体高估了约\s*([\d.]+)\s*分。$/, (m, L) =>
    L === "en" ? `you over-rated yourself by about ${m[1]}.`
      : L === "tw" ? `你整體高估了約 ${m[1]} 分。` : m[0]],
  [/^整体低估了约\s*([\d.]+)\s*分。$/, (m, L) =>
    L === "en" ? `you under-rated yourself by about ${m[1]}.`
      : L === "tw" ? `你整體低估了約 ${m[1]} 分。` : m[0]],
  [/^请先完成自评（还差\s*(\d+)\s*项）$/, (m, L) =>
    L === "en" ? `Finish your self-assessment (${m[1]} left)`
      : L === "tw" ? `請先完成自評（還差 ${m[1]} 項）` : m[0]],
  [/^元认知提示：你整体高估了约\s*([\d.]+)\s*分。$/, (m, L) =>
    L === "en" ? `Metacognition: you over-rated yourself by about ${m[1]}.`
      : L === "tw" ? `元認知提示：你整體高估了約 ${m[1]} 分。` : m[0]],
  [/^元认知提示：你整体低估了约\s*([\d.]+)\s*分。$/, (m, L) =>
    L === "en" ? `Metacognition: you under-rated yourself by about ${m[1]}.`
      : L === "tw" ? `元認知提示：你整體低估了約 ${m[1]} 分。` : m[0]],
  [/^自评偏差：整体(高估|低估)约\s*([\d.]+)\s*分$/, (m, L) =>
    L === "en" ? `Self-rating gap: ${m[1] === "高估" ? "over" : "under"}-rated by ${m[2]}`
      : L === "tw" ? `自評偏差：整體${m[1]}約 ${m[2]} 分` : m[0]],
  [/^一致性\s*(高|中|低)$/, (m, L) =>
    L === "en" ? `agreement: ${{ "高": "high", "中": "medium", "低": "low" }[m[1]]}` : m[0]],
  [/^(\d+)\s*个选项$/, (m, L) =>
    L === "en" ? `${m[1]} option(s)` : L === "tw" ? `${m[1]} 個選項` : m[0]],
  [/^平均提示级数（(\d+)% 用过提示）$/, (m, L) =>
    L === "en" ? `Avg. hints used (${m[1]}% used hints)`
      : L === "tw" ? `平均提示級數（${m[1]}% 用過提示）` : m[0]],
  [/^平均提示级数（无数据）$/, (m, L) =>
    L === "en" ? "Avg. hints used (no data)"
      : L === "tw" ? "平均提示級數（無資料）" : m[0]],
];

const LS_KEY = "hs_lang";
let LANG = localStorage.getItem(LS_KEY) || "zh";

const ORIGINALS = new WeakMap();   // Text 节点 -> 原文
const ATTR_ORIG = new WeakMap();   // 元素 -> {attr: 原文}
const SKIP = "[data-no-i18n]";
const OBS_OPTS = { childList: true, subtree: true, characterData: true };

function value(zh) {
  const hit = DICT[zh];
  if (!hit) return zh;                       // 词条缺失就原样返回，绝不抛错
  return LANG === "tw" ? hit[0] : LANG === "en" ? hit[1] : zh;
}

function translateKey(zh) {
  if (DICT[zh]) return value(zh);
  if (LANG === "zh") return zh;
  // 1) 整句模式优先（带数字的动态句式）
  for (const [re, fn] of PATTERNS) {
    const m = zh.match(re);
    if (m) return fn(m, LANG);
  }
  // 2) 再退到「前缀 + 内容」：只翻前缀，保留教师/学生自己的文字
  for (const pre of PREFIX_KEYS) {
    if (zh.length > pre.length && zh.startsWith(pre)) {
      return value(pre) + zh.slice(pre.length);
    }
  }
  return zh;
}

function walkText(node) {
  const parent = node.parentElement;
  if (!parent || (parent.closest && parent.closest(SKIP))) return;

  const raw = node.nodeValue;
  let original = ORIGINALS.get(node);
  if (original === undefined) { original = raw.trim(); ORIGINALS.set(node, original); }
  if (!original) return;

  const key = original.replace(/\s+/g, " ");
  const out = DICT[original] ? translateKey(original)
    : DICT[key] ? translateKey(key)
      : translateKey(original);
  const next = raw.replace(raw.trim(), out);
  if (next !== raw) node.nodeValue = next;    // 只在真的变了才写，避免自我触发
}

function walkAttrs(node) {
  if (!node.hasAttribute) return;
  let store = ATTR_ORIG.get(node);
  if (!store) { store = {}; ATTR_ORIG.set(node, store); }
  for (const attr of ["placeholder", "title", "aria-label", "data-tip"]) {
    if (!node.hasAttribute(attr)) continue;
    if (store[attr] === undefined) store[attr] = (node.getAttribute(attr) || "").trim();
    const out = translateKey(store[attr]);
    if (node.getAttribute(attr) !== out) node.setAttribute(attr, out);
  }
}

function walk(node) {
  try {
    if (node.nodeType === 3) return walkText(node);
    if (node.nodeType !== 1) return;
    if (node.matches && node.matches(SKIP)) return;
    walkAttrs(node);
    if (node.childNodes) {
      for (let i = 0; i < node.childNodes.length; i += 1) walk(node.childNodes[i]);
    }
  } catch (err) {
    // 单个节点失败不影响其余部分
    if (globalThis.console) console.warn("[i18n] skipped node:", err);
  }
}

let TITLE_ORIGINAL = null;

export function applyI18n() {
  if (TITLE_ORIGINAL === null) TITLE_ORIGINAL = document.title;
  if (TITLE_ORIGINAL) document.title = translateKey(TITLE_ORIGINAL.trim());
  if (document.body) walk(document.body);
  document.documentElement.lang =
    LANG === "en" ? "en" : LANG === "tw" ? "zh-Hant" : "zh-Hans";
}

export function currentLang() { return LANG; }

export function setLang(lang) {
  LANG = lang;
  localStorage.setItem(LS_KEY, lang);
  runPass();                                  // 立即生效，不等 observer
  // 通知页面：动态拼出来的文案（如 API 摘要）需要按新语言重算
  try { document.dispatchEvent(new CustomEvent("i18n:changed")); } catch (e) { /* ignore */ }
}

function mountSwitcher() {
  if (document.querySelector(".lang-switch")) return;
  const bar = document.querySelector(".topbar");
  if (!bar) return;
  const box = document.createElement("div");
  box.className = "lang-switch";
  box.innerHTML = `<select aria-label="Language">
      <option value="zh">简体中文</option>
      <option value="tw">繁體中文</option>
      <option value="en">English</option>
    </select>`;
  bar.appendChild(box);
  const sel = box.querySelector("select");
  sel.value = LANG;
  sel.addEventListener("change", () => setLang(sel.value));
}

let mo = null;
let scheduled = false;

function observe() {
  if (mo && document.body) mo.observe(document.body, OBS_OPTS);
}

// 翻译期间先断开 observer，翻完再挂上：避免"写入 → 触发 → 再写入"的自激循环
function runPass() {
  if (mo) mo.disconnect();
  applyI18n();
  observe();
}

function schedule() {
  if (scheduled) return;
  scheduled = true;
  const run = () => { scheduled = false; runPass(); };
  if (typeof globalThis.requestAnimationFrame === "function") {
    globalThis.requestAnimationFrame(run);
  } else {
    setTimeout(run, 30);
  }
}

function boot() {
  mountSwitcher();
  runPass();
  mo = new MutationObserver(schedule);
  observe();
  if (typeof globalThis.addEventListener === "function") {
    globalThis.addEventListener("load", schedule);
  }
  globalThis.applyI18n = applyI18n;   // 页面渲染完可主动调用，双保险
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
else boot();
