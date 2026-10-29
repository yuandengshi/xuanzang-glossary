# 界品 U06–U54 分批编写记录

由 7 个子代理并行编写，每批完成后由主会话独立重跑核验（akbh1_verify.py）与体例自查（akbh1_lint.py）。以下是各批汇报的疑点摘要，合并后整理进《待核清单》。

## G：U50–U54（颂 1.44cd–1.48）

- 实例 799 条（U50 141、U51 67、U52 204、U53 221、U54 166）。独立复核：错误 0，ERROR 0，WARN 12。
- 保留的 WARN：samanantara → 無間（词义本身）；U52-071 āhosvit → 不（选择问"為同不"）；U53-192 -artham 复合词作"為…故"。
- 单位与对位：U50 起于 0012b03 行中；S1053 玄奘置于 U52 长行（0012b27）；S1108、S1112 玄奘移前至 0012a12，与 S1102 合为一句（合译）。
- **GRETIL 缺文**：S1063 缺"若以初靜慮眼…身色欲界、眼識初定"与"身屬欲界"，两汉译都有。暂记为增译并注"非玄奘增译"（U52-091、U52-097、U52-098）——合并时改为专门的类型。
- 玄奘增出值得注意的：後三一分意意識攝（S1120）、餘界亦應如是分別（S1072）、如是所說二十二根…法一分攝（S1118）、設是…耶（S1038）、謂眼等五是別所依…（S1037）。
- 影响词义的 GRETIL 误读：S1054 dhi 当作 ca（玄奘"及"）；S1116 ādṛtya 当作 anādṛtya（玄奘"越"、真谛"破"）。其余误字均在 note 注出正读。
- 待核：U50-042、U50-119、U52-002、U52-039、U52-097、U53-152、U54-060、U54-117。
- 主会话抽查发现：U54-054 dharmā → 法界（"界"为补出），应拆为 法 + 增译"界"。

## C：U26–U33（颂 1.22cd–1.30a）

- 实例 1,444 条（U26 229、U27 185、U28 163、U29 45、U30 98、U31 194、U32 135、U33 395）。独立复核：错误 0，ERROR 0，WARN 15（均为词本身含否定：ārūpya→無色、ānantya→無邊、naivasaṃjñānāsaṃjñāyatana→非想非非想處、akuśala→不善 等）。
- 子代理问：pūrvam、anya、sva、ubhayatra 是否限两例。主会话决定按实词处理、每次出现都收（有实在词义，译法有变化，如 anya → 餘/異/別/他），与裁剪脚本的虚词表一致。
- 跨单位译出：S0449 末句玄奘译在 U27（0005c24）；S0513 末玄奘译在 U32（0006c09）。卷二开头总问（0007a07–08）合 S0529、S0532、S0570 三问。S0466 结语玄奘提前到 0006a05。
- **GRETIL 缺文**（两汉译都有）：S0586 缺"無色界繫"一问；U26 想、行、識"易了知""難分別"的理由；S0460"撞擊鍾鼓"一例。暂记为增译——合并时改为"梵本缺文"类型。
- 只有玄奘有的增出：S0480 法處一段；S0496"如是餘處諸蘊處界類亦應然"；S0508"四蘊性故"；S0528 结语"彼經餘界…"。
- 影响词义的 GRETIL 误读：S0447 bhājana- 当作 bhojana-（玄奘"類食同助"）；S0520 cittastha 当作 citastha（積集）；S0452 vyadhvānadhra- 当作 tryadhvānadhva-；S0465 takyāḥ syāsya 当作 kāyasya；S0472 tadrūpakayātanaṃ 当作 tad rūpāyatanaṃ；S0450 vārttamārthyāt 当作 vārtamānārthyāt；S0438、S0512 "aca"当作 ca。另真谛本"界陰"当作"戒陰"。
- 待核 11 条：U26-092（煩惱依識而生，所据梵本或作 kleśāś cittāt）、U27-026、U27-064/072/114（āśutara 两家都多"明"字）、U27-067、U28-024、U28-051、U30-097、U33-056、U33-111（titīla，两家作"蝙蝠"）。
- 主会话抽查：U33-122 rātrau divā ca → 俱，宜记为合译。

## E：U41–U45（颂 1.37–1.40）

- 实例 1,044 条（U41 332、U42 128、U43 126、U44 330、U45 128），批内已按两例裁剪（去掉 83 条）。独立复核：错误 0，ERROR 0，WARN 11（词本身含否定或意译：abhāva→無、ārūpya→無色、a-vihīna→不失、nanu→豈不 等）。
- 子代理自加虚词 kati、yāvat、nanu、api tu、evaṃ tarhi、kiṃcit；主会话已补进 akbh1_prune.py 的虚词表。
- 跨单位：S0773–S0775 引出 1.38cd 的问句在 U41，āha → 頌曰 在 U42 的行（0009b27）；S0812、S0856 问句对应行在 U43 文本中；S0856 句末 rūpiṇas tāvat 对应 U45 的"十色界"（0010b17）。
- 玄奘调整次序：U45 长行 S0870 的 rūpaṃ kāyavākkarma 移到 0010b29；S0871、S0875 两处结论合为"前及此色，定非見斷"（合译）。0010a07"已正當生"的"正"为增译（梵本只有两时，真谛同）。
- 真谛的问题：S0836 真谛"於一切人非等分"与梵本、玄奘意思相反；S0799 svarga 真谛作"解脫"。
- Pradhan 页行号异常：S0773（026|12-025|12）、S0800（027|09-026|09）、S0817（027|14-027|25）；S0838 页行编号误入句文。
- 影响词义的 GRETIL 误读：S0827 yad dṛṣṭvā 当作 yad adṛṣṭvā（玄奘、真谛"不見"）；S0824 acakṣuḥ 当作 cakṣuḥ；S0761 sañābhāvāt 当作 saṃcayābhāvāt；S0770 anyasaṃbhūtasaṃskṛto 疑作 anyaḥ saṃbhūtaḥ saṃskṛto。另有误字三十余处，均在 note 注出正读。
- 待核：U41 S0773 idaṃ → 今；U44 S0848 evam → 理。
- 主会话抽查：U44-250 gandhādayas → 香味觸三（"三"为增字，应另记）；U43-051 sādhu → 應善（"應"待核）。

## F：U46–U49（颂 1.41–1.44ab）

- 实例 1,156 条（U46 595、U47 63、U48 310、U49 188）。独立复核：错误 0，ERROR 0，WARN 10（复合词成分本身含否定：samegha-amegha→有雲無雲、kliṣṭa-akliṣṭa→有染無染、bheda→不同 等）。
- kadācit → 有時 原有 10 例，子代理按虚词留 2 例；主会话同意（与 kaścit 同属不定代词一系），已补进虚词表。
- 新语法形式词目：-sya (gen.)、-e (loc.)、-e (loc. abs.)、-et (opt.)、-tu (impv.)、-ya- (pass.)、-āya (dat.)、-tavya (gdv.)、-tara (comp.)、-tvā (abs.)、-ti (act.)（S0940 能/所对举）。主会话已在缩略语表补 impv.、act.；合并时 comp. 统一为 compar.。
- 跨单位：S1000（U48）对应 0012a05"前說至境鼻等三根"（U49 的行）。
- Pradhan 页行号异常：S0937（030|10）、S0974（031|13）、S0965（03207）；S1031 页行编号误入句文。
- **两汉译都有、梵本没有的内容**（疑所据梵本多文，均标待核）：以無分別（S0888）、是故不由（S0907）、S0915 后的结句、共聚（S0939）、假立（S0992）、橫作行度…無高下（S1015）。合并时改为"梵本缺文"类型。
- 譬喻或措辞不同（待核）：śalākāvat → 雙爪甲（S1014）；S0953 → 閉一觸一此事則無；ardhanimīlita 玄奘作"觸"，真谛作"半閉"（S0952）。
- S0928 CBETA 标点"然無了者。了用不同"疑应连读（待核）。
- 疑有讹脱（待核）：ghoṣam（S1006，或作 yojyam）、bhūrjābhyantarāvasthitāḥ（S1013）、ghaṭābhyantareṇa（S1014）。其余误字四十余处均在 note 注出正读。
- 待核 16 条：U46-129、199、200、268、292、342、435、444、523；U47-035；U49-044、045、082、087、089、093。

## B：U14–U25（颂 1.14–1.22ab）

- 实例 1,337 条（U14 68、U15 205、U16 109、U17 46、U18 83、U19 94、U20 46、U21 49、U22 411、U23 70、U24 71、U25 85）。独立复核：错误 0，ERROR 0，WARN 15（nanu → 豈不、samanantara → 無間、-artham 复合词作"…故"、vairūpya → 不端嚴 等）。
- 子代理问：独立式立目 -ya (abs.) 与样本 -tya (abs.)、F 批 -tvā (abs.) 是否统一。主会话决定按语法范畴统一为 `-tvā/-ya (abs.)`；动形容词统一为 `-ya/-tavya/-anīya (gdv.)`。合并时改。
- 跨单位：S0273（U13）玄奘译在 U14 的行（0003c22–23），未收，留待 A 批或合并时处理；S0403 末 vineyānāṃ 玄奘译在 U23 的行（0005b04），记在 U22。
- **梵本缺文**：S0353 之后玄奘 0004c07–c11"此釋不然。若本來爾……是故三根各生二處"，真谛 0165a17–a21 也有，GRETIL 无。子代理未收——合并时补一条"梵本缺文"记录。U24 0005b17"何故無為說在處界，非蘊攝耶"真谛也有，疑梵本脱。
- 无梵文对应的承上启下语（增译）：U15 0004a17"已說受等三蘊處界，當說識蘊并立處界"；U20 0004c03"若爾，何緣生依二處"；U25 0005b28"當說次第"。
- S0382 GRETIL 疑脱 ākaratvāt 一类词（玄奘"生之本故"、真谛"同類因故"），待核。
- 误字与误分写数十处，均在 note 注出正读；S0279、S0398 有混入的页行标记。
- 待核：S0281/S0282 增译"隨觸"；S0285 yāvat；S0295 增译"未滅"；S0309 atho → 轉為；S0382 两条；S0389 deyaṃ → 還；S0398 vā → 若不爾者；S0418 tredho（GRETIL 疑讹）。

## D：U34–U40（颂 1.30b–1.36）

- 实例 1,261 条（U34 416、U35 40、U36 154、U37 88、U38 144、U39 292、U40 127）。独立复核：错误 0，ERROR 0，WARN 16（ālambana-abhāva → 無所緣、niṣ-prayojana → 無用、ārūpya → 無色、itarathā → 若不許然、ucchedin → 不相續 等）。
- anya → 餘 留 3 例：按实词处理，与 C 批的决定一致。
- 跨单位：S0632（U34 末）实为下颂 1.31b 的引语，玄奘未译，记为省译；问句 S0675、S0715 玄奘提前，译在前一单位的行（0008b10、0008b28–29）。
- 玄奘（多数真谛也）有、梵本无的句子，记为增译：0007b28"欲界所繫具足十八"；0007c22"男根非有，鼻舌應無"（真谛不同，疑底本不同）；0008a13"以行相麁外門轉故"；0008a14"根、境、識中各居後故"（真谛有类似句）——合并时，两汉译都有的改为"梵本缺文"。
- GRETIL 页行标记本身有误：S0672 [023|04-021|04]、S0681 [023|13-013|13]、S0698 [024|01-023|01]（已在原文件中查实）。
- 误字约 45 处均在 note 注出正读；S0607"vinā'; śraya"一段乱码。S0276 nivarttate 疑当读 nirvartate。
- 待核 15 条：U34-007、008、078、104、105、143、150、261、263、276；U38-045、092；U40-024、027、076。
- 主会话抽查：U34-384"意、法及意識界"（"及"为补出）、U39-247 yathoktaṃ →"如前所說"（"前"为补出）——增字算进了译语，合并后统一处理。

## A：U06–U13（颂 1.7–1.13）

- 实例 1,518 条（U06 152、U07 124、U08 52、U09 93、U10 528、U11 108、U12 139、U13 322）。独立复核：错误 0，ERROR 0，WARN 12（an-upātta → 無執受、a-sattva → 非有情、a-śubha → 不淨、a-kuśala → 不善 等）。
- yathākramam、anya、apara 按实词处理，与 C、D 批一致。
- 跨单位：S0129（U08）后半句玄奘移到 0002b13；S0273（U13 末）玄奘译在 0003c23（U14 的行）；S0205 seyam ucyate 对 0003a15"頌曰"；S0222 问"何为自性"玄奘挪到答完"業"之后（0003b07）；S0236 整句玄奘概括为"水火亦然"，各词记为省译。
- S0234 颂 1.13ab 与长行并在一句（夹 [009|02]）；S0215 页行栏空，正文混入"[008|09-008|09"。
- **GRETIL 脱文**：S0094 缺 saṃjñāskandhaḥ；S0184 缺 pipāsā pānābhilāṣakṛt（玄奘、真谛都有"飲欲／飲愛為渴"）。
- **两汉译都有、梵本无**（合并时改为"梵本缺文"）：觸動善品故（S0118）、有對治故（S0121）、電（S0147）、或起種種大事用故（S0221）、生等五種因的"五"（S0212）。只有玄奘有：障光明生（S0148）。
- GRETIL 误字若干，均在 note 注出正读；S0098 vāvāyam 当读 vākyam；lakṣyata 玄奘、真谛所据当为 lujyata（lemma 立 luj）。
- 待核 7 条：U06-093、U06-099、U07-079、U10-041（vṛtta → 方）、U10-088、U12-115、U13-127（rūpeṇa，所据或为 rūpaṇam）。

# 形态标注（2026-10-29，全部标注）

## D：U34–U40

- 标注 808 条（含 occ_extra），拒绝 0、找不到 0；自查无形态 ERROR。
- 自定做法：复合词末一成分带词尾的（dhātubhiḥ、āptāḥ）标整个复合词的格数（如 n. instr. pl.），非末位成分标"成分"——与规则"成分一律标成分"不同，合并时统一。
- -vat 复合词整体标 cpd. ind.；kati 标 pron. interrog. nom. pl.；作"何故"的 kiṃ 标 pron. acc. sg.。
- (?) 4 条：U39-152/153（GRETIL 重复 catvāri mahābhūtāni）、U39-170 spaṣṭam、U40-094 dagdhṛtulyayoḥ。
- 数据问题：U40-063 skt andhatvāt 与 lemma accha-tva 不符（GRETIL 讹，U40-084 作 acchatvān）；U34-073/074 tatrabhāva 当作 tatrābhāva；U40-005 dhātue 当作 dhātucatuṣṭayam；U39-080、U39-242 GRETIL 误分写；U38-029 isiddham = iti siddham；U39-117 arupy 拼写讹；U35-017 saṃgṛhīta → 是，对齐可疑。

## E：U41–U45

- 标注 659 条（U41 214、U42 77、U43 78、U44 201、U45 89），拒绝 0、找不到 0；自查无形态 ERROR。
- 复合词末成分一律标"成分"（按规则）；与 D 批相反，合并时统一。原本合规、未在待标清单中的末成分带格记录：U42-004、U42-026、U42-106、U44-039、U44-213、U44-297。
- -vat：cpd. 成分 (-vat)、n. 成分 (-vat)。kiṃ kāraṇam 标 pron. + n. nom. sg.；uktaṃ bhavati 标 ptc. nom. sg. + bhū (v. pres. 3sg.)。
- (?) 3 条：U41-294/295（anyasaṃbhūtasaṃskṛto 拆读）、U42-075（cakṣurvijñānāsaṃmukhīkurvāṇaḥ）。
- 数据问题：U41-280/281 prathamānāsrave 应为复合词 prathama-anāsrava（loc. sg.），缺复合词整体记录；U44-314 skt "te teṣā" 跨两词；U45-118 jaṃ 为 pañcendriyajaṃ 的 -ja 成分（提醒）。

## F：U46–U49

- 标注 673 条（U46 349、U47 34、U48 187、U49 103），拒绝 0、找不到 0；自查无形态 ERROR。
- 自定做法：复合词末成分标整个复合词的格数（同 D，与 E 相反），合并时统一。-vat 前的词干标 n./cpd. 成分 (-vat)（17 条）。kim、anyonyam 作副词或疑问小品词时标 pron. acc. sg.。致使式被动 kalpyate、saṃpradhāryate 标 v. pres. pass. caus. 3sg.。
- (?) 4 条：U46-490 cakṣuḥ（应为复合词 cakṣuḥ-saṃprāpta 的成分，GRETIL 分写）、U48-149/152（skt 含同一词目的两个形式）、U49-044 ghoṣam。
- 数据问题：U46-490/491 应合为 cakṣus-saṃprāpta；U48-149、U48-152 一条记录涵盖两个词形，宜拆开；kiṃ kāraṇam 或宜标 phr.；U46-100 skt 缺连声前的 -ā。

## G：U01–U05、U50–U54

- 标注 894 条，拒绝 0、找不到 0；自查无形态 ERROR（含 occ_extra）。
- 自定做法：复合词末成分标整个复合词的格数（同 D、F），合并时统一。kim 作疑问小品词标 pron. acc. sg.；uktaṃ bhavati 标 ptc. nom. sg. + bhū (v. pres. 3sg.)；-vat 前词干标"成分"，dānavargīyakaraṇavad 整词标 cpd. ind.；vicāryate 标 v. pres. pass. caus. 3sg.；sādhīyas 作副词标 adj. acc. sg. (compar.)。
- 改了词类 1 条：U05-095 sākṣātk 由 v. 改为 n. abl. sg. (sākṣātkaraṇa)（样本中的记录；词目仍作 sākṣāt-kṛ，合并时改为名词词目）。
- (?) 1 条：U52-097 rūpāṇi（GRETIL 讹脱）。
- 数据问题：U05-160 vākyasyārtho 实为两个词（vākyasya + arthaḥ），不是复合词；U04-012、U04-024 śāstrā 为 instr. sg.；U04-041 bhadanta 标成分；xz 为空的 U03-024、U50-007、U50-055、U50-092、U53-015 均为省译（有意）。

## C：U26–U33

- 标注 867 条（含 occ_extra），拒绝 0、找不到 0；自查无形态 ERROR。
- 自定做法：复合词末成分标整个复合词的格数（同 D、F、G）；-tva/-tā 前的词干标 adj. 成分；不变格复合词内的名词标成分；lemma 本身是大复合词中的小复合词（kāma-guṇa 等）标 cpd. 成分；kim 作疑问小词标 pron. acc. sg.（U28-149、U31-175），作谓语标 pron. nom. sg.；"A + B"式两边都补形态（U27-164、U33-015）；note 有校读的按校读标（U31-114）。
- (?) 1 条：U27-128 jihvā——note 校读为 jihvām（acc.），但玄奘"舌後甞味"以舌为主语，似 nom.。
- 改词类：无。
- 数据问题：U32-100/U32-102 原文连写 cyuticittasādhāraṇabhūtāḥ，cyuti-citta 是成分还是另读 cyuticittam 待核；U26-094 tatsaṃkliṣṭam 的 tad 标 pron. nom. sg.（GRETIL 有讹"aca"）；U33-045/U33-048 sva→他、para→自，是玄奘换视角，不是错。
- 并发：U31 套用时报过一次 KeyError: 'oid'（读到别组写到一半的文件），重跑后确认已写全。

## A：U06–U13

- 标注 977 条（含 occ_extra），拒绝 0、找不到 0；自查无形态 ERROR。
- (?)：0。较可疑：U11-043 kuśalākuśale 取 loc. sg.（不取 du.）；U10-513 saṃtateḥ 取 gen.；U06-055 adhvā 形为 nom. sg.、义为复数。
- 改词类：无。
- 自定做法：复合词末成分一律标"成分"（与 D、F、G、C 不同）；原带格、被改成成分的 23 条：U06-074、093；U07-071；U10-174、202、286、356、491；U11-003、021、030、067；U12-015；U13-009、085、167、173、184、192、202、209、261、316。本来就合规、末成分带格未动的：U09-019、U10-083、U10-486、U12-009、U12-038、U12-063、U12-071、U13-254。-vat 复合词整体 cpd. ind.；子复合词 cpd. 成分；原 pos 附加信息保留（ptc. adj. nom. pl.、gdv. n. nom. sg. 等），原有的性也保留（U11-080、U13-164、U13-280）。U11-085、U11-092、U13-021 原作 v. caus. pres. 3sg.，次序与规则不同未动。
- 数据问题：U12-087、096、109、110、127 lemma 作 īraṇa，句中为阴性 īraṇā；U13-123 utpādana 句中为 -utpādanā（阴性）。缺整个复合词记录的：U10-150（dīrghādi-pariccheda）、U13-256/261、U13-315/316（āśrayarūpaṇāt，GRETIL 分写）、U12-003/004（pṛthivīdhātur）、U12-006~009（aptejovāyudhātavaḥ）。U11-060 skt 片段"artha upādāyārtha"定位不清。

## B：U14–U25

- 标注 944 条，另改正 3 条已合规的；拒绝 0、找不到 0；自查无形态 ERROR。
- (?)：0。U22-029/319、U25-040 tat sarvam … abhisaṃkṣipya 标 nom. sg.；U24-068 etac 是宾语，由 nom. 改 acc.。
- 改词类：无。
- 自定做法：复合词成分（含原带格的末成分）一律标成分（同 A、E）；-tva/-tā/-vat 前词干标成分；X-vat 整词 cpd. ind.；aikadhyam 标 n. acc. sg. (adv.)；saṃkhyāṃ gam 标 v. … (idiom)；kiṃ kāraṇam 标 pron. + n. nom. sg.；U15-148 pron. nom. 1sg. → pron. nom. sg.。改正：U19-052 → n. 成分；U22-228 → n. 成分；U24-070 → v. fut. caus. 1pl.。
- 数据问题：U15-137/139 lemma parihāṇa 疑当作 prahāṇa（玄奘"斷"）；U24-069 lemma "tredho" 当作 tredhā，U24-070 skt "papādayiṣyāmaḥ" 为残片；U14-066 GRETIL vaktavyaḥ 疑当作 vaktavyāḥ；U22-226~228 aṣṭādaśdharmāṇāṃ 讹，疑为两词；缺整词记录：U22-340/341（āyadvāra bhāvāt 多一空格）、U18-017/018（pañcāśrayāḥ）；U21-022/027/029 长复合词分成两条重叠的 cpd 记录；U24-016 lemma "ni-veśaya (caus. viś)" 写法不规范。

# 补标性（2026-10-29，用户要求"按词类、性、数、格的顺序标"）

合并前我先做的：已有标注的格数次序改为数、格（4,565 条，morph.canon）；复合词末成分统一照整个复合词标（209 条由"成分"改出，lint 查末成分与复合词的性数格一致）；pañca → pañcan。之后七组分单位补标性。

## D2：U31–U36

- 650 条（U31 82、U32 72、U33 207、U34 167、U35 26、U36 96），拒绝 0、找不到 0；无形态/末成分 ERROR。
- (?)：U31-187 与末成分 U31-192 -ādiṣu 标 nt. pl. loc. (?)（阳中同形，所列门窗口多中性）；U33-048 parasya、U33-157 yasya、U33-159 tasya、U33-265 paraiḥ 标 m. (?)（泛指"法""他"）；U33-324 anāsrave m. (?)（暗含 dharma）；U34-142 eṣām、U34-144 trayāṇām m. (?)（rūpa nt.、śabda m.、spraṣṭavya nt. 混合）。
- 次序改正：U32-010、U33-174（ptc. pres. 格在数前；canon 把含 pres. 的分词当动词处理，漏排）。
- 同一名词不同性（都合规则）：ādi（有情列举 m.；-ādīni nt.）；ālambana U34-401 m.、indriya U34-319 m.、vasti-guhya U34-282 m.（多财释末成分）。
- 数据问题：U33-366 skt śabdadhātū、lemma śabda，被当成 rūpaśabdadhātū 的末成分，实为非末成分（共用的 dhātu 无记录）；末成分未被脚本关联：U34-319、U34-343、U31-138（已手工保持一致）。scratchpad 根目录共用，临时文件被别组覆盖过（已改用子目录）。

## G2：U49–U54

- 563 条（U49 105、U50 79、U51 30、U52 127、U53 124、U54 98），拒绝 0、找不到 0；lint ERROR 0、WARN 0。
- (?)：U53-094 ūrdhvaṃ adj. nt. sg. nom. (?)（修饰阳性 śabda 而作中性，疑套颂文 ūrdhvaṃ rūpaṃ 或作副词）；U52-097 rūpāṇi n. nt. pl. nom. (?)（保留）；U49-044 ghoṣam n. m. sg. acc. (?)（note 疑当读 yojyam）。
- 次序改正：U52 的 12 条 ptc. pres.（086、096、109、117、126、145、155、159、166、172、180、198）。U50-130、U51-050 kiṃ kāraṇam 改作 pron. nt. sg. nom. + n. nt. sg. nom.（照 U27-164）。
- 有判断余地未加 (?)：caramasya（U49-181、U50-001）、eṣāṃ（U49-185）m.（指 dhātu）；-ādīnām/-ādibhiḥ 斜格复数按同段 -ādayaḥ 标 m.；U52-007、U50-019 taiḥ m.；U53-101 ubhe nt.；kim 疑问小词 pron. nt.。U53-128 bhūmi 作多财释末成分标 nt.（复合词修饰 kāyavijñānam）。
- 数据问题：末成分未被脚本关联（连声或词目写法）：U49-070、139、147，U50-011、087、093、099、127、134、136，U52-193，U53-144、151，U54-067、143（已手工核对一致）；compar. 位置不统一（U51-040 放括号里，U49-022/026 放词类后）；-upapanna 复合词 U53-141/148 作 cpd.、U52-077/150/191 作 cpd. ptc.；U52-097 的译语"色"对的是宾语，对应本身待核。

## E2：U37–U43

- 637 条（U37 48、U38 77、U39 153、U40 57、U41 166、U42 71、U43 65），拒绝 0、找不到 0；无形态/末成分 ERROR。
- U40-092/094/095 dagdhṛtulyayoḥ 定为第七格（vivāda 的论题用第七格；"关于能烧、所称有争论"，合玄奘"能燒所稱 諍"），性随 tulya 作 nt.（下文 S0732、S0733 tulyam 皆中性）：三条均为 nt. du. loc.，U40-094 去掉 (?)。
- (?)：U38-100、U38-105、U38-107 -ādiṣu 取 m. (?)；U41-152、U41-170 asau 取 f. (?)（随表语 paraṃparā；note 说指"聲"m.，存疑）；U43-064 cakṣurādīnām m. (?)。原有 (?) 保留：U39-152、153、170，U41-294、295，U42-075。
- 改正：U38-125 cpd. du. abl. → cpd. m. du. instr.（与末成分 U38-127 instr. 一致，"以损益而展转相随"）；U42-020、029、040、045、057、076、096 ptc. pres. 次序；U42-001、104、107 括号说明 (dvandva) 移到末尾；U41-128 kiṃ kāraṇam 只插入性。
- 同一名词不同性（合规则）：ādi（m. U38-105、U41-013；nt. U39-018、U39-089、U40-038、U42-026）；cakṣus（U42-084、U42-090 多财释末成分指人作 m.）。
- 数据问题：末成分 skt 以连声元音开头（o-、ā-）时脚本认不出：U38-125↔127、U38-128↔130、U40-022↔024、U40-029↔031（已手工一致）。较费斟酌未加 (?)：U39-091 cakṣurādibhir nt.、U42-049 ubhayena m.、U41-055 tasmāt m.。

## C2：U21–U30

- 657 条（U21 18、U22 216、U23 34、U24 37、U25 42、U26 95、U27 87、U28 65、U29 26、U30 37），拒绝 0、找不到 0；lint 无 ERROR。复合词与末成分两两对查一致。
- (?)：U22-137 atītādīnāṃ nt.；U22-143 vedanādayo、U22-146 veditavyāḥ m.（或随 vedanā 作 f.）；U22-205 kasyā nt.；U22-261 ekasyāsti m.（承 paramāṇu，或泛指 nt.）；U26-040 dvābhyāṃ m.；U26-213 cakṣurādīnām m.（或指眼等根 nt.）；U28-150 ebhir m.；U27-128 jihvā 原有 (?)（格存疑），加 f.。
- 改：无（只把 U24-059、U25-009、U27-095 的 ptc. 次序调为数、格）。
- 同一名词不同性（都是多财释末成分随复合词）：āśraya（U22-103 nt.）、viṣaya（U27-024、U27-084 nt.）、svabhāva（U29-023、U29-036 nt.）、saṃjñā（U24-055 m.）、pramāṇa（U30-006 m.）、ādi。-tas 形式不标性（U22-059、U23-027、U26-010、U26-121）。
- 格式：kiṃ kāraṇam 写法不统一（U23-058 "pron. nt. + n. nt. sg. nom."，U27-164 "pron. nt. sg. nom. + n. nt. sg. nom."）；U27-123 bhojyasya 作 gdv. n. nt. sg. gen.。
- 数据问题：U22-207 svasyā 的 WARN 是误报（f. -asyāḥ 脱 visarga；已改粗查规则）；U21-018 dvayoḥ 词目作 dvaya（n.），实为 dvi 的双数斜格，词目应改 dvi、词类 num.；U27-067 itasmād 已标待核（疑读 ito 'smād），性取 m.。

## B2：U11–U20

- 580 条（U11 48、U12 71、U13 147、U14 34、U15 90、U16 59、U17 20、U18 35、U19 55、U20 21），拒绝 0、找不到 0；lint ERROR 0；form_gender_warning 无矛盾。
- (?)：U11-043 kuśalākuśale cpd. nt. sg. loc. (?)（无中心词；或指 dharma 作 m.）；U12-137 pṛthivyādīnāṃ m. (?)；U13-080 kena m. (?)（按答句 pāṇisparśena）；U13-278 avijñaptyāśrayeṣu m. (?)（同位于 mahābhūteṣu nt.）；U15-067 caturbhyo m. (?)（颂文暗指四蕴；长行 U15-080 标 nt.）；U16-109 teṣām m. (?)；U19-005 ekena m. (?)（兼管 skandha m.、āyatana nt.、dhātu m.）。
- 改：脚本未认出的末成分 16 条由"成分"改为照复合词：U12-056、U12-087、U12-106、U13-078、U13-107、U13-115、U13-123、U14-003、U14-014、U15-027、U15-037、U15-053、U17-006、U17-013、U17-041、U18-037。另 6 条 ptc. pres. 只调次序（U13-016、102、154，U15-018、059，U19-019）。U12-109（-vat 前）、U12-127（非末成分）仍作成分。
- 同一名词不同性（合规则）：citta（U11-021 多财释末成分 m.）、svabhāva（U11-078 f.，随 avijñapti）、utpādana（按词形 nt./f.）、ākhyā（U15-191 m.）、cittaka（U11-017 m.）；īraṇa 三处 f.。
- 数据问题：final_members 漏检的类型——连声使末成分首字母变 ā/e/o；词目是动词词根而词形是分词（saṃ-sidh/siddhāḥ、jan/jātasya、vyadh/viddha、ni-rudh/niruddhaṃ）；词目太短（ja/jā）或阴性 -ikā；skt 讹字（sdandha、vyavasathānād）。U14-066 vaktavyaḥ 疑当读 vaktavyāḥ（note 未注）；U14-001 与 U14-012 同一复合词，前者带 (dvandva) 后者无；kiṃ kāraṇam 写法不统一。

## F2：U44–U48

- 744 条（U44 178、U45 74、U46 290、U47 32、U48 170），拒绝 0、找不到 0。自查剩 U48-100 一条末成分 ERROR：U48-099 skt 误包 "ity arthaḥ"（应作 prāptaviṣayam），致 U48-100 arthaḥ 被当成末成分。
- (?)：U48-221 cayavatāṃ m. (?)（m./nt. 同形）；U48-149 hasto、U48-152 upale 原有 (?) 保留。
- 改：无；U45-083 括号说明移到末尾。
- 同一名词不同性：viṣaya（多财释末成分 U46-273、U48-007、U48-085 作 nt.）。
- 按所指定性未加 (?)：-ādi 复合词（U44-286 m.；U46-040、U46-016、U46-019 f.，指五见；U46-227 nt.；U48-059、U48-290、U48-310 nt.，指称作 trayam 的诸根；U48-302 m.）；U48-120 anyonyam m.；副词性疑问 kim 皆 nt.；指人的代词、数词 m.（U44-182 等）；U46-030 ayam m.、U48-109 kā iyam f.、U46-131 asau f.。
- 数据问题：skt 带进邻词（U48-196、U48-199、U46-538）；U47-041、U47-043 GRETIL parasaṅga（应作 prasaṅga），末成分未被认出（已一致）；迦濕彌羅 词目 kāśmīra（U44-118）与 kāśmīraka（U48-123）不统一。scratchpad 根目录跑过 rm -rf scratchpad/sim（只删同名目录）。

## A2：U01–U10

- 760 条（U01 91、U02 45、U03 21、U04 36、U05 139、U06 65、U07 52、U08 23、U09 42、U10 253），另改 7 条末成分（U06-145、U08-005、U10-215、U10-234、U10-356、U10-518、U10-310 由"成分"补出性数格），拒绝 0、找不到 0；无形态/末成分 ERROR；与备份比对，pos 以外未动。
- (?)：U10-148 nīlādīnāṃ cpd. nt. pl. gen. (?)（无中心词：照 S0140 指 varṇa 作 m.，照 S0144 作颜色名词作 nt.）。据 Yaśomitra 定下的：U05-125/128 m.（多财释 ekarūpavyāsaktacakṣurmanāḥ）；U01-159 anena nt.（指 viśeṣaṇa）。
- 次序改正：U01-107、U10-431（ptc. pres.）。
- 同一名词不同性：andhakāra（U01-006 多财释末成分 m.；andhakāram nt.）；kośa（U03-016 m.；书名 abhidharmakośam 一律 nt.，与 śāstram 同位）；svabhāva、varṇa、saṃsthāna、ālambana 作多财释末成分随所修饰的词。
- 数据问题：U05-095 lemma 作动词 sākṣāt-kṛ 而 pos 是名词 sākṣātkaraṇa，脚本因此认不出它是 U05-091 的末成分（两条已一致 nt. sg. abl.）；U06-093 grahaṇāt xz 空、note 待核。scratchpad 根目录的 build.py 被别组换过，误跑一次（只重写了 scratchpad 里 U44–U48 的草表，没写项目文件）。

# 补复合词整词记录（2026-10-29，用户要求"补上缺的复合词整词记录"）

akbh1_cpd_todo.py 找出孤立成分（标"成分"而句中没有整词记录包住的），归并为 71 个候选，分三组逐个判断；新增用 akbh1_add_records.py，改成分用 akbh1_edit_records.py（都先核验）。

## cpdA：U01–U13（22 个候选）

- 新增 10 条：U01-166 māhātmya-jñāpana-artham（cpd. ind.）、U01-167 pratipakṣa-lābha、U04-064 bhadanta-kātyāyanīputra-prabhṛti、U04-065 bhadanta-dharmatrāta-udāna-vargīya-karaṇa-vat（cpd. ind.；GRETIL 分写的 dharmatrāto 是 dharmatrāta + udāna 连声，EdUHK 同）、U05-195 samāsa-nirdeśa、U10-529 dīrgha-ādi-pariccheda、U12-140 pṛthivī-dhātu、U12-141 ap-tejas-vāyu-dhātu（二词合为"四界，即地水火風"）、U13-323 sva-bhūta-catuṣka-āśrita-tva-abhyupagama、U13-324 āśraya-rūpaṇa（GRETIL 分写）。
- 改成分 27 处：skt 收窄（U01-059、U04-035、U06-038、U10-059、U10-150、U11-060、U12-004、U12-128、U13-003、U13-004、U13-062、U13-063、U13-257、U13-258、U13-261、U13-315 等），末成分由"成分"改为性数格（U10-151、U11-060、U12-004、U12-128、U13-004、U13-063、U13-261、U13-316），U04-037 prabhṛti ind. → n. m. pl. instr.（照 -ādi），U04-042 dharmatrāta n. m. sg. nom. → n. 成分。
- 误报：hyeka、caikavarṇam、hetvartha、īraṇāsvabhāvo、varṇasaṃsthānam、rūpaskandha（整词已有，成分 skt 带进邻词或与整词同长）。
- 待编者定：U04-065 改为大复合词；prabhṛti 的词类；U12-126 īraṇāsvabhāvo 作多财释（主会话已改 cpd. adj. m. sg. nom. (bahuvrīhi)）；收窄后的 skt 在句中出现两次的 U04-035、U11-060、U12-128、U13-003（靠记录次序区分）。

## cpdC：U34–U54（24 个候选）

- 新增 9 条：U34-417 tad-a-saṃbhava、U39-293 sa-rāga-citta-ādi-vacana（GRETIL 分写）、U40-128 dhātu-catuṣṭaya（GRETIL 分写）、U41-333 prathama-an-āsrava（cpd. adj.）、U46-596 sa-megha-a-megha-rātrindiva-rūpa-darśana（cpd. 成分 (-vat)）、U46-597 kliṣṭa-a-kliṣṭa-laukika-śaikṣa-a-śaikṣa（cpd. adj. f. pl. instr. (dvandva)；玄奘拆在"世間諸見有染無染"与"學無學見"两处）、U46-598 tad-vijñāna、U46-599 cakṣus-saṃprāpta（GRETIL 分写）、U48-311 saha-bhū-gandha-ādi-a-grahaṇa。
- 改成分 13 处：skt 收窄（U34-207、U39-244、U45-118、U46-474、U46-490、U48-066、U48-067），末成分补性数格（U41-281、U45-118），U46-075 lemma samegha-amegha → sa-megha-a-megha，U46-490 去掉 (?)，U39-080、U39-075 note。
- 误报：X-vat 后接的 atideśa、avasthita、acchatva 是另一个词（C-6、C-7、C-18–23）；C-8、C-24 整词已有。
- 待编者定：C-2 U39-075 catuṣṭva 与 khakkhaṭādilakṣaṇa 疑同属一个复合词（GRETIL 分写；真谛"四大及堅等四相"），要动 skt/lemma/xz/pm 四栏，已标待核；C-3 sarāgacittādi 缺 citta、ādi 成分记录；U46-491 lemma saṃ-prāpta 拆了分词前缀，不合第八节；另有约 10 条成分记录的 skt 与整词同长（U34-049、U35-037、U39-068、U46-092、U46-537、U50-092、U51-036、U52-069、U53-185、U54-004）；cakṣurādivad、rūpādivad 无成分记录。

## cpdB：U14–U33（25 个候选）

- 新增 19 条：U21-051 eka-cakṣus-śrotra-adhiṣṭhāna-eka-nāsikā-bila-saṃbhava（原 U21-029 降为子复合词 eka-nāsikā-bila，cpd. 成分）及第二个 eka 成分 U21-052；U22-412 āya-dvāra-bhāva（GRETIL 分写）；U30-099 carita-sahasra、U30-100/101 dharma-skandha-sahasra；U31-195~204 六界（pṛthivī-、ap-、tejas-、vāyu-、ākāśa-、vijñāna-dhātu）及所缺的四个 dhātu 末成分；U32-136 citta 末成分（cyuticittaṃ sādhāraṇabhūtāḥ，第二格推定，待核）；U33-396/397 aṣṭādaśa-dhātu。
- 改 45 处：成分 skt 收窄（为使页面高亮——取 skt 在句中第一次出现处——落在正确位置，有的多带前一成分的末字母，如 odhātur、ticitta），末成分补性数格，U18-017/018 pañca āśrayāḥ 判为两个独立的词（num. pl. nom.、n. m. pl. nom.），U32-051、U32-058 tat/tad 判为独立代词（pron. nt. sg. nom.）。
- 误报：B-9 pradeśivat、B-12 sapratighatvāt、B-15 audārikatvāt（单词干派生词）。
- 待编者定：aṣṭādaśa-dhātu 照 aṣṭādaśa-dharma、daśa-dhātu 的先例写（不作 aṣṭādaśan-）；pañcāśrayāḥ 作两个词；U21-029 真谛 pm "一鼻一孔生"的"生"属 saṃbhava（工具改不了 pm，note 已说明）；U32-100 的格。

# 补成分记录（2026-10-29，用户要求"也把缺的成分记录补上"）

akbh1_member_todo.py 找成分记录不全的复合词（920 个，脚本推测缺约 1,787 个成分；其中 708 个复合词原无成分记录），分七组逐个核对补写（akbh1_add_records.py，after 栏按句中次序插在整词或前一成分之后），新记录 note 皆作"补成分记录"。

## M5：U42–U46

- 新增 280 条（U42 58、U43 27、U44 92、U45 51、U46 52），其中省译 32 条；改已有 1 条（U44-252 gṛhaṇād 末成分 → n. nt. sg. abl.）。verify 0 错，lint 0 ERROR；member_todo 剩 3 个（U46-150 -arthena 已有语法记录；U44-178、U44-287 同一复合词里 sabhāga 出现两次，脚本分不清）。
- 脚本漏报而实缺、已补：U42-107、U44-004、U44-071/077、U45-114、U46-040、U46-194（同句别的复合词的成分被算作已有）。
- 新词目：koṭika、dharmaka（-ka 形式照 ādika 单独立目；catur-koṭika 在 U05、U33、U50 的写法宜统一）、dharmin、a-ṣaṣṭha、vi-i（ptc. (vīta)）、kṣānti、dṛśi、pāṭha、ānupūrvī（整词词目 pāṭha-anupūrvī 是否改 pāṭha-ānupūrvī 待定）。
- 待定：U43-061、U42-092、U44-071 整词意译，成分难逐字对；分词词目 ā-śri 与 āśrita 并存（U46-188、193、345 用 āśrita）；tatsabhāga 真谛"非等分"，"非"未对给 tat；U42-120、U44-079 ca 标 ind. 成分；GRETIL 误字照录 skt、note 注正读。

## M7：U53–U54

- 新增 184 条（U53 89：U53-222~310；U54 95：U54-167~261），改已有 1 条（U54-083 indriya 末成分 skt 收窄为 indriyaṃ）。verify 0 错，lint 0 ERROR；member_todo 剩 1 个（U54-118 末成分已有 U54-120 ānantaraṃ，词目 anantaram，脚本误报）。
- 新词目 11 个：avacara、utsarga、ati-bahu（照 ati-viprakṛṣṭa 合为一条）、jīvita、saumanasya、daurmanasya、upekṣā、śraddhā、vīrya、ājñā、ājñātāvin。序数词成分作 num. 成分 (ord.)；ukta 末成分作 vac … (ukta)；adhas 作 ind. 成分（无先例，待定）。
- 待核：U53-274 utsargaviśeṣeṇa 真谛"通立無差別"，疑读 utsargam aviśeṣeṇa（已标待核；若成立，整词 U53-118 也要重拟）。
- 合译、意译、概括处的分配见各条 note（dvitīya-ādi → 上三；ati-bahu、bhāra → 繁；tad-bhūmika → 等；色等五界、眼等五識中未单独译出的成分记省译）。
- 页面问题：玄奘译语的高亮取所标行中第一处，单字译语（根、等、色、識）在同行前面已出现时会标错——主会话改页面。
- 词目写法：ṣaḍ-āyatana 与 ṣaṣ-āyatana 并存。

## M2：U11–U22

- 新增 258 条（U11 21、U12 28、U13 34、U14 10、U15 14、U16 36、U17 7、U18 18、U19 19、U20 6、U21 5、U22 60；对译 219、意译 12、省译 24、合译 3），改已有 13 处。verify 0 错，lint 0 ERROR，member_todo 剩 0。
- 更正脚本推测：-tva 前的词干（U15-132、U22-150、U22-151）标成分；U19-065 缺的是 tad；U22-008、U15-084 被同句别的记录抵掉。另补脚本漏报的 16 条（U14-046/049/051 dhātu、U19-050 cakṣus、U14-016、U15-038 颂文复述、U15-030、U19-025、U22-161）。全库另有 17 个复合词被脚本漏报（清单 scratchpad/memM2/script_missed.txt），末成分误标"成分"16 条（scratchpad/memM2/finalchk_all.txt）——主会话合并后处理。
- 改已有：末成分补性数格 U11-003、U11-028、U14-027、U15-120、U19-087、U22-053、U22-132、U22-406；U12-041 mahā → mahat；U16-076 skt。
- 新写法：ud-bhū（ptc. 成分 (udbhūta)）；api、hi 作成分标 ind. 成分；upādāya 作成分标 abs. 成分（词目 upa-ā-dā）。
- 待定：mahā-bhūta 拆作 mahat→大、bhūta→種（意译）；U11-061 artha 合译"義"；U12-032 udbhūta、vṛtti 合译"增盛"；U16-071 daśāyatanāni 或为两词（标待核）；U22-295 anāgata、pratyutpanna 省译（玄奘以"等"概括）。

## M4：U35–U41

- 新增 230 条（U35 7、U36 48、U37 8、U38 32、U39 46、U40 9、U41 80），改已有 1 条（U36-044 skt 多带下一词开头，收窄）。verify 0 错，lint 0 ERROR，member_todo 剩 0。
- 另补脚本漏报：U39-153/156 mahat；U35-006 asaṃskṛta（省译）；U39-049、U40-095 长行复述的同形复合词。
- 切法：U40-045 a-dvaidhī-karaṇa 否定管整个 dvaidhī-karaṇa，补 a- (neg.)（gram. neg.）→ 非；nir-indriya 仿 nir-avaśeṣa 作一条；sa-vitarka + vicāra。
- 新词目：viṣ、mūtra、vidha、a-vinirbhāga、vartin、anvaya、dvaidha（adj. 成分 (dvaidhī)）、nir-indriya、pada、lopa、go、ratha、pāṭha、kṣānti。
- 待定：共用一个汉字的成分记合译（U38-004 六識的六个成分皆"六"；U38-069 眼等五根；U35-001 通），也可作省译；viṣ-mūtra；pāṭha-krama 意译的分法；caitasika-svabhāva 的 svabhāva → 法；karma-ja 的 ja → 從…所生；U41-176 ja 省译；sa- 重出的处理（U36-008、U36-102）；bhūta → 種 标对译；GRETIL 误字处 skt（U39-162、U39-190、U38-122）；U38-005 dhātu 真谛作"根"；U39-247 yathā-ukta 的 ukta → 所說。

## M6：U47–U52

- 新增 287 条（U47 3、U48 48、U49 73、U50 39、U51 24、U52 100），改已有 4 条 skt（U48-199、U51-003、U52-137、U52-193）。verify 0 错，lint 0 ERROR，member_todo 剩 0。
- 脚本当作已有、其实缺（相邻复合词的成分或独立的词被抵掉）：U52-072、U52-115/116、U52-124、U52-196、U52-157/161/184、U52-191。
- 新词目：ni-mīl（ptc. … (nimīlita)）、anyathībhāva、alāta、cakra、vāla、drākṣā、carman、koṭika、avacara。
- 待定："X 等"概括成一字的四处（U50-137 根、U50-141 境、U51-049 餘、U52-047 境）两成分都记合译；U48-094 鼻等三；tad/sva-bhūmika 系列（代词还原记意译，bhūmika → 屬/地）；ardha-nimīlita、anyathībhāva、alāta-cakra（GRETIL 脱 ca，cakra skt 取 krā）的拆分；U49-175、U48-103 整词译语里的增字未拆；U50-118、U50-123、U52-163、U52-196 嵌套复合词未补中间层记录。

## M1：U01–U10

- 新增 284 条（U01 43、U02 17、U03 10、U04 20、U05 77、U06 16、U07 12、U08 8、U09 25、U10 56），改已有 16 条。verify 0 错，lint 0 ERROR，member_todo 剩 0。不补的只有后缀 -tva、-vat。
- 另补候选外被顶替的：U01-095 pratipatti、saṃpad；U05-088 dravya；U10-469 viṣaya；U10-069 saṃsthāna 末成分。
- 改已有：末成分误标"成分" → 性数格（U06-131、U07-071、U08-019、U09-071、U10-020、U10-023、U10-067、U10-166、U10-170、U10-306）；skt 收窄（U03-011、U05-023、U10-010、U10-019、U10-305）。skt 过宽未动：U01-004、U01-005、U09-003、U09-054、U09-006、U07-030。
- 新词目：hita、pratipatti、saṃpad、upāya、vara、parama、arṇava、pada、lopa、go、ratha、sākṣātkriyā；-ka/-īya 派生词 pūrvaka、koṭika、sthānīya、pratilambhika。
- 待定：U01-201 upāya → 方便（待核，取下句移后的译法）；-bhūta（成为）用 bhū ptc. (bhūta)，U26-115、U26-199 作 bhūta ptc. (bhū)，需统一；mahat/mahā 并存；多财释末的 -dharman 词目作 dharma；U05-074 duḥkhādi → 四 合译；U05-049 satya → 聖諦（"聖"为补出）；连声片段两边都取融合元音。

## M3：U23–U34

- 新增 319 条（U23 9、U24 16、U25 22、U26 17、U27 12、U28 14、U29 8、U30 20、U31 44、U32 26、U33 69、U34 62；其中 13 条给候选外被顶替的复合词），改已有 13 处。verify 0 错，lint 0 ERROR；member_todo 剩 5 个复合词（整词省译，暂未补成分）：U28-105、U30-060、U33-064、U34-010、U34-415。
- 改已有：末成分补性数格 U23-033、U23-064、U24-017、U25-064、U25-068；skt 夹带下一词删去 U32-030、U33-042、U33-391、U34-350、U34-359；另 U32-028、U33-040、U33-389、U34-348、U34-357 收窄 skt。U33-025、U33-234、U34-372 按同词目先例加一层 cpd. 成分。
- 新词目：abhibhu（照 abhibhu-āyatana；是否应作 abhibhū 待定）、vi-i（ptc. 成分 (vīta)）、koṭika、praṇidhi、sthiti、sādhāraṇa、vasti、guhya。
- 待定：U27-026 vartamāna → 一（待核）；合译处 U26-213 根、U31-003 等、U33-333 等、U33-207/240 有對；U31-087 等处整词词目里成分连写（ānantyāyatana、abhibhvāyatana、kṛtsnāyatana、praṇidhijñāna）；U33-253 pm_line 疑应为 0167b11。
