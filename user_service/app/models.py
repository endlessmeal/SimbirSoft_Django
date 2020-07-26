import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from passlib.hash import argon2


users = sa.Table(
    'users',
    sa.MetaData(),
    sa.Column(str(UUID(as_uuid=True)), sa.String, primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
    sa.Column('username', sa.String(50), unique=True, nullable=False),
    sa.Column('password', sa.String, nullable=False),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('age', sa.Integer, nullable=False),
    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
    ),
)


class User:

    def __init__(self, db, data, *kw):
        self.db = db
        self.username = data[0]
        self.password = data[1]
        if len(data) > 2:
            self.name = data[2]
            self.age = data[3]
        self.pass_hash = argon2.hash(data[1])

    async def check_user(self, **kw):
        async with self.db.acquire() as conn:
            s = sa.select([users]).where(users.c.username == self.username)
            return await conn.execute(s)

    async def create_user(self, **kw):
        user = await self.check_user()
        if not user.rowcount:
            async with self.db.acquire() as conn:
                await conn.execute(
                    users.insert().values(username=self.username,
                                          password=self.pass_hash,
                                          name=self.name,
                                          age=self.age))
            result = True
        else:
            result = False
        return result

    async def find_user(self, row):
        async with self.db.acquire() as conn:
            s = sa.select([users]).where(users.c.username == row)
            res = await conn.execute(s)
            return await res.fetchone()

    async def login_user(self, **kw):
        row = await self.find_user(self.username)
        password = row[2]
        if argon2.verify(self.password, password):
            return True
        else:
            return False

    async def user_info(self, **kw):
        row = await self.find_user(self.username)
        id = row[0]
        username = row[1]
        name = row[3]
        age = row[4]
        return [id, username, name, age]

