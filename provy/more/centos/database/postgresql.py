#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Roles in this namespace are meant to provide PostgreSQL database management utilities for CentOS distributions.
'''
from fabric.context_managers import settings, cd

from provy.more.base.database import postgresql
from provy.more.centos.package.yum import YumRole


class PostgreSQLRole(postgresql.PostgreSQLRole):
    '''
    This role provides PostgreSQL database management utilities for CentOS distributions.
    <em>Sample usage</em>
    <pre class="sh_python">
        from provy.core import Role
        from provy.more.centos import PostgreSQLRole

        class MySampleRole(Role):
            def provision(self):
                with self.using(PostgreSQLRole) as role:
                    role.ensure_user("john")
                    role.ensure_database("foo", owner="john")

    </pre>
    '''
    def provision(self):
        '''
        Installs PostgreSQL and its dependencies. This method should be called upon if overriden in base classes, or PostgreSQL won't work properly in the remote server.
        <em>Sample usage</em>
        <pre class="sh_python">
            class MySampleRole(Role):
                def provision(self):
                    self.provision_role(PostgreSQLRole) # no need to call this if using with block.
        </pre>
        '''
        with self.using(YumRole) as role:
            role.ensure_package_installed('postgresql-server')
            role.ensure_package_installed('postgresql-devel')

        self._ensure_initialized()
        self._ensure_running()
        self._run_on_startup()

    def _execute(self, *args, **kwargs):
        with cd('/var/lib/pgsql') as test:
            return super(PostgreSQLRole, self)._execute(*args, **kwargs)

    def _is_db_initialized(self):
        pgdata = '/var/lib/pgsql/data'
        return self.execute('ls -A %s' % pgdata, sudo=True, stdout=False)

    def _ensure_initialized(self):
        if not self._is_db_initialized():
            return(self.execute("service postgresql initdb", sudo=True))
        return True

    def _is_running(self):
        with settings(warn_only=True):
            status = self.execute('service postgresql status', sudo=True)
            return 'running' in status

    def _ensure_running(self):
        if not self._is_running():
            return self.execute('service postgresql start', sudo=True)
        return True

    def _will_start_on_boot(self):
        pkg_list = self.execute('chkconfig --list', sudo=True, stdout=False)
        return 'postgresql' in pkg_list

    def _run_on_startup(self):
        if not self._will_start_on_boot():
            self.execute('chkconfig --add postgresql', sudo=True)
            self.execute('chkconfig postgresql on', sudo=True)
