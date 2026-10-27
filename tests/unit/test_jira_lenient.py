import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "legacy" / "v1.4" / "scripts"))
from validate_jira_lenient import validate_result

CASES = [
  {
    "id": "空泛代码",
    "root_cause": "代码问题",
    "solution": "已解决",
    "anchors": {
      "specificity": 0,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "责任归咎",
    "root_cause": "开发人员疏忽",
    "solution": "",
    "anchors": {
      "specificity": 0,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "重述现象",
    "root_cause": "程序崩溃",
    "solution": "",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "只说完成",
    "root_cause": "已修复",
    "solution": "",
    "anchors": {
      "specificity": 0,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "空指针修复",
    "root_cause": "空指针导致启动崩溃",
    "solution": "增加判空",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 0
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "配置版本",
    "root_cause": "配置版本不一致导致启动失败",
    "solution": "统一版本后恢复",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "BinderRpc规避",
    "root_cause": "单独运行 BinderRpc case 失败，整个 binderRpcTestSingleThreaded 模块通过",
    "solution": "以整个模块运行",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 10
    },
    "expected_level": "基本有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "偶现重启",
    "root_cause": "服务偶发失败",
    "solution": "重启恢复",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 0
    },
    "expected_level": "基本有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "条件明确无方案",
    "root_cause": "输入超长时接口返回500",
    "solution": "",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 0,
      "verifiability": 10
    },
    "expected_level": "基本有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "多线程竞态",
    "root_cause": "两个线程同时写共享状态导致计数错误",
    "solution": "加锁",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 0
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "环境变量缺失",
    "root_cause": "测试环境未设置RPC_SOCKET变量导致初始化失败",
    "solution": "增加环境检查",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "权限修复",
    "root_cause": "用户角色无写权限导致接口403",
    "solution": "调整角色权限",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "接口不兼容",
    "root_cause": "服务端升级后字段类型改变，旧客户端解析失败",
    "solution": "恢复兼容转换",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "条件与规避",
    "root_cause": "A版本在高负载下超时",
    "solution": "降低并发数",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "笼统测试失败",
    "root_cause": "测试失败",
    "solution": "重跑",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 0,
      "actionability": 10,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "具体堆栈",
    "root_cause": "FooService构造函数在config为空时NPE",
    "solution": "加入配置校验并补充测试",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 15
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "日志证据",
    "root_cause": "升级前正常，升级后模块A在首次请求时500，日志ERR42",
    "solution": "回滚版本并保存日志",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 15
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "仅规避",
    "root_cause": "软件卡住",
    "solution": "重启设备",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 0,
      "actionability": 10,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "明确边界",
    "root_cause": "输入长度256发生越界",
    "solution": "增加边界检查",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "缺方案可通过",
    "root_cause": "网卡禁用时服务初始化失败",
    "solution": "",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 18,
      "actionability": 0,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },

  {
    "id": "网络DNS",
    "root_cause": "DNS配置错误导致服务解析失败",
    "solution": "修正DNS服务器",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "证书到期",
    "root_cause": "TLS证书过期导致连接失败",
    "solution": "更新证书并检查续期",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "磁盘空间",
    "root_cause": "磁盘满导致日志写入失败",
    "solution": "清理旧日志",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "单次重启",
    "root_cause": "客户端超时",
    "solution": "重启客户端",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 0,
      "actionability": 10,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "无主语",
    "root_cause": "已优化",
    "solution": "",
    "anchors": {
      "specificity": 0,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "重试避免",
    "root_cause": "RPC请求短时超时",
    "solution": "增加重试",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 10,
      "actionability": 18,
      "verifiability": 0
    },
    "expected_level": "基本有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "版本回滚",
    "root_cause": "升级到v3后设备无法配对",
    "solution": "回退到v2恢复",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "缓存污染",
    "root_cause": "缓存键忽略语言导致跨语言内容串用",
    "solution": "把语言加入缓存键",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "状态未清",
    "root_cause": "连接断开后旧session未清理导致重连失败",
    "solution": "断链时释放session",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "缺陷重述",
    "root_cause": "某模块有bug",
    "solution": "修改bug",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "资源泄漏",
    "root_cause": "每轮重连未close socket导致FD增加",
    "solution": "断开后关闭句柄",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "负载峰值",
    "root_cause": "高峰期偶发500",
    "solution": "降低QPS",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 5
    },
    "expected_level": "基本有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "文案问题",
    "root_cause": "按钮文字错误",
    "solution": "改正按钮文字",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 18,
      "actionability": 18,
      "verifiability": 0
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "内存不足",
    "root_cause": "OOM killer杀进程，容器memory limit 128MiB",
    "solution": "提高limit并监控内存",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 18,
      "actionability": 18,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "用户操作",
    "root_cause": "客户操作错误",
    "solution": "告知正确操作",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 0,
      "actionability": 10,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "回归遗漏",
    "root_cause": "边界case未覆盖导致输入0时除零",
    "solution": "补充0值测试及分支判断",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "分支竞争",
    "root_cause": "锁粒度过大导致并发请求排队超时",
    "solution": "缩小锁范围",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "配置规避",
    "root_cause": "切换环境后仅Dev网络能访问",
    "solution": "切回Dev",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 5
    },
    "expected_level": "基本有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "更新依赖",
    "root_cause": "依赖包新版本改变API签名导致编译失败",
    "solution": "固定兼容版本",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 18,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "仅工单",
    "root_cause": "BUG-123已处理",
    "solution": "",
    "anchors": {
      "specificity": 15,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "串口初始化",
    "root_cause": "启动前未打开串口导致首次读失败",
    "solution": "初始化前打开设备",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "测试顺序",
    "root_cause": "case B 单跑失败、A后运行通过",
    "solution": "先运行A",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "硬件限制",
    "root_cause": "板卡没有对应外设导致驱动探测失败",
    "solution": "仅在有外设板卡执行",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 18,
      "actionability": 10,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "内核差异",
    "root_cause": "内核6.x下 ioctl 返回 EINVAL",
    "solution": "回退内核版本",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "漏字段",
    "root_cause": "接口返回缺失user_id导致解析失败",
    "solution": "填充必需字段",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "占位描述",
    "root_cause": "待定位",
    "solution": "暂无",
    "anchors": {
      "specificity": 0,
      "cause_or_condition": 0,
      "actionability": 0,
      "verifiability": 0
    },
    "expected_level": "信息不足",
    "expected_pass": False,
    "synthetic": True
  },
  {
    "id": "触发有但无方案",
    "root_cause": "app后台超过30分钟恢复时白屏",
    "solution": "",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 0,
      "verifiability": 10
    },
    "expected_level": "基本有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "数据库锁",
    "root_cause": "事务未提交导致后续查询超时",
    "solution": "补充rollback",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 5
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "CI偶发",
    "root_cause": "CI特定runner报文件不存在，其他runner正常",
    "solution": "换runner执行",
    "anchors": {
      "specificity": 35,
      "cause_or_condition": 10,
      "actionability": 10,
      "verifiability": 10
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  },
  {
    "id": "兼容短句",
    "root_cause": "旧字段改名导致反序列化失败",
    "solution": "增加字段别名兼容",
    "anchors": {
      "specificity": 25,
      "cause_or_condition": 25,
      "actionability": 25,
      "verifiability": 0
    },
    "expected_level": "有效",
    "expected_pass": True,
    "synthetic": True
  }

]

def result(c, manual=False):
    scores = c["anchors"]
    total = sum(scores.values())
    return {
        "mode": "jira_lenient_v1_4", "score": total,
        "level": c["expected_level"],
        "jira_pass": c["expected_pass"] if not manual else False,
        "technical_verification": "unverified",
        "manual_review_required": manual,
        "dimension_scores": dict(scores),
        "reason": "synthetic test fixture only",
        "suggestion": ""
    }

class LenientContractTests(unittest.TestCase):
    def test_fifty_synthetic_anchors_and_thresholds(self):
        self.assertEqual(len(CASES), 50)
        for c in CASES:
            with self.subTest(case=c["id"]):
                self.assertEqual(c["expected_pass"], sum(c["anchors"].values()) >= 30)
                validate_result(result(c))

    def test_threshold_boundaries(self):
        base = result(CASES[0])
        for score, level, passed in ((0, "信息不足", False), (25, "信息不足", False),
                                     (30, "基本有效", True), (55, "基本有效", True),
                                     (60, "有效", True), (100, "有效", True)):
            anchors = next((a for a in self._anchor_combinations() if sum(a.values()) == score), None)
            if anchors is None:
                continue
            d = copy.deepcopy(base)
            d["dimension_scores"] = anchors
            d.update(score=score, level=level, jira_pass=passed)
            validate_result(d)

    @staticmethod
    def _anchor_combinations():
        from itertools import product
        from validate_jira_lenient import ANCHORS
        keys = list(ANCHORS)
        for values in product(*(sorted(ANCHORS[k]) for k in keys)):
            yield dict(zip(keys, values))

    def test_manual_review_overrides_pass(self):
        d = result(CASES[5], manual=True)
        self.assertFalse(validate_result(d)["jira_pass"])

    def test_malformed_and_overclaim_rejected(self):
        d = result(CASES[5])
        for changed in ({"score": 100}, {"jira_pass": False},
                        {"technical_verification": "assumed"},
                        {"technical_verification": "verified"},
                        {"dimension_scores": {**d["dimension_scores"], "specificity": 34}}):
            broken = copy.deepcopy(d)
            broken.update(changed)
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_result(broken)

    def test_no_length_penalty_in_contract(self):
        short = result(CASES[4])
        long = copy.deepcopy(short)
        long["reason"] = "这是一个很长的解释" * 100
        self.assertEqual(validate_result(short)["score"], validate_result(long)["score"])

if __name__ == "__main__":
    unittest.main()
