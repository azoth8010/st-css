# st-css

SillyTavern 全局自定义 CSS 美化的源码与产物仓库。

一套美化一个目录，源码、字段值和可直接导入的主题 json 放在一起。仓库用于源码与产物的备份，不承载运行时资源请求。

## 目录约定

```text
st-css/
├── .gitignore
├── README.md
├── build.py              打包与字段校验
├── theme.schema.json     主题字段的类型、格式、允许值
└── themes/
    └── <slug>/
        ├── style.css     CSS 源码
        ├── meta.json     该套美化的字段值
        └── <slug>.json   打包产物
```

`themes/` 随第一套美化一起出现。新增一套美化只在 `themes/` 下加同级目录，根目录文件数不增加。

## 命名

目录名与文件名使用英文或拼音 slug。主题在 SillyTavern 中显示的名称保存在 `meta.json` 的 `name` 字段，可以使用中文。产物文件名与所在目录名一致。

## 打包

需要 Python 3.8+，仅用标准库。

```bash
python build.py <slug>            # 生成 themes/<slug>/<slug>.json
python build.py <slug> --check    # 只校验，不写文件
```

脚本读取该目录的 `style.css` 与 `meta.json`，按根目录的 `theme.schema.json` 校验 39 个字段，把 CSS 注入 `custom_css`，产物写回同目录。`meta.json` 中以下划线开头的键是本地注释，不会进入产物。

## 字段

`theme.schema.json` 是全局唯一的字段基准，只描述类型、格式与允许值。每套美化各自的取值写在自己的 `meta.json` 里。新增字段先改 schema，再改各套的 `meta.json`。

## 提交

每套美化连同产物一起提交。产物本身就是备份对象，clone 一次即可取回全部源码与成品。

## 许可

[PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)，全文见 `LICENSE`。

可自由阅读、修改、在非商业作品里使用；**不得用于商业目的**。
