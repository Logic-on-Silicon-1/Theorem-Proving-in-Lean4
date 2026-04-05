import os
import requests
from readability import Document
from markdownify import markdownify as md
import re

def sanitize_filename(filename):
    """파일명으로 사용할 수 없는 특수문자 제거 및 정제"""
    return re.sub(r'[\\/*?:"<>|]', "", filename).strip().replace(" ", "_")

def save_webpage_to_markdown(url_list_file):
    # 1. urls.txt 파일 읽기
    if not os.path.exists(url_list_file):
        print(f"Error: {url_list_file} 파일이 존재하지 않습니다.")
        return

    with open(url_list_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    # 저장할 폴더 생성 (출력용)
    output_dir = "../markdown"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for url in urls:
        try:
            print(f"작업 중: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 2. 본문 추출 (readability)
            doc = Document(response.text)
            title = doc.title()
            content_html = doc.summary()

            # 3. 마크다운 변환 (markdownify)
            # Lean 코드 블록 유지 및 제목 스타일 설정
            markdown_content = md(content_html, heading_style="ATX")

            # 4. 파일명 결정 (URL 마지막 단어 또는 제목 활용)
            file_base_name = url.split("/")[-1].replace(".html", "")
            if not file_base_name or file_base_name == "":
                file_base_name = sanitize_filename(title)
            
            file_path = os.path.join(output_dir, f"{file_base_name}.md")

            # 5. 파일 저장
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(markdown_content)
            
            print(f"✅ 저장 완료: {file_path}")

        except Exception as e:
            print(f"❌ 실패 ({url}): {e}")

if __name__ == "__main__":
    # urls.txt 파일이 같은 경로에 있어야 합니다.
    save_webpage_to_markdown("urls.txt")