import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import FileResponse
from sqlmodel import Session

from src.db.db import get_db
from src.pojo.po.fileUploadsPo import FileUploads
from src.dao.fileUploadsDao import (
    get_file_upload_by_id,
    get_all_file_uploads,
    search_file_uploads,
    delete_file_upload,
    logical_delete_file_upload,
    create_file_upload,
    get_file_upload_by_stored_name
)
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel

from src.utils.fileUtils import generate_unique_filename

# 定义文件上传的基础路径
UPLOAD_DIR = "uploads"

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

load_dotenv()

router = APIRouter(prefix="/common/files", tags=["文件上传管理"])


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    id: str
    original_name: str
    stored_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    upload_time: datetime
    upload_ip: Optional[str] = None


@router.get("/{file_id}", response_model=HttpResponseModel[FileUploads])
async def get_file(file_id: str, db: Session = Depends(get_db)):
    """
    根据ID获取文件上传记录

    Args:
        file_id: 文件ID
        db: 数据库会话

    Returns:
        文件上传记录
    """
    file_upload = get_file_upload_by_id(db, file_id)
    if not file_upload:
        return HttpResponse.error(msg=f"文件记录 {file_id} 不存在")
    return HttpResponse.success(file_upload)


@router.get("/", response_model=HttpResponseModel[List[FileUploads]])
async def get_all_files(db: Session = Depends(get_db)):
    """
    获取所有文件上传记录

    Args:
        db: 数据库会话

    Returns:
        所有文件上传记录列表
    """
    files = get_all_file_uploads(db)
    return HttpResponse.success(files)


@router.post("/search", response_model=HttpResponseModel[List[FileUploads]])
async def search_files(search_params: Dict[str, Any] | None, db: Session = Depends(get_db)):
    """
    搜索文件上传记录

    Args:
        search_params: 搜索参数
        db: 数据库会话

    Returns:
        符合条件的文件上传记录列表
    """
    try:
        results = search_file_uploads(db, search_params)
        return HttpResponse.success(results)
    except Exception as e:
        return HttpResponse.error(msg=str(e))


@router.delete("/{file_id}", response_model=HttpResponseModel[bool])
async def delete_file(file_id: str, physical: bool = False, db: Session = Depends(get_db)):
    """
    删除文件上传记录

    Args:
        file_id: 文件ID
        physical: 是否物理删除，默认为逻辑删除
        db: 数据库会话

    Returns:
        是否成功删除
    """
    # 先获取文件记录
    file_upload = get_file_upload_by_id(db, file_id)
    if not file_upload:
        return HttpResponse.error(msg=f"文件记录 {file_id} 不存在")

    # 如果是物理删除，则同时删除文件
    if physical:
        # 构建文件完整路径
        file_path = os.path.join(UPLOAD_DIR, file_upload.file_path)

        # 尝试删除文件
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            return HttpResponse.error(msg=f"删除文件失败: {str(e)}")

        # 删除数据库记录
        result = delete_file_upload(db, file_id)
    else:
        # 逻辑删除
        result = logical_delete_file_upload(db, file_id)
        result = result is not None

    if not result:
        return HttpResponse.error(msg=f"删除文件记录失败")

    return HttpResponse.success(True)


@router.post("/upload", response_model=HttpResponseModel[FileUploadResponse])
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    client_ip: Optional[str] = Query(None, description="上传者IP地址"),
    request: Request = None
):
    """
    上传文件

    Args:
        :param file:
        :param db:
        :param client_ip:
        :param request:
    Returns:
        文件上传记录

    """
    try:


        # 获取原始文件名和扩展名
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1] if original_filename else ""
        base_filename = os.path.splitext(original_filename)[0] if original_filename else ""

        # 确定存储路径（按年月日组织）
        today = datetime.now()
        relative_path = os.path.join(
            str(today.year),
            str(today.month).zfill(2),
            str(today.day).zfill(2)
        )

        # 确保目录存在
        full_dir = os.path.join(UPLOAD_DIR, relative_path)
        os.makedirs(full_dir, exist_ok=True)

        # 生成存储文件名（处理同名文件）
        stored_name = generate_unique_filename(full_dir, base_filename, file_extension)

        # 文件完整路径
        full_path = os.path.join(full_dir, stored_name)
        relative_file_path = os.path.join(relative_path, stored_name)
        
        # 保存文件
        file_content = await file.read()
        with open(full_path, "wb") as f:
            f.write(file_content)

        # 动态获取服务基础URL（如果request对象可用）
        if request:
            # 从请求中获取服务地址（包括协议、主机和端口）
            service_base_url = f"{request.url.scheme}://{request.url.hostname}"
            if request.url.port:
                service_base_url += f":{request.url.port}"
        else:
            # 回退到静态配置的服务地址
            service_base_url = os.getenv("SERVICE_BASE_URL")
        # 构建完整的可访问URL
        file_url = f"{service_base_url}/files/{relative_file_path}"

        # 创建文件上传记录
        file_upload = FileUploads(
            id=uuid.uuid4().hex,
            original_name=file.filename,
            stored_name=stored_name,
            file_path=file_url,
            file_size=len(file_content),
            file_type=file.content_type,
            upload_ip=client_ip
        )

        # 保存到数据库
        created_file = create_file_upload(db, file_upload)

        # 转换为响应模型
        response = FileUploadResponse(
            id=created_file.id,
            original_name=created_file.original_name,
            stored_name=created_file.stored_name,
            file_path=created_file.file_path,
            file_size=created_file.file_size,
            file_type=created_file.file_type,
            upload_time=created_file.upload_time,
            upload_ip=created_file.upload_ip
        )

        return HttpResponse.success(response)

    except Exception as e:
        return HttpResponse.error(msg=f"文件上传失败: {str(e)}")


@router.get("/download/{file_id}")
async def download_file(file_id: str, db: Session = Depends(get_db)):
    """
    下载文件

    Args:
        file_id: 文件ID
        db: 数据库会话

    Returns:
        文件响应
    """
    # 获取文件记录
    file_upload = get_file_upload_by_id(db, file_id)
    if not file_upload:
        raise HTTPException(status_code=404, detail=f"文件记录 {file_id} 不存在")

    # 检查文件状态
    if file_upload.status != "1":
        raise HTTPException(status_code=404, detail=f"文件已被删除")

    # 构建文件完整路径
    file_path = os.path.join(UPLOAD_DIR, file_upload.file_path)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"文件不存在")

    # 返回文件响应
    return FileResponse(
        path=file_path,
        filename=file_upload.original_name,
        media_type=file_upload.file_type
    )


@router.get("/download/by-name/{stored_name}")
async def download_file_by_name(stored_name: str, db: Session = Depends(get_db)):
    """
    通过存储名称下载文件

    Args:
        stored_name: 存储的文件名
        db: 数据库会话

    Returns:
        文件响应
    """
    # 获取文件记录
    file_upload = get_file_upload_by_stored_name(db, stored_name)
    if not file_upload:
        raise HTTPException(status_code=404, detail=f"文件记录 {stored_name} 不存在")

    # 检查文件状态
    if file_upload.status != "1":
        raise HTTPException(status_code=404, detail=f"文件已被删除")

    # 构建文件完整路径
    file_path = os.path.join(UPLOAD_DIR, file_upload.file_path)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"文件不存在")

    # 返回文件响应
    return FileResponse(
        path=file_path,
        filename=file_upload.original_name,
        media_type=file_upload.file_type
    )
