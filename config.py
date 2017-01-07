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

class ProductionConfig(Config):
    """
    Production configurations
    """
    BUNDLE_ERRORS = True
    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}