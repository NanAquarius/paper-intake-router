#!/usr/bin/env python3
import json
from pathlib import Path
from build_task_sheet import normalize

CASES = [
    {
        "name": "zh-degree-full",
        "payload": {
            "paperType": "学位论文",
            "degreeLevel": "硕士",
            "discipline": "计算机科学与技术",
            "topic": "基于 RAG 的企业知识问答系统研究",
            "style": "GB/T 7714",
            "targetWords": "2.5w",
            "language": "zh",
            "deliveryGoal": "pdf_with_sources",
        },
    },
    {
        "name": "zh-course-minimal",
        "payload": {
            "paperType": "课程论文",
            "courseName": "机器学习导论",
            "topic": "大模型在教育场景中的应用",
            "language": "zh",
        },
    },
    {
        "name": "en-degree-minimal",
        "payload": {
            "paperType": "thesis",
            "degreeLevel": "master",
            "discipline": "computer science",
            "topic": "Retrieval-Augmented Generation for enterprise QA",
            "language": "en",
            "deliveryGoal": "reproducible_pdf",
        },
    },
]


def main():
    out = []
    for c in CASES:
        n = normalize(c["payload"])
        out.append({"name": c["name"], "result": n})
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
