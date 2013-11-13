from django.conf import settings

class MasterSlaveRouter(object):
    def db_for_read(self, model, **hints):
        return settings.SLAVE

    def db_for_write(self, model, **hints):
        return settings.MASTER

    def allow_relation(self, obj1, obj2, **hints):
        db_list = (settings.MASTER, settings.SLAVE)
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_syncdb(self, db, model):
        return True
