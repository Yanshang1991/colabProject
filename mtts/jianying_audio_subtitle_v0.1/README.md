# 剪映音频字幕获取脚本

## 目录结构
- audio_subtitle // 核心逻辑代码
- config.json // 配置文件
- example.py // 例示代码
- example.wav // 例示音频

## 使用说明
建议使用脚本前，先运行一次剪映识别字幕功能，抓取每个URL的请求头参数并配置在config.json文件中

## URL抓包工具
Proxifier + Fiddler

### 需要获取签名的URL：
- https://lv-pc-api.ulikecam.com/lv/v1/upload_sign
- https://lv-pc-api.ulikecam.com/lv/v1/audio_subtitle/submit
- https://lv-pc-api.ulikecam.com/lv/v1/audio_subtitle/query
  
### 需要获取请求头参数
- device-time
- tdid
- sign