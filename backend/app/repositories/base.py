from typing import TypeVar, Generic, Type, Optional, List
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get by ID"""
        result = await self.session.get(self.model, id)
        return result
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, obj: ModelType) -> ModelType:
        """Create new record"""
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, obj: ModelType) -> ModelType:
        """Update existing record"""
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def delete(self, id: int) -> bool:
        """Delete record"""
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False
