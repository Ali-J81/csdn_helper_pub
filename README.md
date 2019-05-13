# CSDN Helper
#### QQ机器人自动下载CSDN资源

### 1. CSDN Helper 使用方法：

* 需要 python3.7 以上版本。

* 安装 requirements.txt 依赖库，```pip install requirements.txt``` (建议使用 [独立环境](https://www.jianshu.com/p/6a3ff66cb8d3) 安装)。

* 运行CoolQ插件，酷Q Air 目录下 CQA.exe。如发生错误，参考下文 **CoolQ 插件使用 注意事项**。

* 配置 csdn_helper/config.ini 配置文件，完成自己想要的配置。

* 在 csdn_helper 目录下运行 coolq.py ```python coolq.py``` （如果有独立Python环境，请切换到独立环境中运行）。

* 尝试 发送QQ消息 ```-help``` 给登录的账户（需要是好友，或者在同一个群组中），验证功能是否运行成功。

* 后续会发布 Release 版本以供使用。

### 2. CoolQ 使用：

* CoolQ官网 https://cqp.cc/

* CoolQ Python插件 [coolq-http-api](https://github.com/richardchien/coolq-http-api)

* CoolQ 插件使用 [注意事项](https://cqhttp.cc/docs/4.10/#/)

  >注意如果 酷Q 启动时报错说插件加载失败，或者系统弹窗提示缺少 DLL 文件，则需要安装 [VC++ 2017 运行库](https://aka.ms/vs/15/release/VC_redist.x86.exe)（**一定要装 x86 也就是 32 位版本！**），如果你的系统是 Windows 7 或 Windows Server 2008、或者安装 VC++ 2017 运行库之后仍然加载失败，则还需要安装 [通用 C 运行库更新](https://support.microsoft.com/zh-cn/help/3118401/update-for-universal-c-runtime-in-windows)，在这个链接里选择你系统对应的版本下载安装即可。如果此时还加载失败，请尝试重启系统。

### 3. Selenium Chrome：

* 需要 Chrome 74以上版本，或替换对应的 [chromedriver 驱动](http://npm.taobao.org/mirrors/chromedriver/)。
