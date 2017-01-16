class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True
    BUNDLE_ERRORS =True
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 280

class ProductionConfig(Config):
    """
    Production configurations
    """
    BUNDLE_ERRORS = True
    DEBUG = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 280

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}