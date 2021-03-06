# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2013 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <http://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from trans.models import SubProject
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.conf import settings
from weblate import appsettings
from trans.util import HAS_LIBRAVATAR
from accounts.forms import HAS_ICU
import weblate
import django

import subprocess
import hashlib
import os

# List of default domain names on which warn user
DEFAULT_DOMAINS = ('example.net', 'example.com')

# SSH key files
KNOWN_HOSTS_FILE = os.path.expanduser('~/.ssh/known_hosts')
RSA_KEY_FILE = os.path.expanduser('~/.ssh/id_rsa.pub')


@staff_member_required
def report(request):
    '''
    Provides report about git status of all repos.
    '''
    return render_to_response("admin/report.html", RequestContext(request, {
        'subprojects': SubProject.objects.all()
    }))


@staff_member_required
def performance(request):
    '''
    Shows performance tuning tips.
    '''
    checks = []
    # Check for debug mode
    checks.append((
        _('Debug mode'),
        not settings.DEBUG,
        'production-debug',
    ))
    # Check for domain configuration
    checks.append((
        _('Site domain'),
        Site.objects.get_current().domain not in DEFAULT_DOMAINS,
        'production-site',
    ))
    # Check database being used
    checks.append((
        _('Database backend'),
        "sqlite" not in settings.DATABASES['default']['ENGINE'],
        'production-database',
    ))
    # Check configured admins
    checks.append((
        _('Site administrator'),
        len(settings.ADMINS) > 0,
        'production-admins',
    ))
    # Check offloading indexing
    checks.append((
        # Translators: Indexing is postponed to cron job
        _('Indexing offloading'),
        appsettings.OFFLOAD_INDEXING,
        'production-indexing',
    ))
    # Check for sane caching
    cache = settings.CACHES['default']['BACKEND'].split('.')[-1]
    if cache in ['MemcachedCache', 'DatabaseCache']:
        # We consider these good
        cache = True
    elif cache in ['DummyCache']:
        # This one is definitely bad
        cache = False
    else:
        # These might not be that bad
        cache = None
    checks.append((
        _('Django caching'),
        cache,
        'production-cache',
    ))
    # Check email setup
    default_mails = (
        'root@localhost',
        'webmaster@localhost',
        'noreply@weblate.org'
    )
    checks.append((
        _('Email addresses'),
        (
            settings.SERVER_EMAIL not in default_mails
            and settings.DEFAULT_FROM_EMAIL not in default_mails
        ),
        'production-email',
    ))
    checks.append((
        _('Federated avatar support'),
        HAS_LIBRAVATAR,
        'production-avatar',
    ))
    checks.append((
        _('PyICU library'),
        HAS_ICU,
        'production-pyicu',
    ))
    if django.VERSION > (1, 5):
        checks.append((
            _('Allowed hosts'),
            len(settings.ALLOWED_HOSTS) > 0,
            'production-hosts',
        ))
    return render_to_response(
        "admin/performance.html",
        RequestContext(
            request,
            {
                'checks': checks,
            }
        )
    )


def parse_hosts_line(line):
    '''
    Parses single hosts line into tuple host, key fingerprint.
    '''
    host, dummy, key = line.strip().partition(' ssh-rsa ')
    fp_plain = hashlib.md5(key.decode('base64')).hexdigest()
    fingerprint = ':'.join(
        [a + b for a, b in zip(fp_plain[::2], fp_plain[1::2])]
    )
    if host.startswith('|1|'):
        # Translators: placeholder SSH hashed hostname
        host = _('[hostname hashed]')
    return (host, fingerprint)


def get_host_keys():
    '''
    Returns list of host keys.
    '''
    try:
        result = []
        with open(KNOWN_HOSTS_FILE, 'r') as handle:
            for line in handle:
                if ' ssh-rsa ' not in line:
                    continue
                result.append(parse_hosts_line(line))
    except IOError:
        return []

    return result


@staff_member_required
def ssh(request):
    '''
    Show information and manipulate with SSH key.
    '''
    # Check whether we can generate SSH key
    try:
        ret = subprocess.check_call(['which', 'ssh-keygen'])
        can_generate = (ret == 0 and not os.path.exists(RSA_KEY_FILE))
    except:
        can_generate = False

    # Grab action type
    action = request.POST.get('action', None)

    # Generate key if it does not exist yet
    if can_generate and action == 'generate':
        # Create directory if it does not exist
        key_dir = os.path.dirname(RSA_KEY_FILE)
        if not os.path.exists(key_dir):
            os.makedirs(key_dir)

        # Try generating key
        try:
            subprocess.check_output(
                [
                    'ssh-keygen', '-q',
                    '-N', '',
                    '-C', 'Weblate',
                    '-t', 'rsa',
                    '-f', RSA_KEY_FILE[:-4]
                ],
                stderr=subprocess.STDOUT,
            )
            messages.info(request, _('Created new SSH key.'))
        except subprocess.CalledProcessError as exc:
            messages.error(
                request,
                _('Failed to generate key: %s') % exc.output
            )

    # Read key data if it exists
    if os.path.exists(RSA_KEY_FILE):
        key_data = file(RSA_KEY_FILE).read()
        key_type, key_fingerprint, key_id = key_data.strip().split(None, 2)
        key = {
            'key': key_data,
            'type': key_type,
            'fingerprint': key_fingerprint,
            'id': key_id,
        }
    else:
        key = None

    # Add host key
    if action == 'add-host':
        host = request.POST.get('host', '')
        if len(host) == 0:
            messages.error(request, _('Invalid host name given!'))
        else:
            output = subprocess.check_output(['ssh-keyscan', host])
            keys = [
                line
                for line in output.splitlines()
                if ' ssh-rsa ' in line
            ]
            for key in keys:
                host, fingerprint = parse_hosts_line(key)
                messages.warning(
                    request,
                    _(
                        'Added host key for %(host)s with fingerprint '
                        '%(fingerprint)s, please verify that it is correct.'
                    ) % {
                        'host': host,
                        'fingerprint': fingerprint,
                    }
                )
            with open(KNOWN_HOSTS_FILE, 'a') as handle:
                for key in keys:
                    handle.write('%s\n' % key)

    return render_to_response("admin/ssh.html", RequestContext(request, {
        'public_key': key,
        'can_generate': can_generate,
        'host_keys': get_host_keys(),
        'ssh_docs': weblate.get_doc_url('admin', 'private'),
    }))
