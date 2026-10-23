# c4d-douyin

在 Cinema 4D 的可停靠面板中浏览抖音网页版。

使用原生 `HtmlViewerCustomGui` 直接加载 [抖音官网](https://www.douyin.com/)。顶部提供 **返回、前进、抖音首页、刷新** 四个按钮，搜索和视频浏览通过网页操作。

## 环境

- 已在 Windows / Cinema 4D 2027.0.0 中验证网页显示、视频播放和面板停靠。
- macOS 和其他 C4D 版本尚未验证。
- 需要能够访问抖音官网的网络环境。

## 安装

1. 下载仓库：点击 GitHub 页面的 **Code → Download ZIP**，然后解压。
2. 在 C4D 的 **编辑 → 设置** 中打开首选项目录，进入其上一级的 `plugins` 文件夹；没有则新建。
3. 将本仓库内完整的 **`Douyin` 文件夹**复制到 `plugins`，保持以下结构：

   ```text
   plugins/
   └── Douyin/
       ├── Douyin.pyp
       └── res/
           └── bridge.html
   ```

4. 重启 C4D，在 **扩展 → 抖音网页版** 中打开插件，也可按 **Shift+C** 搜索“抖音网页版”。
5. 拖动面板左上角的停靠手柄，将其放入工作布局。需要下次恢复时，通过 C4D 保存布局。

更新时替换旧 `Douyin` 文件夹并重启 C4D。请避免同时安装旧名 `DouyinPanel` 的副本。

## 使用说明

- **返回 / 前进**：浏览网页历史记录。
- **抖音首页**：回到抖音官网首页。
- **刷新**：重新加载当前页面。
- 登录、扫码及验证由使用者直接在网页中完成，插件不读取或复制其他浏览器的登录信息。

## 开发说明

插件入口是 `Douyin/Douyin.pyp`，由 C4D 启动时注册命令。`GeDialog` 配合 `CommandData.RestoreLayout` 提供可停靠面板与布局恢复接口。

保留供开发调试调用的 `DouyinDialog.ShowDiagnostic()`，界面不显示检测按钮。它加载本地 `res/bridge.html`，通过 `SetWebMessageCallback` 和 `PostWebMessage` 测试消息往返，同时显示浏览器声明的媒体编码支持。该往返通信已在 C4D 2027.0.0 中验证。

接口参考：[Maxon 官方 HTML GUI 示例](https://github.com/Maxon-Computer/Cinema-4D-Python-API-Examples/tree/master/examples/plugins/py_cmd_gui_html)。

## 当前限制

- 本项目为实验插件，命令 ID `1069987` 暂作本地原型使用，尚未申请正式 Maxon Plugin ID；如与其他插件冲突，需要更换 ID。
- 网页行为和视频兼容性受抖音网站、网络及 C4D 内置浏览器影响；媒体编码检测不能保证所有视频都能播放。
- 插件不修改场景，不向网页提供执行 Python 或编辑场景的功能。
- 提供布局恢复实现，但尚未完成跨重启布局恢复测试。

本项目与抖音、字节跳动及 Maxon 无官方关联。
