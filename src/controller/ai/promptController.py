from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List, Optional, Sequence
from datetime import datetime
import uuid

from src.db.db import get_db
from src.pojo.po.promptPo import Prompt
from src.dao.promptDao import (
    create_prompt,
    get_prompt_by_id,
    get_prompt_by_code,
    get_prompt_by_code_with_check,
    search_prompts,
    update_prompt,
    update_prompt_by_code,
    delete_prompt,
    delete_prompt_by_code,
    batch_create_prompts,
    get_all_prompts,
    get_prompts_by_category,
    get_prompts_by_model_type,
    get_prompts_by_agent_code,
    get_prompts_by_status,
    increment_usage_count,
    increment_usage_count_by_code,
    count_prompts,
    count_prompts_by_category,
    count_prompts_by_status
)
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel

router = APIRouter(prefix="/ai/prompt", tags=["Prompt"])

# 创建提示词的请求模型
class PromptCreate(BaseModel):
    code: str
    name: str
    content: str
    description: Optional[str] = None
    placeholder_template: Optional[str] = None
    model_type: Optional[str] = None
    agent_code: Optional[str] = None
    status: str = "1"
    creator_id: Optional[str] = None
    category: Optional[str] = None

    def to_po(self) -> Prompt:
        """
        将VO转换为PO
        """
        now = datetime.now()
        return Prompt(
            id=str(uuid.uuid4()),
            code=self.code,
            name=self.name,
            content=self.content,
            description=self.description,
            placeholder_template=self.placeholder_template,
            created_at=now,
            updated_at=now,
            model_type=self.model_type,
            agent_code=self.agent_code,
            usage_count=0,
            last_called_at=None,
            status=self.status,
            creator_id=self.creator_id,
            modifier_id=self.creator_id,
            category=self.category
        )

# 批量创建提示词的请求模型
class BatchPromptCreate(BaseModel):
    prompts: List[PromptCreate]

# 更新提示词的请求模型
class PromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    placeholder_template: Optional[str] = None
    model_type: Optional[str] = None
    agent_code: Optional[str] = None
    status: Optional[str] = None
    modifier_id: Optional[str] = None
    category: Optional[str] = None


@router.get("/{prompt_id}", response_model=HttpResponseModel[Prompt])
async def get_prompt(prompt_id: str, db: Session = Depends(get_db)):
    """
    根据ID获取提示词

    Args:
        prompt_id: 提示词ID
        db: 数据库会话

    Returns:
        提示词信息
    """
    prompt = get_prompt_by_id(db, prompt_id)
    if not prompt:
        return HttpResponse.error(msg=f"Prompt with id {prompt_id} not found")
    return HttpResponse.success(prompt)

@router.get("/code/{code}", response_model=HttpResponseModel[Prompt])
async def get_prompt_by_code_endpoint(code: str, db: Session = Depends(get_db)):
    """
    根据编码获取提示词
    
    Args:
        code: 提示词编码
        db: 数据库会话
        
    Returns:
        提示词信息
    """
    prompt = get_prompt_by_code(db, code)
    if not prompt:
        return HttpResponse.error(msg=f"Prompt with code {code} not found")
    return HttpResponse.success(prompt)

@router.get("/", response_model=HttpResponseModel[List[Prompt]])
async def get_all_prompts_endpoint(db: Session = Depends(get_db)):
    """
    获取所有提示词
    
    Args:
        db: 数据库会话
        
    Returns:
        提示词列表
    """
    prompts = get_all_prompts(db)
    return HttpResponse.success(prompts)

@router.get("/category/{category}", response_model=HttpResponseModel[List[Prompt]])
async def get_prompts_by_category_endpoint(category: str, db: Session = Depends(get_db)):
    """
    获取特定分类的提示词
    
    Args:
        category: 提示词分类
        db: 数据库会话
        
    Returns:
        提示词列表
    """
    prompts = get_prompts_by_category(db, category)
    return HttpResponse.success(prompts)

@router.get("/model-type/{model_type}", response_model=HttpResponseModel[List[Prompt]])
async def get_prompts_by_model_type_endpoint(model_type: str, db: Session = Depends(get_db)):
    """
    获取特定模型类型的提示词
    
    Args:
        model_type: 模型类型
        db: 数据库会话
        
    Returns:
        提示词列表
    """
    prompts = get_prompts_by_model_type(db, model_type)
    return HttpResponse.success(prompts)

@router.get("/agent-code/{agent_code}", response_model=HttpResponseModel[List[Prompt]])
async def get_prompts_by_agent_code_endpoint(agent_code: str, db: Session = Depends(get_db)):
    """
    获取特定Agent编码的提示词
    
    Args:
        agent_code: Agent编码
        db: 数据库会话
        
    Returns:
        提示词列表
    """
    prompts = get_prompts_by_agent_code(db, agent_code)
    return HttpResponse.success(prompts)

@router.get("/status/{status}", response_model=HttpResponseModel[List[Prompt]])
async def get_prompts_by_status_endpoint(status: str, db: Session = Depends(get_db)):
    """
    获取特定状态的提示词
    
    Args:
        status: 状态
        db: 数据库会话
        
    Returns:
        提示词列表
    """
    prompts = get_prompts_by_status(db, status)
    return HttpResponse.success(prompts)

@router.get("/count", response_model=HttpResponseModel[int])
async def count_prompts_endpoint(db: Session = Depends(get_db)):
    """
    统计提示词数量
    
    Args:
        db: 数据库会话
        
    Returns:
        提示词数量
    """
    count = count_prompts(db)
    return HttpResponse.success(count)

@router.get("/count/category/{category}", response_model=HttpResponseModel[int])
async def count_prompts_by_category_endpoint(category: str, db: Session = Depends(get_db)):
    """
    统计特定分类的提示词数量
    
    Args:
        category: 提示词分类
        db: 数据库会话
        
    Returns:
        提示词数量
    """
    count = count_prompts_by_category(db, category)
    return HttpResponse.success(count)

@router.get("/count/status/{status}", response_model=HttpResponseModel[int])
async def count_prompts_by_status_endpoint(status: str, db: Session = Depends(get_db)):
    """
    统计特定状态的提示词数量
    
    Args:
        status: 状态
        db: 数据库会话
        
    Returns:
        提示词数量
    """
    count = count_prompts_by_status(db, status)
    return HttpResponse.success(count)

@router.post("/", response_model=HttpResponseModel[Prompt])
async def create_prompt_endpoint(prompt_data: PromptCreate, db: Session = Depends(get_db)):
    """
    创建提示词
    
    Args:
        prompt_data: 提示词数据
        db: 数据库会话
        
    Returns:
        创建的提示词
    """
    try:
        # 检查是否已存在该编码的提示词
        existing_prompt = get_prompt_by_code(db, prompt_data.code)
        if existing_prompt:
            return HttpResponse.error(msg=f"Prompt with code {prompt_data.code} already exists")
        
        # 转换为PO并创建
        prompt_po = prompt_data.to_po()
        created_prompt = create_prompt(db, prompt_po)
        return HttpResponse.success(created_prompt)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/batch", response_model=HttpResponseModel[List[Prompt]])
async def batch_create_prompts_endpoint(batch_data: BatchPromptCreate, db: Session = Depends(get_db)):
    """
    批量创建提示词
    
    Args:
        batch_data: 批量提示词数据
        db: 数据库会话
        
    Returns:
        创建的提示词列表
    """
    try:
        # 转换为PO并批量创建
        prompt_pos = [prompt.to_po() for prompt in batch_data.prompts]
        created_prompts = batch_create_prompts(db, prompt_pos)
        return HttpResponse.success(created_prompts)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.put("/{prompt_id}", response_model=HttpResponseModel[Prompt])
async def update_prompt_endpoint(prompt_id: str, prompt_data: PromptUpdate, db: Session = Depends(get_db)):
    """
    更新提示词
    
    Args:
        prompt_id: 提示词ID
        prompt_data: 更新的提示词数据
        db: 数据库会话
        
    Returns:
        更新后的提示词
    """
    # 转换为字典
    update_data = prompt_data.model_dump(exclude_unset=True)
    
    # 更新提示词
    updated_prompt = update_prompt(db, prompt_id, update_data)
    if not updated_prompt:
        return HttpResponse.error(msg=f"Prompt with id {prompt_id} not found")
    
    return HttpResponse.success(updated_prompt)

@router.put("/code/{code}", response_model=HttpResponseModel[Prompt])
async def update_prompt_by_code_endpoint(code: str, prompt_data: PromptUpdate, db: Session = Depends(get_db)):
    """
    通过编码更新提示词
    
    Args:
        code: 提示词编码
        prompt_data: 更新的提示词数据
        db: 数据库会话
        
    Returns:
        更新后的提示词
    """
    # 转换为字典
    update_data = prompt_data.model_dump(exclude_unset=True)
    
    # 更新提示词
    updated_prompt = update_prompt_by_code(db, code, update_data)
    if not updated_prompt:
        return HttpResponse.error(msg=f"Prompt with code {code} not found")
    
    return HttpResponse.success(updated_prompt)

@router.delete("/{prompt_id}", response_model=HttpResponseModel[bool])
async def delete_prompt_endpoint(prompt_id: str, db: Session = Depends(get_db)):
    """
    删除提示词
    
    Args:
        prompt_id: 提示词ID
        db: 数据库会话
        
    Returns:
        是否成功删除
    """
    result = delete_prompt(db, prompt_id)
    if not result:
        return HttpResponse.error(msg=f"Prompt with id {prompt_id} not found")
    
    return HttpResponse.success(True)

@router.delete("/code/{code}", response_model=HttpResponseModel[bool])
async def delete_prompt_by_code_endpoint(code: str, db: Session = Depends(get_db)):
    """
    通过编码删除提示词
    
    Args:
        code: 提示词编码
        db: 数据库会话
        
    Returns:
        是否成功删除
    """
    result = delete_prompt_by_code(db, code)
    if not result:
        return HttpResponse.error(msg=f"Prompt with code {code} not found")
    
    return HttpResponse.success(True)

@router.post("/search", response_model=HttpResponseModel[List[Prompt]])
async def search_prompts_endpoint(search_params: Dict[str, Any], db: Session = Depends(get_db)):
    """
    搜索提示词
    
    Args:
        search_params: 搜索参数
        db: 数据库会话
        
    Returns:
        符合条件的提示词列表
    """
    try:
        results = search_prompts(db, search_params)
        return HttpResponse.success(results)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/increment-usage/{prompt_id}", response_model=HttpResponseModel[Prompt])
async def increment_usage_count_endpoint(prompt_id: str, db: Session = Depends(get_db)):
    """
    增加提示词使用次数
    
    Args:
        prompt_id: 提示词ID
        db: 数据库会话
        
    Returns:
        更新后的提示词
    """
    updated_prompt = increment_usage_count(db, prompt_id)
    if not updated_prompt:
        return HttpResponse.error(msg=f"Prompt with id {prompt_id} not found")
    
    return HttpResponse.success(updated_prompt)

@router.post("/increment-usage/code/{code}", response_model=HttpResponseModel[Prompt])
async def increment_usage_count_by_code_endpoint(code: str, db: Session = Depends(get_db)):
    """
    通过编码增加提示词使用次数
    
    Args:
        code: 提示词编码
        db: 数据库会话
        
    Returns:
        更新后的提示词
    """
    updated_prompt = increment_usage_count_by_code(db, code)
    if not updated_prompt:
        return HttpResponse.error(msg=f"Prompt with code {code} not found")
    
    return HttpResponse.success(updated_prompt)
