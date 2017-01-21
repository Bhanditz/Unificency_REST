class Config(object):
    """
    Common configurations
    """
    UPLOAD_FOLDER_USER_PROFILE_IMAGES = 'static/users/profile_images/'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 280


    # Put any configurations here that are common across all environments

class DevelopmentConfig(Config):
    """
    Development configurations
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """
    DEBUG = False
    SQLALCHEMY_ECHO = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}