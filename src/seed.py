import asyncio
import csv
import bcrypt

from sqlalchemy import func, select

from src.infra.session import async_session_maker
from src.infra.models import Item, Role, RolePermission, User
from src.domain.enums import ItemRarity, ResourceType


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


async def seed_roles(session):
    count = await session.scalar(select(func.count()).select_from(Role))
    if count > 0:
        print(f'Roles already seeded ({count} roles), skipping')
        return

    roles = [
        Role(name="admin"),
        Role(name="moderator"),
        Role(name="user"),
    ]
    session.add_all(roles)
    await session.flush()

    for resource in ResourceType:
        session.add(RolePermission(
            role_id=roles[0].id,
            resource=resource,
            can_read=True,
            can_write=True,
            can_delete=True,
        ))

    session.add(RolePermission(
        role_id=roles[1].id,
        resource=ResourceType.ITEMS,
        can_read=True,
        can_write=True,
        can_delete=True,
    ))
    session.add(RolePermission(
        role_id=roles[1].id,
        resource=ResourceType.USERS,
        can_read=True,
        can_write=False,
        can_delete=False,
    ))
    session.add(RolePermission(
        role_id=roles[1].id,
        resource=ResourceType.ROLES,
        can_read=False,
        can_write=False,
        can_delete=False,
    ))

    session.add(RolePermission(
        role_id=roles[2].id,
        resource=ResourceType.ITEMS,
        can_read=True,
        can_write=False,
        can_delete=False,
    ))
    session.add(RolePermission(
        role_id=roles[2].id,
        resource=ResourceType.USERS,
        can_read=False,
        can_write=False,
        can_delete=False,
    ))
    session.add(RolePermission(
        role_id=roles[2].id,
        resource=ResourceType.ROLES,
        can_read=False,
        can_write=False,
        can_delete=False,
    ))


async def seed_users(session):
    count = await session.scalar(select(func.count()).select_from(User))
    if count > 0:
        print(f'Users already seeded ({count} users), skipping')
        return

    roles = await session.execute(select(Role).order_by(Role.id))
    roles = roles.scalars().all()

    users = [
        User(
            name="Admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role_id=roles[0].id,
        ),
        User(
            name="Moderator",
            email="moderator@example.com",
            password_hash=hash_password("moderator123"),
            role_id=roles[1].id,
        ),
        User(
            name="User",
            email="user@example.com",
            password_hash=hash_password("user123"),
            role_id=roles[2].id,
        ),
    ]
    session.add_all(users)
    print(f'Seeded {len(users)} users')


async def seed_items(session):
    count = await session.scalar(select(func.count()).select_from(Item))
    if count > 0:
        print(f'Items already seeded ({count} items), skipping')
        return

    with open('data/dnd_magic_items.csv', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    session.add_all([
        Item(
            name=row['name_rus'],
            type=row['type'],
            rarity=ItemRarity(row['rarity']),
            source=row['source'],
            source_name=row['source_name'],
        )
        for row in rows
    ])
    print(f'Seeded {len(rows)} items')


async def seed():
    async with async_session_maker() as session:
        await seed_roles(session)
        await seed_users(session)
        await seed_items(session)
        await session.commit()

    print('Seeding complete!')


if __name__ == '__main__':
    asyncio.run(seed())
