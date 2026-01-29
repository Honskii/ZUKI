import tomllib
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from zuki.plugin import Plugin
from .base import Base
from .middlewares.outer import OuterMiddleware
from .uow import UnitOfWork

class DBManager(Plugin):
    name = "db_manager"
    default_config_dir = "default_configs/"
    config_dir_path: Path
    config = {}

    async def on_load(self):
        self.config_manager.ensure_plugin_configs(self)
        self.config_path = self.config_manager.get_plugin_config_path(self.name)
        self.config = await self.load_config("config.toml")

        self.engine = create_async_engine(
            await self._assemble_connection(),
            future=True
        )
        self.sessionmaker = async_sessionmaker(
            self.engine,
            autoflush=False,
            expire_on_commit=False
        )

        self.app.register_service(f"{self.name}:engine", self.engine)
        self.app.register_service(f"{self.name}:base", Base)
        self.app.register_service(
            f"{self.name}:uow_factory",
            lambda: UnitOfWork(self.sessionmaker)
        )

        self.app.add_dispatcher_middleware(
            OuterMiddleware(lambda: UnitOfWork(self.sessionmaker))
        )

    async def on_startup(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def load_config(self, conf_file_path: str):
        with open(self.config_path / conf_file_path, "rb") as file:
            return tomllib.load(file)

    async def _assemble_connection(self):
        database_config = self.config.get("database", {})
        async_driver = database_config.get("async_driver", "")
        user = database_config.get("user", "")
        password = database_config.get("password", "")
        host = database_config.get("host", "localhost")
        port = database_config.get("port", 5432)
        db_name = database_config.get("db_name", "")

        return f"{async_driver}://{user}:{password}@{host}:{port}/{db_name}"