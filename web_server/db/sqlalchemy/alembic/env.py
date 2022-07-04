from logging import config as log_config

from alembic import context
from oslo_db.sqlalchemy import enginefacade

from web_server.db.sqlalchemy import models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
log_config.fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = models.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    engine = enginefacade.writer.get_engine()
    with engine.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
