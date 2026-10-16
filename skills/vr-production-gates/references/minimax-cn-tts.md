# 中国大陆 MiniMax TTS

本工具直接调用中国官方HTTP TTS，不冒称mcode执行。当前默认中国文档域名是api.minimax.cn；官方GitHub旧示例还使用api.minimaxi.com，工具仅允许这两个中国官方base，不自动切国际域名。中国M Plan说明可用音频模型并可获取API Key接入外部工具；具体TTS调用权限、额度扣减及账单必须看账户与实际结果，不从“订阅支持”推导免费API。

## 使用

Python 3.10+标准库，FFmpeg/ffprobe用于实际音频校验。密钥由宿主注入MINIMAX_CN_API_KEY或MINIMAX_API_KEY，不复制进脚本、Skill、Wiki或命令参数。

运行音色查询：python3 scripts/minimax_tts_cn.py voices。真实系统音色ID从成功查询或官方音色表取得，不猜测用户克隆音色。接口错误先诊断；音色查询不通过不反复发送生成请求。

配音：python3 scripts/minimax_tts_cn.py synthesize --text-file <本版口播.txt> --voice <音色ID> --model speech-2.8-hd --output-dir <新的配音目录>。

也可用speech-2.8-turbo。按完整语义句生成，默认一个文件处理30秒片旁白，不按字幕逐字调用。若按章生成，每章使用独立目录；成功目录会核请求与音频SHA后复用，失败目录保留诊断且不自动发新请求，防止未知结果重复计费。HTTP超时不表示服务端未执行。认证失败、余额/权益问题按准确代码说明，不绕道换账户或隐式改服务。

输出配音.mp3、voiceover-manifest.json，记录模型/音色/速度、文本SHA、请求SHA、音频SHA、trace_id、用量字段和技术状态。ffprobe核时长及音频流、ffmpeg完整解码通过才写technical_passed；生成成功不等于发音/音色合格。词级时码仍用既有对齐流程，subtitle_enable=false不生成虚构逐字时间戳。BGM仍用指定现成曲库。

## 官方依据与本次边界

- [中国同步TTS](https://platform.minimaxi.com/docs/api-reference/speech-t2a-http)：POST /v1/t2a_v2，speech-2.8-hd/turbo，data.status=2与hex音频，usage_characters、trace_id。
- [中国音色管理](https://platform.minimaxi.com/docs/api-reference/voice-management-get)：POST /v1/get_voice，voice_type=system。
- [中国M Plan](https://platform.minimaxi.com/docs/m-plan/intro)：音频模型可用、API Key可接外部工具。
- [官方HTTP示例](https://github.com/MiniMax-AI/skills/blob/main/skills/frontend-dev/scripts/minimax_tts.py)：同步非流式实现参考。

2026-10-16真实音色查询返回API code 2049、无trace_id，本次未生成真实音频，不能宣称账户已获TTS权限或订阅已扣费/未扣费。离线测试用合成音频验证写入、SHA、解码和恢复行为；不代表真人试听。需要账户对应的中国M Plan可用凭据完成真实生成验收。
