import traceback
import zipfile
from io import BytesIO
from typing import List, Dict
import random
from PIL import Image
from pdf2image import convert_from_bytes
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI()

# pdf 转换 为 图片 耗时
# 异步执行
# 假设传入pdf 有1000页怎么办？

async def pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[Dict]:
    """Convert PDF pages to high-resolution images preserving original dimensions.

    Args:
        pdf_bytes: PDF file bytes
        dpi: Resolution in dots per inch (default 300)

    Returns:
        List of dictionaries containing image data and metadata for each page
    """
    try:
        # Convert PDF to images with high resolution
        images = convert_from_bytes(
            pdf_bytes,
            dpi=dpi,
            fmt='jpeg',
            thread_count=4,
            transparent=False,
            grayscale=False,
            size=None,  # Preserve original size
            strict=False
        )

        results = []
        # 并行
        for i, image in enumerate(images):
            # Save image to bytes buffer
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)

            # Get original PDF page size in inches (approximate)
            width_inch = image.width / dpi
            height_inch = image.height / dpi

            results.append({
                'page_number': i + 1,
                'image': buffer,
                'content_type': 'image/jpeg',
                'width': image.width,
                'height': image.height,
                'dpi': dpi,
                'width_inch': width_inch,
                'height_inch': height_inch,
                'size_bytes': buffer.getbuffer().nbytes
            })

        return results

    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")


@app.post("/pdf-to-images")
async def convert_pdf_to_images(file: UploadFile = File(...)):
    """Endpoint that accepts a PDF and returns all pages as images"""
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    print("111")
    pdf_bytes = await file.read()
    print("222")
    images_data = await pdf_to_images(pdf_bytes, dpi=300)
    print("333")

    # Return first page as example (you could modify to return all pages)
    first_page = images_data[0]
    return StreamingResponse(
        first_page['image'],
        media_type=first_page['content_type'],
        headers={
            'X-Page-Number': str(first_page['page_number']),
            'X-Width': str(first_page['width']),
            'X-Height': str(first_page['height']),
            'X-DPI': str(first_page['dpi'])
        }
    )

@app.post("/pdf-to-all-images")
async def convert_pdf_to_all_images(file: UploadFile = File(...)):
    """Endpoint that returns all pages as downloadable images"""
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        pdf_bytes = await file.read()
        images_data = await pdf_to_images(pdf_bytes, dpi=300)

        # Create a ZIP file containing all images
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for page in images_data:
                zip_file.writestr(
                    f"page_{page['page_number']}.jpg",
                    page['image'].getvalue()
                )
        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                'Content-Disposition': 'attachment; filename=converted_pages.zip'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))