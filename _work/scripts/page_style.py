"""page_style.py -- 清单页与词汇表页共用的字体与基础样式。

界面与注释（简体）用 Noto Serif SC / Noto Sans SC；引用的 CBETA 原文与玄奘译语（繁体）用 Noto Serif TC，
字形合于繁体规范；梵文转写用 Gentium Book Plus（变音符号完备）。各字体栈都把 Gentium 放在最前，
夹在中文里的梵文转写（如注释中的 kleśa）也用它显示，汉字自动落到中文字体上。
"""

_FONT_CSS = ('https://fonts.googleapis.com/css2?'
             'family=Gentium+Book+Plus:ital,wght@0,400;0,700;1,400;1,700'
             '&family=Noto+Serif+SC:wght@400;600;700&family=Noto+Serif+TC:wght@400;600'
             '&family=Noto+Sans+SC:wght@400;500;700&display=swap')
# 异步加载字体样式表（media=print 再切换），不阻塞页面脚本；字体到达前先用系统字体显示
FONT_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link rel="stylesheet" href="%s" media="print" onload="this.media=\'all\'">'
             '<noscript><link rel="stylesheet" href="%s"></noscript>' % (_FONT_CSS, _FONT_CSS))

# 离线资料包：字体随包附带（由 pkg_fonts.py 生成 fonts/fonts.css）
LOCAL_FONT_LINK = '<link rel="stylesheet" href="fonts/fonts.css">'

BASE_CSS = r'''
:root{
  --bg:#f7f3ea;--paper:#fffdf8;--ink:#2b2621;--mut:#7b7265;--line:#e5ddcd;--soft:#efe8d9;
  --acc:#a23b2a;--acc-soft:rgba(162,59,42,.10);--ok:#3d7a4a;--warn:#a86b12;
  --serif:"Gentium Book Plus","Noto Serif SC","Source Han Serif SC","Songti SC",serif;
  --zh:"Gentium Book Plus","Noto Serif SC","Source Han Serif SC","Songti SC",serif;
  --zht:"Gentium Book Plus","Noto Serif TC","Source Han Serif TC","Noto Serif SC","Songti TC",serif;
  --sans:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#1a1815;--paper:#22201c;--ink:#ece5d8;--mut:#a69d8f;--line:#38332c;--soft:#2a2722;
  --acc:#e3866d;--acc-soft:rgba(227,134,109,.16);--ok:#7fbf8c;--warn:#e0b060}}
:root[data-theme="dark"]{
  --bg:#1a1815;--paper:#22201c;--ink:#ece5d8;--mut:#a69d8f;--line:#38332c;--soft:#2a2722;
  --acc:#e3866d;--acc-soft:rgba(227,134,109,.16);--ok:#7fbf8c;--warn:#e0b060}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--serif);font-size:17px;line-height:1.75;
  font-kerning:normal;text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}
main{max-width:1120px;margin:0 auto;padding:40px 16px 96px}
header.top{border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:20px}
.kicker{font-family:var(--sans);font-size:12.5px;letter-spacing:.14em;color:var(--acc);font-weight:500;margin:0 0 6px}
h1{font-family:var(--zh);font-weight:700;font-size:32px;line-height:1.3;letter-spacing:.04em;margin:0 0 10px}
.lead{font-family:var(--zh);color:var(--mut);font-size:15.5px;line-height:1.85;margin:0;max-width:46em}
.bar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:10px;align-items:center;
  padding:12px 0;margin:0 0 16px;background:color-mix(in srgb,var(--bg) 88%,transparent);
  backdrop-filter:saturate(1.2) blur(6px);-webkit-backdrop-filter:saturate(1.2) blur(6px);border-bottom:1px solid var(--line)}
input[type=search]{flex:1 1 240px;min-width:0;font:15px/1.4 var(--sans);color:var(--ink);background:var(--paper);
  border:1px solid var(--line);border-radius:8px;padding:9px 12px;outline:none}
input[type=search]:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:var(--paper)}
.seg button{font:500 13.5px/1 var(--sans);color:var(--mut);background:none;border:0;padding:10px 14px;cursor:pointer;letter-spacing:.04em}
.seg button+button{border-left:1px solid var(--line)}
.seg button.on{color:var(--acc);background:var(--acc-soft)}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline;text-underline-offset:3px}
.sk{font-family:var(--serif)}
.zh{font-family:var(--zh);letter-spacing:.02em}
.zht{font-family:var(--zht);letter-spacing:.03em}
.small{font-family:var(--sans);font-size:12.5px;color:var(--mut);letter-spacing:.02em}
@media (max-width:640px){body{font-size:16px}h1{font-size:26px}main{padding-top:28px}}
'''
