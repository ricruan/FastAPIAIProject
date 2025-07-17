from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List, Optional, Sequence
from datetime import datetime
import uuid

from src.db.db import get_db
from src.pojo.po.userProfilePo import UserProfile
from src.dao.userProfileDao import (
    create_user_profile,
    get_profile_by_id,
    get_profile_by_user_id,
    get_profile_by_user_id_with_check,
    search_user_profiles,
    update_user_profile,
    update_user_profile_by_user_id,
    delete_user_profile,
    delete_user_profile_by_user_id,
    batch_create_user_profiles,
    get_all_user_profiles,
    get_user_profiles_by_source,
    count_user_profiles
)
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel, Field

from src.service.userProfileService import analysis_language_style

router = APIRouter(prefix="/user-profile", tags=["用户画像"])

# 创建用户画像的请求模型
class UserProfileCreate(BaseModel):
    user_id: str = Field(..., description="用户唯一标识符", example="user123456")
    user_info: Optional[str] = Field(None, description="用户基本信息", example="25岁，男性，程序员")
    source: Optional[str] = Field(None, description="用户来源渠道", example="web/ios/android")
    language_style: Optional[str] = Field(None, description="用户语言风格偏好", example="正式/随意/技术性")
    preferred_llm_style: Optional[str] = Field(None, description="用户偏好的LLM交互风格", example="简洁/详细/幽默")
    disliked_llm_style: Optional[str] = Field(None, description="用户不喜欢的LLM交互风格", example="冗长/模糊/官方")
    personality_traits: Optional[str] = Field(None, description="用户性格特征", example="外向/内向/分析型")
    behavior_profile: Optional[str] = Field(None, description="用户行为画像", example="活跃时段/交互频率")
    interpersonal_profile: Optional[str] = Field(None, description="用户人际互动偏好", example="直接/委婉/正式")
    key_events: Optional[str] = Field(None, description="用户关键事件记录", example="注册时间/重要交互时间点")
    preference_questions: Optional[str] = Field(None, description="用户偏好问题集", example="喜欢的话题/避讳的内容")
    topic_preferences: Optional[str] = Field(None, description="用户主题偏好", example="科技/体育/娱乐")
    sentiment_trend: Optional[str] = Field(None, description="用户情感倾向变化", example="积极/中立/消极")
    user_summary: Optional[str] = Field(None, description="用户综合摘要", example="技术爱好者，偏好详细解答")

    def to_po(self) -> UserProfile:
        """
        将VO转换为PO
        """
        now = datetime.now()
        return UserProfile(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            user_info=self.user_info,
            source=self.source,
            language_style=self.language_style,
            preferred_llm_style=self.preferred_llm_style,
            disliked_llm_style=self.disliked_llm_style,
            personality_traits=self.personality_traits,
            behavior_profile=self.behavior_profile,
            interpersonal_profile=self.interpersonal_profile,
            key_events=self.key_events,
            preference_questions=self.preference_questions,
            topic_preferences=self.topic_preferences,
            sentiment_trend=self.sentiment_trend,
            user_summary=self.user_summary,
            create_time=now,
            update_time=now
        )

# 批量创建用户画像的请求模型
class BatchUserProfileCreate(BaseModel):
    profiles: List[UserProfileCreate]

# 更新用户画像的请求模型
class UserProfileUpdate(BaseModel):
    user_info: Optional[str] = None
    source: Optional[str] = None
    language_style: Optional[str] = None
    preferred_llm_style: Optional[str] = None
    disliked_llm_style: Optional[str] = None
    personality_traits: Optional[str] = None
    behavior_profile: Optional[str] = None
    interpersonal_profile: Optional[str] = None
    key_events: Optional[str] = None
    preference_questions: Optional[str] = None
    topic_preferences: Optional[str] = None
    sentiment_trend: Optional[str] = None
    user_summary: Optional[str] = None


@router.get("/{profile_id}", response_model=HttpResponseModel[UserProfile])
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """
    根据ID获取用户画像

    Args:
        profile_id: 用户画像ID
        db: 数据库会话

    Returns:
        用户画像信息
    """
    profile = get_profile_by_id(db, profile_id)
    if not profile:
        return HttpResponse.error(msg=f"User profile with id {profile_id} not found")
    return HttpResponse.success(profile)

@router.get("/user/{user_id}", response_model=HttpResponseModel[UserProfile])
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    根据用户ID获取用户画像

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        用户画像信息
    """
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        return HttpResponse.error(msg=f"User profile for user {user_id} not found")
    return HttpResponse.success(profile)

@router.post("/analysis/language-style")
async def get_user_profile(param: dict, db: Session = Depends(get_db)):
    """

    """
    user_id = param.get('user_id')
    profile = get_profile_by_user_id(db, user_id)
    await analysis_language_style(session=db, profile=profile)
    return HttpResponse.success(profile)

@router.get("/", response_model=HttpResponseModel[List[UserProfile]])
async def get_all_profiles(db: Session = Depends(get_db)):
    """
    获取所有用户画像

    Args:
        db: 数据库会话

    Returns:
        用户画像列表
    """
    profiles = get_all_user_profiles(db)
    return HttpResponse.success(profiles)

@router.get("/source/{source}", response_model=HttpResponseModel[List[UserProfile]])
async def get_profiles_by_source(source: str, db: Session = Depends(get_db)):
    """
    获取特定来源的用户画像

    Args:
        source: 用户来源
        db: 数据库会话

    Returns:
        用户画像列表
    """
    profiles = get_user_profiles_by_source(db, source)
    return HttpResponse.success(profiles)

@router.get("/count", response_model=HttpResponseModel[int])
async def count_profiles(db: Session = Depends(get_db)):
    """
    统计用户画像数量

    Args:
        db: 数据库会话

    Returns:
        用户画像数量
    """
    count = count_user_profiles(db)
    return HttpResponse.success(count)

@router.post("/", response_model=HttpResponseModel[UserProfile])
async def create_profile(profile_data: UserProfileCreate, db: Session = Depends(get_db)):
    """
    创建用户画像

    Args:
        profile_data: 用户画像数据
        db: 数据库会话

    Returns:
        创建的用户画像
    """
    try:
        # 检查是否已存在该用户的画像
        existing_profile = get_profile_by_user_id(db, profile_data.user_id)
        if existing_profile:
            return HttpResponse.error(msg=f"User profile for user {profile_data.user_id} already exists")

        # 转换为PO并创建
        profile_po = profile_data.to_po()
        created_profile = create_user_profile(db, profile_po)
        return HttpResponse.success(created_profile)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/batch", response_model=HttpResponseModel[List[UserProfile]])
async def batch_create_profiles(batch_data: BatchUserProfileCreate, db: Session = Depends(get_db)):
    """
    批量创建用户画像

    Args:
        batch_data: 批量用户画像数据
        db: 数据库会话

    Returns:
        创建的用户画像列表
    """
    try:
        # 转换为PO并批量创建
        profile_pos = [profile.to_po() for profile in batch_data.profiles]
        created_profiles = batch_create_user_profiles(db, profile_pos)
        return HttpResponse.success(created_profiles)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.put("/{profile_id}", response_model=HttpResponseModel[UserProfile])
async def update_profile(profile_id: str, profile_data: UserProfileUpdate, db: Session = Depends(get_db)):
    """
    更新用户画像

    Args:
        profile_id: 用户画像ID
        profile_data: 更新的用户画像数据
        db: 数据库会话

    Returns:
        更新后的用户画像
    """
    # 转换为字典
    update_data = profile_data.model_dump(exclude_unset=True)

    # 更新用户画像
    updated_profile = update_user_profile(db, profile_id, update_data)
    if not updated_profile:
        return HttpResponse.error(msg=f"User profile with id {profile_id} not found")

    return HttpResponse.success(updated_profile)

@router.put("/user/{user_id}", response_model=HttpResponseModel[UserProfile])
async def update_profile_by_user_id(user_id: str, profile_data: UserProfileUpdate, db: Session = Depends(get_db)):
    """
    通过用户ID更新用户画像

    Args:
        user_id: 用户ID
        profile_data: 更新的用户画像数据
        db: 数据库会话

    Returns:
        更新后的用户画像
    """
    # 转换为字典
    update_data = profile_data.model_dump(exclude_unset=True)

    # 更新用户画像
    updated_profile = update_user_profile_by_user_id(db, user_id, update_data)
    if not updated_profile:
        return HttpResponse.error(msg=f"User profile for user {user_id} not found")

    return HttpResponse.success(updated_profile)

@router.delete("/{profile_id}", response_model=HttpResponseModel[bool])
async def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """
    删除用户画像

    Args:
        profile_id: 用户画像ID
        db: 数据库会话

    Returns:
        是否成功删除
    """
    result = delete_user_profile(db, profile_id)
    if not result:
        return HttpResponse.error(msg=f"User profile with id {profile_id} not found")

    return HttpResponse.success(True)

@router.delete("/user/{user_id}", response_model=HttpResponseModel[bool])
async def delete_profile_by_user_id(user_id: str, db: Session = Depends(get_db)):
    """
    通过用户ID删除用户画像

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        是否成功删除
    """
    result = delete_user_profile_by_user_id(db, user_id)
    if not result:
        return HttpResponse.error(msg=f"User profile for user {user_id} not found")

    return HttpResponse.success(True)

@router.post("/search", response_model=HttpResponseModel[List[UserProfile]])
async def search_profiles(search_params: Dict[str, Any], db: Session = Depends(get_db)):
    """
    搜索用户画像

    Args:
        search_params: 搜索参数
        db: 数据库会话

    Returns:
        符合条件的用户画像列表
    """
    try:
        results = search_user_profiles(db, search_params)
        return HttpResponse.success(results)
    except Exception as e:
        return HttpResponse.error(msg=str(e))
