# -*- coding: utf-8 -*-
"""Dockable Douyin web panel for Cinema 4D 2027. Local prototype."""
import json
from pathlib import Path
from urllib.parse import urlsplit

import c4d

PLUGIN_ID = 1069987  # Local prototype ID; obtain a Maxon ID before distribution.
PLUGIN_NAME = "抖音网页版"
HOME_URL = "https://www.douyin.com/"
ROOT = Path(__file__).resolve().parent


def normalize_douyin_url(value):
    value = value.strip()
    if not value:
        return HOME_URL
    if "://" not in value:
        value = "https://" + value
    parts = urlsplit(value)
    host = (parts.hostname or "").lower()
    if (parts.scheme != "https" or parts.username or parts.password
            or parts.port not in (None, 443)
            or not (host == "douyin.com" or host.endswith(".douyin.com"))):
        raise ValueError("请填写 https:// 抖音官网链接，例如 https://www.douyin.com/")
    return value


class DouyinDialog(c4d.gui.GeDialog):
    BACK, FORWARD, HOME, REFRESH = 1001, 1002, 1003, 1004
    VIEWER, STATUS = 1100, 1101

    def __init__(self):
        super().__init__()
        self.viewer = None
        self.bridge_result = None
        self.last_url = HOME_URL
        self.status = "抖音官网 · 页面加载和视频播放取决于网络及内置浏览器兼容性"

    def CreateLayout(self):
        self.SetTitle(PLUGIN_NAME)
        self.GroupBorderSpace(4, 4, 4, 4)
        self.GroupBegin(1200, c4d.BFH_SCALEFIT, cols=4)
        self.GroupSpace(4, 4)
        for mid, label in ((self.BACK, "返回"), (self.FORWARD, "前进"),
                           (self.HOME, "抖音首页"), (self.REFRESH, "刷新")):
            self.AddButton(mid, c4d.BFH_LEFT, name=label)
        self.GroupEnd()
        self.viewer = self.AddCustomGui(
            self.VIEWER, c4d.CUSTOMGUI_HTMLVIEWER, "",
            c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 480, 480)
        if not isinstance(self.viewer, c4d.gui.HtmlViewerCustomGui):
            print("[Douyin] HTML viewer creation failed.")
            return False
        self.AddStaticText(self.STATUS, c4d.BFH_SCALEFIT, name=self.status)
        return True

    def InitValues(self):
        # Only our packaged diagnostics page can send messages to this callback.
        if hasattr(self.viewer, "SetWebMessageCallback"):
            self.viewer.SetWebMessageCallback(self.OnWebMessage, "bridge.html")
        self.Navigate(self.last_url)
        return True

    def SetStatus(self, value):
        self.status = value
        self.SetString(self.STATUS, value)

    def Navigate(self, value):
        try:
            url = normalize_douyin_url(value)
        except (ValueError, TypeError) as exc:
            self.SetStatus(str(exc))
            return False
        self.last_url = url
        self.viewer.SetUrl(url, c4d.URL_ENCODING_ESCAPED)
        self.SetStatus("抖音官网 · 如需登录，请直接在网页中自行操作")
        return True

    def ShowDiagnostic(self):
        self.bridge_result = None
        self.viewer.SetUrl((ROOT / "res" / "bridge.html").as_uri(), c4d.URL_ENCODING_ESCAPED)
        self.SetStatus("正在检测本地网页与 C4D 的双向通信…")

    def OnWebMessage(self, message, error):
        if error or not isinstance(message, str) or len(message) > 4096:
            return
        try:
            data = json.loads(message)
        except (ValueError, TypeError):
            return
        if not isinstance(data, dict) or data.get("app") != "douyin-panel-diagnostic":
            return
        if data.get("event") == "ready":
            self.bridge_result = {"received": True, "acknowledged": False,
                                  "h264": data.get("h264"), "webm": data.get("webm")}
            self.viewer.PostWebMessage(json.dumps({"app": "douyin-panel-diagnostic", "event": "ack"}))
        elif data.get("event") == "confirmed" and self.bridge_result:
            self.bridge_result["acknowledged"] = True
            self.SetStatus("双向通信成功 · 点击“抖音首页”返回网页")
            print("[Douyin] Web message round trip OK. " + json.dumps(self.bridge_result))

    def Command(self, mid, msg):
        try:
            if mid == self.BACK:
                self.viewer.DoAction(c4d.WEBPAGE_GOBACK)
            elif mid == self.FORWARD:
                self.viewer.DoAction(c4d.WEBPAGE_GOFORWARD)
            elif mid == self.HOME:
                self.Navigate(HOME_URL)
            elif mid == self.REFRESH:
                self.viewer.DoAction(c4d.WEBPAGE_REFRESH)
        except Exception as exc:
            self.SetStatus("操作失败：" + str(exc))
            print("[Douyin] " + repr(exc))
        return True


class DouyinCommand(c4d.plugins.CommandData):
    def __init__(self):
        self.dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = DouyinDialog()
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID,
                                defaultw=1080, defaulth=780)

    def RestoreLayout(self, secret):
        if self.dialog is None:
            self.dialog = DouyinDialog()
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=secret)

    def GetState(self, doc):
        return c4d.CMD_ENABLED


COMMAND = None


def register():
    global COMMAND
    if c4d.plugins.FindPlugin(PLUGIN_ID, c4d.PLUGINTYPE_COMMAND):
        print("[Douyin] Plugin ID already registered: " + str(PLUGIN_ID))
        return False
    command = DouyinCommand()
    ok = c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID, str=PLUGIN_NAME, info=0, icon=None,
        help="在可停靠面板中打开抖音网页版", dat=command)
    if ok:
        COMMAND = command
    return ok


if __name__ == "__main__":
    register()
