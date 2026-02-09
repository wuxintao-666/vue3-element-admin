#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的文件夹结构
"""

import os
import json

def test_folder_structure():
    """测试新的文件夹结构"""
    print("📁 测试新的文件夹结构")
    print("=" * 50)

    # 检查现有的章节文件夹
    chapter_dirs = [d for d in os.listdir('.') if d.startswith('chapter_') and os.path.isdir(d)]

    if not chapter_dirs:
        print("❌ 未找到任何章节文件夹")
        return False

    print(f"📂 发现 {len(chapter_dirs)} 个章节文件夹:")
    for chapter_dir in chapter_dirs:
        print(f"  📁 {chapter_dir}")

    print("-" * 50)

    # 检查每个章节文件夹的结构
    for chapter_dir in chapter_dirs:
        print(f"\n🔍 检查章节: {chapter_dir}")

        chapter_path = os.path.join('.', chapter_dir)

        # 检查knowledge子文件夹
        knowledge_dir = os.path.join(chapter_path, 'knowledge')
        if os.path.exists(knowledge_dir):
            print(f"  ✅ knowledge文件夹存在")

            content_file = os.path.join(knowledge_dir, 'content.json')
            if os.path.exists(content_file):
                print(f"  ✅ content.json存在")

                # 读取并验证JSON
                try:
                    with open(content_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    print(f"  📊 包含键: {list(data.keys())}")
                    if 'levels' in data:
                        print(f"  📚 级别数量: {len(data['levels'])}")

                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON解析失败: {e}")
                except Exception as e:
                    print(f"  ❌ 文件读取失败: {e}")
            else:
                print(f"  ❌ content.json不存在")
        else:
            print(f"  ❌ knowledge文件夹不存在")

        # 检查test子文件夹
        test_dir = os.path.join(chapter_path, 'test')
        if os.path.exists(test_dir):
            print(f"  ✅ test文件夹存在")

            content_file = os.path.join(test_dir, 'content.json')
            if os.path.exists(content_file):
                print(f"  ✅ content.json存在")

                # 读取并验证JSON
                try:
                    with open(content_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    print(f"  📊 包含键: {list(data.keys())}")
                    if 'checkpoints' in data:
                        print(f"  🎯 检查点数量: {len(data['checkpoints'])}")

                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON解析失败: {e}")
                except Exception as e:
                    print(f"  ❌ 文件读取失败: {e}")
            else:
                print(f"  ❌ content.json不存在")
        else:
            print(f"  ❌ test文件夹不存在")

    print("-" * 50)

    # 检查course_generation_results.json
    results_file = "course_generation_results_v2.json"
    if os.path.exists(results_file):
        print(f"📋 检查结果文件: {results_file}")

        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)

            if 'chapters' in results:
                print(f"  📚 章节数量: {len(results['chapters'])}")

                for i, chapter in enumerate(results['chapters']):
                    print(f"  {i+1}. {chapter.get('chapter', 'Unknown')}")
                    print(f"     🆔 ID: {chapter.get('chapter_id', 'N/A')}")
                    print(f"     📁 知识点: {chapter.get('knowledge_file', 'N/A')}")
                    print(f"     🧪 测试题: {chapter.get('test_file', 'N/A')}")

        except json.JSONDecodeError as e:
            print(f"  ❌ 结果文件JSON解析失败: {e}")
        except Exception as e:
            print(f"  ❌ 结果文件读取失败: {e}")
    else:
        print(f"❌ 结果文件不存在: {results_file}")

    print("-" * 50)
    print("🎯 文件夹结构说明:")
    print("📂 chapter_{id}/")
    print("  ├── 📁 knowledge/")
    print("  │   └── 📄 content.json (知识点)")
    print("  └── 📁 test/")
    print("      └── 📄 content.json (测试题)")

    return True

if __name__ == "__main__":
    test_folder_structure()