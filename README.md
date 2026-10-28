# REITs Investment Lab

中文、模拟数据的五年权益投资分析工具。单一产权类商业物业、无债务、平层结构、全部权益归投资人；年度末现金流，无额外初始交易费用，无固定还本付息或担保收益机制。

## Mac 首次启动

1. 安装 Python 3.11 或 3.12：访问 https://www.python.org/downloads/macos/ 下载并打开安装包，按提示完成安装。
2. 使用随附本地项目文件夹，或解压交付的 ZIP。代码同步到 GitHub 后，也可在仓库页面点击 Code → Download ZIP。
3. 按 Command + 空格，输入“终端”，回车。
4. 输入 `cd `（后面有空格），把解压后的项目文件夹拖进终端，然后回车。
5. 依次复制下列命令，每行回车并等上一行结束：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

浏览器会打开工具；若没有自动打开，访问 http://localhost:8501 。修改表单后点击“计算收益与估值”。按 Control + C 停止服务。

以后启动：重新打开终端，按第4步进入项目目录，再执行：

```sh
source .venv/bin/activate
python -m streamlit run app.py
```

运行测试：进入同一目录并激活环境后执行 `python -m pytest -q`。若出现 module not found，请确认激活环境并重新安装依赖。若端口占用，使用 `python -m streamlit run app.py --server.port 8502`。

## 口径与复算

金额均为万元，输入界面利率用百分数，model.py 参数使用小数。持有5年，第6年NOI单独输入，仅用于退出估值。资本开支、其他税费仅填写尚未从NOI扣除的项目。

- 年度分派 = NOI − 资本开支 − 其他税费及费用，100%当年分派，无留存。
- 年度分派率 = 分派 / 初始买入成本。
- 退出价值 = 第6年NOI / 退出Cap Rate；净回收 = 退出价值 × (1 − 处置费用率)。
- 第5年投资人现金流 = 当年分派 + 退出净回收。
- IRR采用第0年负投资及第1至5年投资人现金流。
- 最高允许总投入 = 未来现金流按目标IRR折现的现值。

基准：成本1000，年NOI60、资本开支10、其他费用10，第6年NOI60，退出Cap Rate 6%，处置费率2%，目标IRR5%。现金流为 [-1000,40,40,40,40,1020]，分派率4%，IRR为3.6279901564%，最高允许总投入941.0347099643万元。原期望值3.628%及941.03万元均正确。

负可分配现金作为投资人补资处理。现金流无正负变化或多次变化时不展示单一IRR，保留现金流与现值并明确提示。本工具只用于模拟分析，不包含真实项目数据或外部密钥服务。

## 文件

- model.py：独立计算及校验
- app.py：中文输入、指标、现金流、退出Cap Rate敏感性
- data/sample_case.json：模拟基准
- tests/test_model.py：财务逻辑和界面启动测试
- requirements.txt：依赖
- .gitignore：排除虚拟环境、缓存和本地敏感文件
