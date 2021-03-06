import web


@web.memoize
def get_db():
    if 'database_url' in web.config:
        return web.database(web.config.database_url)
    else:
        return web.database(**web.config.db_parameters)


class ResultSet:
    """Iterator wrapper over database result.

    Provides utilities like first, list etc.
    """
    def __init__(self, seq, model=web.storage):
        self.model = model
        self.seq = iter(seq)

    def list(self):
        return list(self)

    def __iter__(self):
        return self

    def __next__(self):
        return self.model(next(self.seq))
    next = __next__

    def first(self):
        """Returns the first element from the database result or None.
        """
        try:
            return next(self)
        except StopIteration:
            return None


class Model(web.storage):
    """Base model.
    """
    @classmethod
    def where(cls, **kw):
        result = get_db().where(cls.TABLE, **kw)
        return ResultSet(result, model=cls)

    @classmethod
    def find(cls, **kw):
        """Returns the first item matching the constraints specified as keywords.
        """
        return cls.where(**kw).first()

    @classmethod
    def findall(cls, **kw):
        """Returns the first item matching the constraints specified as keywords.
        """
        return cls.where(**kw).list()


class User(Model):
    TABLE = "users"

    @classmethod
    def new(cls, name, email, phone=None):
        id = get_db().insert("users", name=name, email=email, phone=phone)
        return cls.find(id=id)

    def update(self, **kw):
        get_db().update("users", where='id=$id', vars=self, **kw)
        dict.update(self, kw)


class Trainer(User):
    """Model class for Trainer.
    """
    TABLE = "trainer"

    @classmethod
    def new(cls, name, email, phone, city, **kw):
        id = get_db().insert("users", name=name, email=email, phone=phone)
        get_db().insert('trainer', user_id=id, city=city, seqname=False, **kw)
        return cls.find(id=id)

    @classmethod
    def where(cls, **kw):
        w = 'user_id=users.id'
        if kw:
            w = w + ' AND ' + web.db.sqlwhere(kw)
        result = get_db().select([cls.TABLE, 'users'],
                                 what='users.*, trainer.*', where=w)
        return ResultSet(result, model=cls)

    def update(self, **kw):
        keys = ['name', 'email', 'phone']
        d1 = dict((k, v) for k, v in kw.items() if k in keys)
        d2 = dict((k, v) for k, v in kw.items() if k not in keys)

        db = get_db()
        with db.transaction():
            User.update(self, **d1)
            db.update('trainer', where='user_id=$user_id', vars=self, **d2)
        dict.update(self, d2)


class Organization(Model):
    TABLE = "organization"

    @classmethod
    def new(cls, name, city, admin_user, role):
        id = get_db().insert("organization", name=name, city=city,
                             admin_id=admin_user.id, admin_role=role)
        return cls.find(id=id)

    def get_admin(self):
        return User.find(id=self.admin_id)

    def get_workshops(self, status=None):
        """Returns list of workshops by this organiazation.
        """
        wheres = {}
        if status:
            wheres['status'] = status
        return Workshop.findall(org_id=self.id, order='date desc', **wheres)

    def add_new_workshop(self, title, description,
                         expected_participants, date):
        return Workshop.new(self, title, description,
                            expected_participants, date)

    def is_admin(self, email):
        """Returns True of given email is an admin of this org.
        """
        if not email:
            return False

        # Admin user is admin of every org
        if web.config.get('admin_user') == email:
            return True

        admin = self.get_admin()
        if admin and admin.email == email:
            return True

        return False

class Workshop(Model):
    TABLE = "workshop"

    @classmethod
    def new(cls, org, title, description, expected_participants, date):
        id = get_db().insert("workshop",
                             org_id=org.id,
                             title=title,
                             description=description,
                             expected_participants=expected_participants,
                             date=date)
        return cls.find(id=id)

    def get_org(self):
        return Organization.find(id=self.org_id)
