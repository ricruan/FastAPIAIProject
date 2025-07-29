import os
from docxtpl import DocxTemplate
from datetime import datetime

def generate_doc_with_jinja(template_path, output_path, context):
    """
    使用 docxtpl 生成 Word 文档
    :param template_path: 模板文件路径
    :param output_path: 输出文件路径
    :param context: 字典，包含模板变量
    """
    doc = DocxTemplate(template_path)
    doc.render(context)
    doc.save(output_path)

# 示例用法
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "template.doc")
    output_path = os.path.join(script_dir, "output_docxtpl.docx")

    # 定义替换数据（支持 Jinja2 语法）
    context = {
        "full_name": "张三",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "company": "ABC 公司",
        "items": ["项目1", "项目2", "项目3"]  # 用于循环
    }

    generate_doc_with_jinja(template_path, output_path, context)
    print(f"已生成文件: {output_path}")