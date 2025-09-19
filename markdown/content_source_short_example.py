"""
演示如何在MarkdownGenerationStrategy中使用content_source参数，并集成AI进行智能数据提取
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator

# 添加utils目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))
from utils.ai_extractor import AIExtractor

str_url = "https://my.oschina.net/u/4662964/blog/16269631"

async def demo_markdown_source_config_with_ai():
    print("\n=== 演示: 配置Markdown源 + AI智能提取 ===")

    # 初始化AI提取器
    ai_extractor = AIExtractor()
    print(f"AI提取器初始化完成，默认提供商: {ai_extractor.config.get('default_provider', 'unknown')}")

    # 示例 1: 从清理后的HTML生成markdown（默认行为）
    cleaned_md_generator = DefaultMarkdownGenerator(content_source="cleaned_html")
    config_cleaned = CrawlerRunConfig(markdown_generator=cleaned_md_generator)

    async with AsyncWebCrawler() as crawler:
        result_cleaned = await crawler.arun(url=str_url, config=config_cleaned)
        print("从清理后的HTML生成的Markdown（默认）:")
        print(f"  长度: {len(result_cleaned.markdown.raw_markdown)}")
        print(f"  开头: {result_cleaned.markdown.raw_markdown[:100]}...")

    # 示例 2: 直接从原始HTML生成markdown
    raw_md_generator = DefaultMarkdownGenerator(content_source="raw_html")
    config_raw = CrawlerRunConfig(markdown_generator=raw_md_generator)

    async with AsyncWebCrawler() as crawler:
        result_raw = await crawler.arun(url=str_url, config=config_raw)
        print("\n从原始HTML生成的Markdown:")
        print(f"  长度: {len(result_raw.markdown.raw_markdown)}")
        print(f"  开头: {result_raw.markdown.raw_markdown[:100]}...")

    # 示例 3: 从预处理的'fit' HTML生成markdown
    fit_md_generator = DefaultMarkdownGenerator(content_source="fit_html")
    config_fit = CrawlerRunConfig(markdown_generator=fit_md_generator)

    async with AsyncWebCrawler() as crawler:
        result_fit = await crawler.arun(url=str_url, config=config_fit)
        print("\n从适配HTML生成的Markdown:")
        print(f"  长度: {len(result_fit.markdown.raw_markdown)}")
        print(f"  开头: {result_fit.markdown.raw_markdown[:100]}...")
    
    # AI智能数据提取演示
    print("\n" + "=" * 50)
    print("AI智能数据提取演示")
    print("=" * 50)
    
    # 选择最佳的markdown内容进行AI分析（通常是cleaned版本）
    best_content = result_cleaned.markdown.raw_markdown
    
    # 执行AI内容摘要提取
    print("\n正在执行AI内容摘要提取...")
    try:
        summary_result = await ai_extractor.extract(best_content, mode="content_summary")
        
        if summary_result.get("success"):
            print("✓ AI内容摘要提取成功")
            summary_text = summary_result.get("result", "")
            print(f"摘要内容: {summary_text}")
        else:
            print(f"✗ AI摘要提取失败: {summary_result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"✗ AI摘要提取过程中发生异常: {e}")
        summary_result = {"error": str(e)}
    
    # 执行AI关键点提取
    print("\n正在执行AI关键点提取...")
    try:
        keypoints_result = await ai_extractor.extract(best_content, mode="key_points")
        
        if keypoints_result.get("success"):
            print("✓ AI关键点提取成功")
            keypoints_text = keypoints_result.get("result", "")
            print(f"关键点: {keypoints_text}")
        else:
            print(f"✗ AI关键点提取失败: {keypoints_result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"✗ AI关键点提取过程中发生异常: {e}")
        keypoints_result = {"error": str(e)}
    
    # 保存markdown文件到doc目录下的时间戳文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_root = Path(__file__).parent.parent  # 获取项目根目录
    output_dir = project_root / "doc" / f"crawl_results_{timestamp}"
    
    # 创建输出目录（如果不存在）
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n正在将文件保存到: {output_dir}")
    
    # 保存三种不同的markdown文件
    files_saved = []
    
    # 保存清理版本
    cleaned_filename = f"example_cleaned_{timestamp}.md"
    cleaned_filepath = output_dir / cleaned_filename
    with open(cleaned_filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 清理HTML模式 (cleaned_html) - {timestamp}\n\n")
        f.write("来源URL: " + str_url)
        f.write(result_cleaned.markdown.raw_markdown)
    files_saved.append(str(cleaned_filepath))
    print(f"✓ 已保存清理版本: {cleaned_filename}")
    
    # 保存原始版本
    raw_filename = f"example_raw_{timestamp}.md"
    raw_filepath = output_dir / raw_filename
    with open(raw_filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 原始HTML模式 (raw_html) - {timestamp}\n\n")
        f.write("来源URL: " + str_url)
        f.write(result_raw.markdown.raw_markdown)
    files_saved.append(str(raw_filepath))
    print(f"✓ 已保存原始版本: {raw_filename}")
    
    # 保存适配版本
    fit_filename = f"example_fit_{timestamp}.md"
    fit_filepath = output_dir / fit_filename
    with open(fit_filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 适配HTML模式 (fit_html) - {timestamp}\n\n")
        f.write("来源URL: " + str_url)
        f.write(result_fit.markdown.raw_markdown)
    files_saved.append(str(fit_filepath))
    print(f"✓ 已保存适配版本: {fit_filename}")
    
    # 保存AI提取结果
    ai_files_saved = []
    
    # 保存摘要结果
    if summary_result.get("success"):
        summary_filename = f"ai_summary_{timestamp}.md"
        summary_filepath = output_dir / summary_filename
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# AI内容摘要 - {timestamp}\n\n")
            f.write("**来源URL**: " + str_url)
            f.write(f"**提取时间**: {summary_result.get('timestamp', timestamp)}\n\n")
            f.write(f"**LLM提供商**: {summary_result.get('provider', 'unknown')}\n\n")
            f.write("## 内容摘要\n\n")
            f.write(summary_result.get("result", "无摘要内容"))
        ai_files_saved.append(str(summary_filepath))
        print(f"✓ 已保存AI摘要: {summary_filename}")
    
    # 保存关键点结果
    if keypoints_result.get("success"):
        keypoints_filename = f"ai_keypoints_{timestamp}.md"
        keypoints_filepath = output_dir / keypoints_filename
        with open(keypoints_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# AI关键点提取 - {timestamp}\n\n")
            f.write("**来源URL**: " + str_url)
            f.write(f"**提取时间**: {keypoints_result.get('timestamp', timestamp)}\n\n")
            f.write(f"**LLM提供商**: {keypoints_result.get('provider', 'unknown')}\n\n")
            f.write("## 关键点\n\n")
            f.write(keypoints_result.get("result", "无关键点内容"))
        ai_files_saved.append(str(keypoints_filepath))
        print(f"✓ 已保存AI关键点: {keypoints_filename}")
    
    # 输出处理结果总结
    print("\n" + "=" * 50)
    print("处理结果总结")
    print("=" * 50)
    
    print(f"\n总共保存了 {len(files_saved)} 个markdown文件到 {output_dir}:")
    for filepath in files_saved:
        print(f"  - {Path(filepath).name}")
    
    if ai_files_saved:
        print(f"\n总共保存了 {len(ai_files_saved)} 个AI分析结果文件:")
        for filepath in ai_files_saved:
            print(f"  - {Path(filepath).name}")
    
    # AI处理统计
    successful_ai_tasks = 0
    if summary_result.get("success"):
        successful_ai_tasks += 1
    if keypoints_result.get("success"):
        successful_ai_tasks += 1
    
    print(f"\nAI处理统计:")
    print(f"  - 成功完成的AI任务: {successful_ai_tasks}/2")
    print(f"  - 使用的LLM提供商: {ai_extractor.config.get('default_provider', 'unknown')}")
    
    if successful_ai_tasks == 0:
        print("\n⚠️  注意: AI提取功能未能正常工作")
        print("   请检查以下配置:")
        print("   1. config/ai_config.yaml 文件中的API密钥")
        print("   2. 网络连接是否正常")
        print("   3. LLM服务是否可用")
    else:
        print(f"\n✅ AI功能运行正常，成功完成 {successful_ai_tasks} 个智能分析任务")

if __name__ == "__main__":
    asyncio.run(demo_markdown_source_config_with_ai())