from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class Postgres:
    db_name: str
    db_user: str
    db_pass: str
    db_host: str

    @staticmethod
    def from_env(env: Env):
        db_name = env.str("POSTGRES_DB")
        db_user = env.str("POSTGRES_USER")
        db_pass = env.str("POSTGRES_PASSWORD")
        db_host = env.str("POSTGRES_HOST")
        return Postgres(
            db_name=db_name, db_user=db_user, db_pass=db_pass, db_host=db_host
        )


@dataclass
class Redis:
    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return Redis(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class Secrets:
    auth: str

    @staticmethod
    def from_env(env: Env):
        auth = env.str("AUTH_SECRET")

        return Secrets(auth=auth)


@dataclass
class Config:
    postgres: Postgres
    redis: Redis
    secrets: Secrets


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        postgres=Postgres.from_env(env),
        redis=Redis.from_env(env),
        secrets=Secrets.from_env(env),
    )
