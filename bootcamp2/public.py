from bootcamp2.settings import REDISINFO
import redis

def get_redis_connction(db):
    return redis.Redis(host=REDISINFO['HOST'], password=REDISINFO['PASSWORD'], port=REDISINFO['PORT'], db=db)
