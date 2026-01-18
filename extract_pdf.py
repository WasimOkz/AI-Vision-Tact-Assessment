import fitz

doc = fitz.open(r'd:\Vision Tact Assesment\AI_Engineer_Assessment_Task.pdf')
with open(r'd:\Vision Tact Assesment\pdf_content.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total pages: {len(doc)}\n")
    for i, page in enumerate(doc):
        f.write(f"\n--- Page {i+1} ---\n")
        f.write(page.get_text())
doc.close()
print("Done! Content written to pdf_content.txt")
