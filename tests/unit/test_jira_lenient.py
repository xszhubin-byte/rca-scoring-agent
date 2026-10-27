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
    def test_twenty_synthetic_anchors_and_thresholds(self):
        self.assertEqual(len(CASES), 20)
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
