"""
演示如何使用content_source参数控制markdown生成的HTML输入源，并集成AI进行智能数据提取。
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

async def demo_content_source_with_ai():
    """演示不同content_source选项的markdown生成效果，并使用AI进行智能数据提取。"""
    url = "https://my.oschina.net/infinilabs/blog/18692467"  # 简单演示网站
    
    print("使用不同的content_source选项进行爬取...")
    
    # 初始化AI提取器
    ai_extractor = AIExtractor()
    print(f"可用的AI提取模式: {ai_extractor.get_available_modes()}")
    print(f"可用的LLM提供商: {ai_extractor.get_available_providers()}")
    
    # --- 示例 1: 默认行为 (cleaned_html) ---
    # 使用经过爬取策略处理后的HTML
    # HTML已被清理、简化并优化以提高可读性
    default_generator = DefaultMarkdownGenerator()  # content_source="cleaned_html" 是默认值
    default_config = CrawlerRunConfig(markdown_generator=default_generator)
    
    # --- 示例 2: 原始HTML ---
    # 直接使用网页的原始HTML
    # 保留更多原始内容，但可能包含导航、广告等
    raw_generator = DefaultMarkdownGenerator(content_source="raw_html")
    raw_config = CrawlerRunConfig(markdown_generator=raw_generator)
    
    # --- 示例 3: 适配HTML ---
    # 使用为模式提取优化的预处理HTML
    # 更适合结构化数据提取，但可能丢失一些格式
    fit_generator = DefaultMarkdownGenerator(content_source="fit_html")
    fit_config = CrawlerRunConfig(markdown_generator=fit_generator)
    
    # 按顺序执行所有三个爬虫
    async with AsyncWebCrawler() as crawler:
        print("\n正在爬取网页内容...")
        
        # 默认 (cleaned_html)
        result_default = await crawler.arun(url=url, config=default_config)
        
        # 原始HTML
        result_raw = await crawler.arun(url=url, config=raw_config)
        
        # 适配HTML
        result_fit = await crawler.arun(url=url, config=fit_config)
    
    # 打印结果摘要
    print("\nMarkdown生成结果:\n")
    
    print("1. 默认 (cleaned_html):")
    print(f"   长度: {len(result_default.markdown.raw_markdown)} 字符")
    print(f"   前80个字符: {result_default.markdown.raw_markdown[:80]}...\n")
    
    print("2. 原始HTML:")
    print(f"   长度: {len(result_raw.markdown.raw_markdown)} 字符")
    print(f"   前80个字符: {result_raw.markdown.raw_markdown[:80]}...\n")
    
    print("3. 适配HTML:")
    print(f"   长度: {len(result_fit.markdown.raw_markdown)} 字符")
    print(f"   前80个字符: {result_fit.markdown.raw_markdown[:80]}...\n")
    
    # AI智能数据提取
    print("=" * 60)
    print("开始AI智能数据提取...")
    print("=" * 60)
    
    # 使用默认版本的markdown进行AI提取
    markdown_content = result_default.markdown.raw_markdown
    
    # 执行多种AI提取模式
    extraction_modes = ["structured_data", "content_summary", "key_points"]
    ai_results = {}
    
    for mode in extraction_modes:
        print(f"\n正在执行 {mode} 模式的AI提取...")
        try:
            ai_result = await ai_extractor.extract(markdown_content, mode=mode)
            ai_results[mode] = ai_result
            
            if ai_result.get("success"):
                print(f"✓ {mode} 提取成功")
                # 显示提取结果的前200个字符
                result_text = ai_result.get("result", "")
                print(f"  结果预览: {result_text[:200]}...")
            else:
                print(f"✗ {mode} 提取失败: {ai_result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"✗ {mode} 提取过程中发生异常: {e}")
            ai_results[mode] = {"error": str(e)}
    
    # 保存markdown文件到doc目录下的时间戳文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_root = Path(__file__).parent.parent  # 获取项目根目录
    output_dir = project_root / "doc" / f"crawl_results_{timestamp}"
    
    # 创建输出目录（如果不存在）
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n正在将文件保存到: {output_dir}")
    
    # 保存三种不同的markdown文件
    files_saved = []
    
    # 保存默认版本（cleaned_html）
    default_filename = f"markdown_default_{timestamp}.md"
    default_filepath = output_dir / default_filename
    with open(default_filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 默认模式 (cleaned_html) - {timestamp}\n\n")
        f.write("来源URL: https://www.oschina.net/\n\n")
        f.write(result_default.markdown.raw_markdown)
    files_saved.append(str(default_filepath))
    print(f"✓ 已保存默认版本: {default_filename}")
    
    # 保存原始HTML版本
    raw_filename = f"markdown_raw_{timestamp}.md"
    raw_filepath = output_dir / raw_filename
    with open(raw_filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 原始HTML模式 (raw_html) - {timestamp}\n\n")
        f.write("来源URL: https://www.oschina.net/\n\n")
        f.write(result_raw.markdown.raw_markdown)
    files_saved.append(str(raw_filepath))
    print(f"✓ 已保存原始HTML版本: {raw_filename}")
    
    # 保存适配HTML版本
    fit_filename = f"markdown_fit_{timestamp}.md"
    fit_filepath = output_dir / fit_filename
    with open(fit_filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 适配HTML模式 (fit_html) - {timestamp}\n\n")
        f.write("来源URL: https://www.oschina.net/\n\n")
        f.write(result_fit.markdown.raw_markdown)
    files_saved.append(str(fit_filepath))
    print(f"✓ 已保存适配HTML版本: {fit_filename}")
    
    # 保存AI提取结果
    ai_files_saved = []
    
    for mode, result in ai_results.items():
        if result.get("success"):
            ai_filename = f"ai_{mode}_{timestamp}.md"
            ai_filepath = output_dir / ai_filename
            with open(ai_filepath, 'w', encoding='utf-8') as f:
                f.write(f"# AI {mode.replace('_', ' ').title()} - {timestamp}\n\n")
                f.write("**来源URL**: https://www.oschina.net/\n\n")
                f.write(f"**提取时间**: {result.get('timestamp', timestamp)}\n\n")
                f.write(f"**LLM提供商**: {result.get('provider', 'unknown')}\n\n")
                f.write(f"## {mode.replace('_', ' ').title()}\n\n")
                f.write(result.get("result", f"无{mode}内容"))
            ai_files_saved.append(str(ai_filepath))
            print(f"✓ 已保存AI {mode}: {ai_filename}")
    
    # 展示输出差异
    print("\n" + "=" * 60)
    print("处理结果总结")
    print("=" * 60)
    
    print("\n关键要点:")
    print("- cleaned_html: 最适合可读性强、内容聚焦的场景")
    print("- raw_html: 保留更多原始内容，但可能包含噪音")
    print("- fit_html: 为模式提取和结构化数据优化")
    
    print(f"\n总共保存了 {len(files_saved)} 个markdown文件到 {output_dir}:")
    for filepath in files_saved:
        print(f"  - {Path(filepath).name}")
    
    if ai_files_saved:
        print(f"\n总共保存了 {len(ai_files_saved)} 个AI分析结果文件:")
        for filepath in ai_files_saved:
            print(f"  - {Path(filepath).name}")
    
    # AI提取结果统计
    successful_extractions = sum(1 for result in ai_results.values() if result.get("success"))
    print(f"\nAI提取统计:")
    print(f"  - 成功提取: {successful_extractions}/{len(extraction_modes)} 个模式")
    print(f"  - 使用的LLM提供商: {ai_extractor.config.get('default_provider', 'unknown')}")
    
    if successful_extractions == 0:
        print("\n⚠️  注意: 所有AI提取都失败了，请检查配置文件中的API密钥设置")
        print("   配置文件位置: config/ai_config.yaml")

if __name__ == "__main__":
    asyncio.run(demo_content_source_with_ai())