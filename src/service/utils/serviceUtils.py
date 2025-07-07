

def service_func_after_execution(callback=None):
    """
    service函数执行后回调函数
    :param callback:回调函数，在commit后执行
    :return:
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)  # 执行原函数
            # 从 kwargs 中获取 session 并提交
            if 'session' in kwargs:
                session = kwargs['session']
                if hasattr(session, 'commit'):  # 检查是否有 commit 方法
                    session.commit()


            if callback is not None:
                callback()
            return result

        return wrapper

    return decorator
